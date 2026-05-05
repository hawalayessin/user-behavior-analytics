import io
import json
import re
import os
import asyncio
import sys
import time
import uuid
import traceback
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal, get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.import_logs import ImportLog
from app.models.platform_users import PlatformUser

router = APIRouter(prefix="/admin/import", tags=["Admin Import"])

CSV_MAX_FILE_BYTES = 20 * 1024 * 1024
SQL_MAX_FILE_BYTES = 50 * 1024 * 1024

ImportMode = Literal["append", "replace"]


# ──────────────────────────────────────────────────────────────────────────────
# STEP 0 — TABLE_REGISTRY (derived from app/models/*)
# Notes:
# - "required" = columns with nullable=False AND no default/server_default
# - "optional" = nullable=True OR has default/server_default
# - "defaults_excluded" = columns with default/server_default (import should omit)
# ──────────────────────────────────────────────────────────────────────────────

TABLE_REGISTRY: dict[str, dict[str, Any]] = {
    "service_types": {
        "required": ["name", "billing_frequency_days", "price"],
        "optional": ["trial_duration_days", "is_active"],
        "defaults_excluded": ["id", "trial_duration_days", "is_active", "created_at"],
        "fk": {},
        "import_order": 1,
    },
    "services": {
        "required": ["name", "service_type_id"],
        "optional": ["description", "is_active"],
        "defaults_excluded": ["id", "is_active", "created_at"],
        "fk": {"service_type_id": "service_types.id"},
        "import_order": 2,
    },
    "users": {
        "required": ["phone_number"],
        "optional": ["status", "last_activity_at"],
        "defaults_excluded": ["id", "created_at", "status"],
        "fk": {},
        "import_order": 3,
    },
    "campaigns": {
        "required": ["name", "send_datetime", "target_size", "campaign_type", "status"],
        "optional": ["description", "service_id", "cost"],
        "defaults_excluded": ["id", "created_at"],
        "fk": {"service_id": "services.id"},
        "import_order": 4,
    },
    "subscriptions": {
        "required": ["user_id", "service_id", "subscription_start_date", "status"],
        "optional": ["campaign_id", "subscription_end_date"],
        "defaults_excluded": ["id", "created_at"],
        "fk": {
            "user_id": "users.id",
            "service_id": "services.id",
            "campaign_id": "campaigns.id",
        },
        "import_order": 5,
    },
    "billing_events": {
        "required": [
            "subscription_id",
            "user_id",
            "service_id",
            "event_datetime",
            "status",
            "is_first_charge",
        ],
        "optional": ["failure_reason", "retry_count"],
        "defaults_excluded": ["id", "retry_count", "created_at"],
        "fk": {
            "subscription_id": "subscriptions.id",
            "user_id": "users.id",
            "service_id": "services.id",
        },
        "import_order": 6,
    },
    "unsubscriptions": {
        "required": [
            "subscription_id",
            "user_id",
            "service_id",
            "unsubscription_datetime",
            "churn_type",
        ],
        "optional": ["churn_reason", "days_since_subscription", "last_billing_event_id"],
        "defaults_excluded": ["id"],
        "fk": {
            "subscription_id": "subscriptions.id",
            "user_id": "users.id",
            "service_id": "services.id",
            "last_billing_event_id": "billing_events.id",
        },
        "import_order": 7,
    },
    "sms_events": {
        "required": ["user_id", "event_datetime", "event_type", "direction"],
        "optional": [
            "campaign_id",
            "service_id",
            "message_content",
            "delivery_status",
        ],
        "defaults_excluded": ["id"],
        "fk": {
            "user_id": "users.id",
            "campaign_id": "campaigns.id",
            "service_id": "services.id",
        },
        "import_order": 8,
    },
    "user_activities": {
        "required": ["user_id", "service_id", "activity_datetime", "activity_type"],
        "optional": ["session_id"],
        "defaults_excluded": ["id"],
        "fk": {"user_id": "users.id", "service_id": "services.id"},
        "import_order": 9,
    },
}

EXCLUDED_TABLES = {
    "platform_users",  # auth-managed
    "cohorts",  # computed
    "staging_imports",  # internal ETL
    "import_logs",  # audit
}


def _read_upload_bytes(file: UploadFile, *, max_bytes: int) -> bytes:
    raw = file.file.read()
    if raw is None:
        return b""
    if len(raw) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large (max {int(max_bytes / (1024 * 1024))}MB).",
        )
    return raw


def _is_valid_uuid(value: Any) -> bool:
    if value is None:
        return False
    try:
        uuid.UUID(str(value))
        return True
    except Exception:
        return False


def _coerce_datetime(value: Any) -> datetime | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    dt = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(dt):
        return None
    return dt.to_pydatetime()


def _coerce_bool(value: Any) -> bool | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in {"true", "1", "yes", "y"}:
        return True
    if s in {"false", "0", "no", "n"}:
        return False
    return None


def _coerce_numeric(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    num = pd.to_numeric(value, errors="coerce")
    if pd.isna(num):
        return None
    return float(num)


def _ensure_staging_tables(db: Session) -> None:
    """
    Create staging tables if absent.
    We intentionally avoid DEFAULT gen_random_uuid() to not require pgcrypto.
    """
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS staging_imports (
              id            UUID PRIMARY KEY,
              import_id     UUID NOT NULL,
              row_number    INTEGER,
              raw_data      JSONB,
              status        VARCHAR(20),
              error_message TEXT,
              created_at    TIMESTAMP DEFAULT NOW()
            );
            """
        )
    )
    db.commit()


def _log_import(
    db: Session,
    *,
    admin: PlatformUser,
    file_name: str | None,
    file_type: str,
    target_table: str | None,
    scope: str | None,
    mode: str | None,
    status_value: str,
    rows_inserted: int = 0,
    rows_skipped: int = 0,
    error_details: dict | None = None,
) -> uuid.UUID:
    """
    Persist minimal audit info. The ImportLog model doesn't have all fields from the spec
    (scope/duration/cohorts flags), so we store extra fields in error_details JSON.
    """
    payload = dict(error_details or {})
    if scope is not None:
        payload.setdefault("scope", scope)
    log = ImportLog(
        admin_id=admin.id,
        file_name=file_name,
        file_type=file_type,
        target_table=target_table,
        mode=mode,
        rows_inserted=int(rows_inserted),
        rows_skipped=int(rows_skipped),
        status=status_value,
        error_details=payload or None,
    )
    db.add(log)
    db.commit()
    return log.id


def _fk_exists_map(db: Session, fk_table: str, fk_col: str, ids: list[str]) -> set[str]:
    if not ids:
        return set()
    stmt = text(f'SELECT "{fk_col}" AS id FROM "{fk_table}" WHERE "{fk_col}" IN :ids').bindparams(
        bindparam("ids", expanding=True)
    )
    rows = db.execute(stmt, {"ids": ids}).fetchall()
    return {str(r.id) for r in rows}


@dataclass
class ValidationResult:
    import_id: uuid.UUID
    total_rows: int
    valid_rows: int
    invalid_rows: int
    errors: list[dict]


def _validate_and_stage_csv(
    db: Session,
    *,
    table: str,
    file_name: str | None,
    mode: ImportMode,
    raw: bytes,
) -> ValidationResult:
    if table not in TABLE_REGISTRY or table in EXCLUDED_TABLES:
        raise HTTPException(status_code=400, detail=f"Invalid table '{table}'.")

    try:
        try:
            df = pd.read_csv(io.BytesIO(raw), encoding="utf-8")
        except Exception:
            df = pd.read_csv(io.BytesIO(raw), encoding="latin-1")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {e}")

    df = df.dropna(how="all")
    if df.empty:
        raise HTTPException(status_code=400, detail="Empty file")

    reg = TABLE_REGISTRY[table]
    required_cols: list[str] = list(reg["required"])

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing)}")

    errors: list[dict] = []
    invalid_rows: set[int] = set()

    # Normalize column names (strip)
    df.columns = [str(c).strip() for c in df.columns]

    # Coercions by heuristic
    datetime_cols = [c for c in df.columns if c.endswith("_datetime") or c.endswith("_date") or c.endswith("_at")]
    numeric_cols = [c for c in df.columns if c in {"price", "cost", "target_size", "retry_count", "days_since_subscription"}]
    bool_cols = [c for c in df.columns if c in {"is_active", "is_first_charge"}]

    for c in datetime_cols:
        if c in df.columns:
            df[c] = df[c].apply(_coerce_datetime)

    for c in numeric_cols:
        if c in df.columns:
            df[c] = df[c].apply(_coerce_numeric)

    for c in bool_cols:
        if c in df.columns:
            df[c] = df[c].apply(_coerce_bool)

    # Validate required non-null
    for idx, row in df.iterrows():
        for c in required_cols:
            v = row.get(c)
            if v is None or (isinstance(v, float) and pd.isna(v)) or (isinstance(v, str) and not v.strip()):
                invalid_rows.add(int(idx))
                errors.append({"row": int(idx) + 1, "field": c, "error": "missing"})

    # Per-table enum validations
    enum_rules: dict[str, dict[str, set[str]]] = {
        "users": {"status": {"active", "inactive"}},
        "subscriptions": {"status": {"trial", "active", "cancelled", "expired"}},
        "billing_events": {"status": {"SUCCESS", "FAILED"}},
        "unsubscriptions": {"churn_type": {"VOLUNTARY", "TECHNICAL"}},
        "sms_events": {"direction": {"inbound", "outbound"}},
    }
    if table in enum_rules:
        for field, allowed in enum_rules[table].items():
            if field in df.columns:
                for idx, v in df[field].items():
                    if v is None:
                        continue
                    sval = str(v).strip()
                    ok = sval in allowed
                    if not ok:
                        invalid_rows.add(int(idx))
                        errors.append(
                            {
                                "row": int(idx) + 1,
                                "field": field,
                                "error": f"invalid value '{sval}', expected: {'|'.join(sorted(allowed))}",
                            }
                        )
                    else:
                        df.at[idx, field] = sval

    # Validate UUID format for FK columns (if present)
    fk_map: dict[str, str] = dict(reg.get("fk", {}))
    for fk_col in fk_map.keys():
        if fk_col not in df.columns:
            continue
        for idx, v in df[fk_col].items():
            if v is None or (isinstance(v, float) and pd.isna(v)) or v == "":
                continue
            if not _is_valid_uuid(v):
                invalid_rows.add(int(idx))
                errors.append({"row": int(idx) + 1, "field": fk_col, "error": "invalid uuid"})

    # FK existence check
    for fk_col, target in fk_map.items():
        if fk_col not in df.columns:
            continue
        ids = [str(v) for v in df[fk_col].dropna().tolist() if str(v).strip()]
        if not ids:
            continue
        target_table, target_col = target.split(".", 1)
        existing = _fk_exists_map(db, target_table, target_col, ids)
        for idx, v in df[fk_col].items():
            if v is None or (isinstance(v, float) and pd.isna(v)) or v == "":
                continue
            if str(v) not in existing:
                invalid_rows.add(int(idx))
                errors.append({"row": int(idx) + 1, "field": fk_col, "error": f"FK not found in {target_table}"})

    # Internal duplicates (simple full-row duplicates)
    dup_mask = df.duplicated(keep="first")
    for idx, is_dup in dup_mask.items():
        if bool(is_dup):
            invalid_rows.add(int(idx))
            errors.append({"row": int(idx) + 1, "field": "__row__", "error": "duplicate row in file"})

    # STAGE (valid + invalid)
    _ensure_staging_tables(db)
    import_id = uuid.uuid4()
    records = []
    for idx, row in df.iterrows():
        row_num = int(idx) + 1
        raw_data = {k: (None if (isinstance(v, float) and pd.isna(v)) else v) for k, v in row.to_dict().items()}
        is_valid = int(idx) not in invalid_rows
        err_msgs = [e["error"] for e in errors if e["row"] == row_num]
        records.append(
            {
                "id": str(uuid.uuid4()),
                "import_id": str(import_id),
                "row_number": row_num,
                "raw_data": json.dumps(raw_data, default=str),
                "status": "valid" if is_valid else "invalid",
                "error_message": "; ".join(err_msgs)[:2000] if err_msgs else None,
            }
        )

    db.execute(
        text(
            """
            INSERT INTO staging_imports (id, import_id, row_number, raw_data, status, error_message)
            VALUES (
              CAST(:id AS uuid),
              CAST(:import_id AS uuid),
              :row_number,
              CAST(:raw_data AS jsonb),
              :status,
              :error_message
            )
            """
        ),
        records,
    )
    db.commit()

    total_rows = int(len(df))
    invalid_count = len(invalid_rows)
    valid_count = total_rows - invalid_count
    return ValidationResult(
        import_id=import_id,
        total_rows=total_rows,
        valid_rows=valid_count,
        invalid_rows=invalid_count,
        errors=errors[:200],
    )


def _load_from_staging(
    db: Session,
    *,
    table: str,
    mode: ImportMode,
    import_id: uuid.UUID,
    force: bool,
) -> tuple[int, int]:
    # If invalid and not forced → refuse
    counts = db.execute(
        text(
            """
            SELECT
              SUM(CASE WHEN status = 'valid' THEN 1 ELSE 0 END) AS valid_rows,
              SUM(CASE WHEN status = 'invalid' THEN 1 ELSE 0 END) AS invalid_rows
            FROM staging_imports
            WHERE import_id = CAST(:import_id AS uuid)
            """
        ),
        {"import_id": str(import_id)},
    ).fetchone()
    valid_rows = int(counts.valid_rows or 0)
    invalid_rows = int(counts.invalid_rows or 0)
    if valid_rows == 0:
        raise HTTPException(status_code=400, detail="No valid rows to load.")
    if not force and invalid_rows > 0:
        raise HTTPException(status_code=400, detail="Invalid rows present. Use force=true to load only valid rows.")

    # Build dynamic INSERT from JSONB keys (restrict to registry columns, exclude defaults)
    reg = TABLE_REGISTRY[table]
    allowed_cols = set(reg["required"]) | set(reg["optional"])
    excluded = set(reg.get("defaults_excluded") or [])
    insert_cols = [c for c in sorted(allowed_cols) if c not in excluded]
    if not insert_cols:
        raise HTTPException(status_code=400, detail="No importable columns for this table.")

    col_list_sql = ", ".join([f'"{c}"' for c in insert_cols])
    values_sql = ", ".join([f"(raw_data->>'{c}')" for c in insert_cols])

    # NOTE: we cast per-column for UUID/datetime/numeric when possible using heuristic
    def cast_expr(col: str) -> str:
        if col.endswith("_id") or col == "id":
            return f"NULLIF(raw_data->>'{col}', '')::uuid"
        if col.endswith("_datetime") or col.endswith("_date") or col.endswith("_at"):
            return f"NULLIF(raw_data->>'{col}', '')::timestamptz"
        if col in {"price", "cost"}:
            return f"NULLIF(raw_data->>'{col}', '')::numeric"
        if col in {"target_size", "retry_count", "days_since_subscription", "billing_frequency_days", "trial_duration_days"}:
            return f"NULLIF(raw_data->>'{col}', '')::integer"
        if col in {"is_active", "is_first_charge"}:
            return f"COALESCE(NULLIF(raw_data->>'{col}', '')::boolean, false)"
        return f"NULLIF(raw_data->>'{col}', '')"

    values_sql = ", ".join([cast_expr(c) for c in insert_cols])

    # Transaction
    rows_inserted = 0
    rows_skipped = invalid_rows if not force else invalid_rows
    try:
        db.execute(text("BEGIN"))
        if mode == "replace":
            db.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))

        res = db.execute(
            text(
                f"""
                INSERT INTO "{table}" ({col_list_sql})
                SELECT {values_sql}
                FROM staging_imports
                WHERE import_id = CAST(:import_id AS uuid)
                  AND status = 'valid'
                ON CONFLICT DO NOTHING
                """
            ),
            {"import_id": str(import_id)},
        )
        rows_inserted = int(res.rowcount or 0)

        db.execute(
            text(
                "DELETE FROM staging_imports WHERE import_id = CAST(:import_id AS uuid)"
            ),
            {"import_id": str(import_id)},
        )
        db.execute(text("COMMIT"))
    except Exception:
        db.execute(text("ROLLBACK"))
        raise

    return rows_inserted, rows_skipped


def _maybe_compute_cohorts(table: str) -> bool:
    if table not in {"subscriptions", "billing_events"}:
        return False
    try:
        from scripts.compute_cohorts import compute_cohorts

        compute_cohorts()
        return True
    except Exception:
        # Do not fail the import for cohort recompute issues; keep it visible in logs.
        return False


@router.post("/csv")
def stage_single_table_csv(
    table: str = Query(...),
    mode: ImportMode = Query("append"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_admin),
):
    t0 = time.perf_counter()
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are allowed.")

    raw = _read_upload_bytes(file, max_bytes=CSV_MAX_FILE_BYTES)
    result = _validate_and_stage_csv(db, table=table, file_name=file.filename, mode=mode, raw=raw)

    duration_ms = int((time.perf_counter() - t0) * 1000)
    _log_import(
        db,
        admin=current_user,
        file_name=file.filename,
        file_type="csv",
        target_table=table,
        scope="single_table",
        mode=mode,
        status_value="partial" if result.invalid_rows else "success",
        rows_inserted=0,
        rows_skipped=0,
        error_details={
            "import_id": str(result.import_id),
            "validation": {
                "total_rows": result.total_rows,
                "valid_rows": result.valid_rows,
                "invalid_rows": result.invalid_rows,
                "errors": result.errors,
            },
            "duration_ms": duration_ms,
        },
    )

    return {
        "import_id": str(result.import_id),
        "table": table,
        "total_rows": result.total_rows,
        "valid_rows": result.valid_rows,
        "invalid_rows": result.invalid_rows,
        "errors": result.errors,
        "ready_to_load": result.valid_rows > 0,
    }


@router.post("/csv/confirm")
def confirm_single_table_csv(
    import_id: str = Query(...),
    table: str = Query(...),
    mode: ImportMode = Query("append"),
    force: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_admin),
):
    t0 = time.perf_counter()
    if table not in TABLE_REGISTRY:
        raise HTTPException(status_code=400, detail="Invalid table.")

    try:
        import_uuid = uuid.UUID(import_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid import_id")

    try:
        rows_inserted, rows_skipped = _load_from_staging(
            db,
            table=table,
            mode=mode,
            import_id=import_uuid,
            force=force,
        )
        cohorts_recalculated = _maybe_compute_cohorts(table)
        duration_ms = int((time.perf_counter() - t0) * 1000)
        _log_import(
            db,
            admin=current_user,
            file_name=None,
            file_type="csv",
            target_table=table,
            scope="single_table_confirm",
            mode=mode,
            status_value="success",
            rows_inserted=rows_inserted,
            rows_skipped=rows_skipped,
            error_details={
                "import_id": import_id,
                "cohorts_recalculated": cohorts_recalculated,
                "duration_ms": duration_ms,
            },
        )
        return {
            "success": True,
            "table": table,
            "mode": mode,
            "rows_inserted": rows_inserted,
            "rows_skipped": rows_skipped,
            "cohorts_recalculated": cohorts_recalculated,
            "duration_ms": duration_ms,
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        _log_import(
            db,
            admin=current_user,
            file_name=None,
            file_type="csv",
            target_table=table,
            scope="single_table_confirm",
            mode=mode,
            status_value="failed",
            rows_inserted=0,
            rows_skipped=0,
            error_details={"import_id": import_id, "error": str(e)},
        )
        raise HTTPException(status_code=500, detail=f"Load failed: {e}")


_DANGEROUS_SQL = re.compile(r"\b(drop|delete|truncate|alter|create|update)\b", flags=re.IGNORECASE)
_TABLE_FROM_INSERT = re.compile(r"insert\s+into\s+([a-zA-Z_][a-zA-Z0-9_]*)", flags=re.IGNORECASE)


def _split_sql_statements(sql_text: str) -> list[str]:
    # Simple splitter (good enough for INSERT/COPY scripts without procedural blocks)
    parts = []
    buf = []
    in_single = False
    in_double = False
    for ch in sql_text:
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        if ch == ";" and not in_single and not in_double:
            stmt = "".join(buf).strip()
            if stmt:
                parts.append(stmt)
            buf = []
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


@router.post("/database")
def import_full_database_sql(
    mode: ImportMode = Query("append"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_admin),
):
    t0 = time.perf_counter()
    if not file.filename or not file.filename.lower().endswith(".sql"):
        raise HTTPException(status_code=400, detail="Only .sql files are allowed.")

    raw = _read_upload_bytes(file, max_bytes=SQL_MAX_FILE_BYTES)
    sql_text = raw.decode("utf-8", errors="replace")

    dangerous = sorted(set(m.group(1).upper() for m in _DANGEROUS_SQL.finditer(sql_text)))
    if dangerous:
        _log_import(
            db,
            admin=current_user,
            file_name=file.filename,
            file_type="sql",
            target_table=None,
            scope="full_database",
            mode=mode,
            status_value="failed",
            error_details={"dangerous_keywords": dangerous},
        )
        raise HTTPException(
            status_code=400,
            detail={"error": "Dangerous SQL detected", "dangerous_keywords": dangerous},
        )

    statements = _split_sql_statements(sql_text)
    if not statements:
        raise HTTPException(status_code=400, detail="Empty SQL file")

    # Allow only INSERT/COPY
    bad = []
    for i, stmt in enumerate(statements, start=1):
        s = stmt.strip().lower()
        if not (s.startswith("insert into") or s.startswith("copy")):
            bad.append({"statement": i, "error": "Only INSERT/COPY allowed"})
    if bad:
        raise HTTPException(status_code=400, detail={"error": "Invalid statements detected", "details": bad[:50]})

    # Group by target table
    by_table: dict[str, list[str]] = {t: [] for t in TABLE_REGISTRY.keys()}
    unknown_tables: set[str] = set()
    for stmt in statements:
        m = _TABLE_FROM_INSERT.search(stmt)
        if m:
            t = m.group(1)
            if t in by_table:
                by_table[t].append(stmt)
            else:
                unknown_tables.add(t)

    # Execution order by FK order (warning only if file order differs)
    ordered_tables = [t for t, _ in sorted(TABLE_REGISTRY.items(), key=lambda kv: kv[1]["import_order"])]

    tables_affected: dict[str, dict[str, int]] = {}
    inserted_subs_or_billing = False

    try:
        db.execute(text("BEGIN"))

        if mode == "replace":
            # Full replace: truncate in reverse order to reduce FK issues
            for t in reversed(ordered_tables):
                db.execute(text(f'TRUNCATE TABLE "{t}" RESTART IDENTITY CASCADE'))

        for t in ordered_tables:
            stmts = by_table.get(t) or []
            if not stmts:
                continue
            inserted = 0
            for stmt in stmts:
                res = db.execute(text(stmt))
                if res.rowcount and res.rowcount > 0:
                    inserted += int(res.rowcount)
            tables_affected[t] = {"inserted": inserted, "skipped": 0}
            if t in {"subscriptions", "billing_events"}:
                inserted_subs_or_billing = True

        db.execute(text("COMMIT"))
    except Exception as e:
        db.execute(text("ROLLBACK"))
        _log_import(
            db,
            admin=current_user,
            file_name=file.filename,
            file_type="sql",
            target_table=None,
            scope="full_database",
            mode=mode,
            status_value="failed",
            error_details={"error": str(e), "unknown_tables": sorted(unknown_tables)},
        )
        raise HTTPException(status_code=400, detail=f"SQL execution failed: {e}")

    cohorts_recalculated = _maybe_compute_cohorts("subscriptions") if inserted_subs_or_billing else False
    duration_ms = int((time.perf_counter() - t0) * 1000)

    _log_import(
        db,
        admin=current_user,
        file_name=file.filename,
        file_type="sql",
        target_table=None,
        scope="full_database",
        mode=mode,
        status_value="success",
        rows_inserted=sum(v["inserted"] for v in tables_affected.values()),
        rows_skipped=0,
        error_details={
            "tables_affected": tables_affected,
            "unknown_tables": sorted(unknown_tables),
            "cohorts_recalculated": cohorts_recalculated,
            "duration_ms": duration_ms,
        },
    )

    return {
        "success": True,
        "scope": "full_database",
        "tables_affected": tables_affected,
        "cohorts_recalculated": cohorts_recalculated,
        "duration_ms": duration_ms,
    }


@router.get("/history")
def import_history(
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_admin),
):
    logs = db.query(ImportLog).order_by(ImportLog.imported_at.desc()).limit(20).all()
    admin_map: dict[uuid.UUID, PlatformUser] = {}
    admin_ids = [l.admin_id for l in logs if l.admin_id]
    if admin_ids:
        admins = db.query(PlatformUser).filter(PlatformUser.id.in_(admin_ids)).all()
        admin_map = {a.id: a for a in admins}

    history = []
    for l in logs:
        admin = admin_map.get(l.admin_id) if l.admin_id else None
        details = l.error_details or {}
        history.append(
            {
                "id": str(l.id),
                "imported_at": l.imported_at.isoformat() if l.imported_at else None,
                "admin_name": getattr(admin, "full_name", None) or getattr(admin, "email", None) or "—",
                "file_name": l.file_name,
                "file_type": l.file_type,
                "target_table": l.target_table,
                "scope": details.get("scope"),
                "mode": l.mode,
                "rows_inserted": l.rows_inserted,
                "rows_skipped": l.rows_skipped,
                "status": l.status,
                "cohorts_recalculated": details.get("cohorts_recalculated"),
                "duration_ms": details.get("duration_ms"),
            }
        )

    return {"history": history}


@router.get("/schema/{table}")
def get_table_schema(
    table: str,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_admin),
):
    _ = db
    _ = current_user

    if table not in TABLE_REGISTRY or table in EXCLUDED_TABLES:
        raise HTTPException(status_code=404, detail="Unknown table")

    reg = TABLE_REGISTRY[table]
    required = list(reg.get("required", []))
    optional = list(reg.get("optional", []))
    defaults_excluded = list(reg.get("defaults_excluded", []))
    fk_map = dict(reg.get("fk", {}))

    columns = []
    for col in required:
        columns.append(
            {
                "name": col,
                "role": "required",
                "has_default": col in defaults_excluded,
                "fk": fk_map.get(col),
            }
        )
    for col in optional:
        columns.append(
            {
                "name": col,
                "role": "optional",
                "has_default": col in defaults_excluded,
                "fk": fk_map.get(col),
            }
        )

    return {
        "table": table,
        "import_order": int(reg.get("import_order", 0) or 0),
        "required": required,
        "optional": optional,
        "defaults_excluded": defaults_excluded,
        "fk": fk_map,
        "columns": columns,
        "template_headers": required + optional,
    }


@router.get("/template/{table}")
def download_template(
    table: str,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_admin),
):
    if table not in TABLE_REGISTRY:
        raise HTTPException(status_code=404, detail="Unknown table")
    reg = TABLE_REGISTRY[table]
    cols = list(reg["required"]) + list(reg["optional"])
    # CSV headers only (empty body)
    content = ",".join(cols) + "\n"
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{table}_template.csv"'},
    )


ETL_STEPS = [
    {"num": 1, "key": "etl_service_types", "label": "Types de services"},
    {"num": 2, "key": "etl_services", "label": "Services"},
    {"num": 3, "key": "etl_users", "label": "Utilisateurs"},
    {"num": 4, "key": "etl_subscriptions", "label": "Abonnements"},
    {"num": 5, "key": "etl_billing_events", "label": "Evenements de facturation"},
    {"num": 6, "key": "etl_unsubscriptions", "label": "Desabonnements"},
    {"num": 7, "key": "etl_user_activities", "label": "Activites utilisateurs"},
    {"num": 8, "key": "etl_sms_events", "label": "Evenements SMS"},
    {"num": 9, "key": "etl_cohorts", "label": "Cohortes de retention"},
]

_active_runs: dict[str, dict[str, Any]] = {}


@router.post(
    "/run-etl",
    summary="Lancer le pipeline ETL complet",
    dependencies=[Depends(require_admin)],
)
async def run_etl_pipeline(
    background_tasks: BackgroundTasks,
    mode: str = "demo",
    demo_users: int = 50000,
    truncate: bool = True,
    dry_run: bool = True,
    current_user: PlatformUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    active = [v for v in _active_runs.values() if v.get("status") == "running"]
    if active:
        raise HTTPException(
            status_code=409,
            detail="Un pipeline ETL est deja en cours d'execution.",
        )

    if mode not in {"demo", "prod"}:
        raise HTTPException(status_code=400, detail="Mode invalide. Utilisez 'demo' ou 'prod'.")
    # Safety: dry-run must never truncate target data.
    effective_truncate = truncate and (not dry_run)

    log_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc)

    _active_runs[log_id] = {
        "log_id": log_id,
        "status": "running",
        "mode": mode,
        "dry_run": dry_run,
        "demo_users": demo_users if mode == "demo" else None,
        "current_step": ETL_STEPS[0]["key"],
        "current_step_num": 1,
        "current_step_label": ETL_STEPS[0]["label"],
        "total_steps": len(ETL_STEPS),
        "progress_pct": 0,
        "rows_inserted": 0,
        "rows_skipped": 0,
        "duration_sec": 0.0,
        "started_at": started_at.isoformat(),
        "completed_at": None,
        "error": None,
        "steps_done": [],
        "triggered_by": str(current_user.id),
    }

    try:
        db.execute(
            text(
                """
                INSERT INTO import_logs (
                    id, file_name, file_type, target_table,
                    mode, status, current_step, current_step_num,
                    total_steps, progress_pct, rows_inserted,
                    rows_skipped, started_at, admin_id
                ) VALUES (
                    :id, :file_name, :file_type, :target_table,
                    :mode, :status, :current_step, :current_step_num,
                    :total_steps, :progress_pct, :rows_inserted,
                    :rows_skipped, :started_at, :admin_id
                )
                """
            ),
            {
                "id": log_id,
                "file_name": "etl_prod_to_analytics.py",
                "file_type": "etl_pipeline",
                "target_table": "all",
                "mode": mode,
                "status": "running",
                "current_step": ETL_STEPS[0]["key"],
                "current_step_num": 1,
                "total_steps": len(ETL_STEPS),
                "progress_pct": 0,
                "rows_inserted": 0,
                "rows_skipped": 0,
                "started_at": started_at,
                "admin_id": str(current_user.id),
            },
        )
        db.commit()
    except Exception:
        db.rollback()

    background_tasks.add_task(
        _execute_etl_background,
        log_id=log_id,
        mode=mode,
        demo_users=demo_users,
        truncate=effective_truncate,
        dry_run=dry_run,
    )

    return {
        "log_id": log_id,
        "status": "running",
        "message": f"Pipeline ETL demarre en mode {mode}",
        "mode": mode,
        "dry_run": dry_run,
        "truncate": effective_truncate,
        "demo_users": demo_users if mode == "demo" else None,
    }


async def _execute_etl_background(
    log_id: str,
    mode: str,
    demo_users: int,
    truncate: bool,
    dry_run: bool,
):
    start_time = datetime.now(timezone.utc)
    run = _active_runs[log_id]

    python_exe = sys.executable
    etl_script = str(
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "etl"
        / "etl_prod_to_analytics.py"
    )
    cmd = [python_exe, etl_script, "--batch-size", "50000"]

    if mode == "demo":
        cmd += ["--limit", str(demo_users)]
    if dry_run:
        cmd += ["--dry-run"]
    if truncate:
        cmd += ["--truncate-target"]

    log_dir = Path(__file__).resolve().parents[2] / "logs" / "etl_runs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{log_id}.log"
    run["log_path"] = str(log_path)

    try:
        prod_conn = settings.PROD_CONN or settings.prod_conn
        analytics_conn = settings.ANALYTICS_CONN or settings.analytics_conn or settings.DATABASE_URL
        env = {**os.environ, "PYTHONUNBUFFERED": "1"}
        if prod_conn:
            env["PROD_CONN"] = prod_conn
        if analytics_conn:
            env["ANALYTICS_CONN"] = analytics_conn
        with log_path.open("w", encoding="utf-8") as log_file:
            log_file.write(f"Command: {' '.join(cmd)}\n")
            log_file.write(f"Mode: {mode} | Dry run: {dry_run} | Truncate: {truncate}\n")
            log_file.write("--- ETL output ---\n")

            def _run_process():
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    env=env,
                    text=True,
                    bufsize=1,
                )

                rows_inserted = 0
                rows_skipped = 0
                completed_steps: list[str] = []
                output_tail: list[str] = []

                if process.stdout is None:
                    raise RuntimeError("Impossible de lire la sortie ETL.")

                for raw_line in process.stdout:
                    line = raw_line.strip()
                    if not line:
                        continue
                    log_file.write(line + "\n")
                    output_tail.append(line)
                    if len(output_tail) > 20:
                        output_tail = output_tail[-20:]

                    try:
                        log_data = json.loads(line)
                    except Exception:
                        continue

                    msg = str(log_data.get("message", ""))

                    for step in ETL_STEPS:
                        if (
                            "Step done" in msg
                            and step["key"].replace("etl_", "") in msg
                            and step["key"] not in completed_steps
                        ):
                            completed_steps.append(step["key"])
                            next_num = len(completed_steps) + 1
                            next_step = ETL_STEPS[next_num - 1] if next_num <= len(ETL_STEPS) else ETL_STEPS[-1]
                            pct = int(len(completed_steps) / len(ETL_STEPS) * 100)

                            rows_inserted += int(log_data.get("upserted", 0) or 0)
                            rows_skipped += int(log_data.get("skipped", 0) or 0)

                            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()

                            run.update(
                                {
                                    "current_step": next_step["key"],
                                    "current_step_num": min(next_num, len(ETL_STEPS)),
                                    "current_step_label": next_step["label"],
                                    "progress_pct": pct,
                                    "rows_inserted": rows_inserted,
                                    "rows_skipped": rows_skipped,
                                    "duration_sec": round(elapsed, 1),
                                    "steps_done": completed_steps.copy(),
                                }
                            )
                            break

                process.wait()
                return process.returncode, output_tail, rows_inserted, rows_skipped

            returncode, output_tail, rows_inserted, rows_skipped = await asyncio.to_thread(_run_process)
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()

            final_status = "success" if returncode == 0 else "failed"
            error_msg = None
            if final_status == "failed":
                error_msg = "\n".join(output_tail[-8:]) if output_tail else ""
                if not error_msg:
                    error_msg = f"ETL process exited with code {returncode}"
            log_file.write(f"--- ETL finished: {final_status} ---\n")
            run.update(
                {
                    "status": final_status,
                    "progress_pct": 100 if final_status == "success" else run["progress_pct"],
                    "duration_sec": round(elapsed, 1),
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "rows_inserted": rows_inserted,
                    "rows_skipped": rows_skipped,
                    "error": error_msg,
                }
            )

    except Exception as exc:
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        exc_type = type(exc).__name__
        exc_text = str(exc)
        run.update(
            {
                "status": "failed",
                "error": f"{exc_type}: {exc_text}" if exc_text else exc_type,
                "duration_sec": round(elapsed, 1),
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        try:
            log_path.write_text(
                "".join(
                    [
                        f"ETL runner exception: {exc_type}\n",
                        f"Message: {exc_text}\n",
                        "--- Traceback ---\n",
                        traceback.format_exc(),
                    ]
                ),
                encoding="utf-8",
            )
        except Exception:
            pass

    try:
        db2 = SessionLocal()
        db2.execute(
            text(
                """
                UPDATE import_logs SET
                    status           = :status,
                    progress_pct     = :pct,
                    rows_inserted    = :inserted,
                    rows_skipped     = :skipped,
                    duration_sec     = :duration,
                    completed_at     = :completed,
                    current_step     = :current_step,
                    current_step_num = :current_step_num,
                    error_details    = CAST(:error AS jsonb)
                WHERE id = CAST(:id AS uuid)
                """
            ),
            {
                "id": log_id,
                "status": run["status"],
                "pct": run["progress_pct"],
                "inserted": run["rows_inserted"],
                "skipped": run["rows_skipped"],
                "duration": run["duration_sec"],
                "completed": datetime.now(timezone.utc),
                "current_step": run.get("current_step"),
                "current_step_num": run.get("current_step_num"),
                "error": json.dumps({"message": run.get("error")}),
            },
        )
        db2.commit()
        db2.close()
    except Exception:
        pass


@router.get(
    "/run-etl/{log_id}/status",
    summary="Statut temps reel du pipeline ETL",
    dependencies=[Depends(require_admin)],
)
async def get_etl_status(
    log_id: str,
    current_user: PlatformUser = Depends(get_current_user),
):
    _ = current_user
    run = _active_runs.get(log_id)
    if not run:
        raise HTTPException(status_code=404, detail="Aucun pipeline trouve pour cet identifiant.")
    return run


@router.get(
    "/run-etl/{log_id}/log",
    summary="Lire le log ETL",
    dependencies=[Depends(require_admin)],
)
def get_etl_log(
    log_id: str,
    limit: int = 200,
):
    log_path = Path(__file__).resolve().parents[2] / "logs" / "etl_runs" / f"{log_id}.log"
    if not log_path.exists():
        raise HTTPException(status_code=404, detail="Aucun log ETL pour cet identifiant.")

    content = log_path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()
    if limit > 0:
        lines = lines[-limit:]
    return {
        "log_id": log_id,
        "line_count": len(lines),
        "log": "\n".join(lines),
    }


@router.get(
    "/etl-history",
    summary="Historique des pipelines ETL",
    dependencies=[Depends(require_admin)],
)
def get_etl_history(
    limit: int = 20,
    current_user: PlatformUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ = current_user
    rows = db.execute(
        text(
            """
            SELECT
                id,
                mode,
                status,
                rows_inserted,
                rows_skipped,
                duration_sec,
                progress_pct,
                error_details,
                started_at,
                completed_at,
                current_step
            FROM import_logs
            WHERE file_type = 'etl_pipeline'
            ORDER BY started_at DESC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    ).fetchall()

    response = []
    for r in rows:
        error_message = None
        if r.error_details:
            if isinstance(r.error_details, dict):
                error_message = r.error_details.get("message")
            else:
                try:
                    parsed = json.loads(r.error_details)
                    if isinstance(parsed, dict):
                        error_message = parsed.get("message")
                    else:
                        error_message = str(parsed)
                except Exception:
                    error_message = str(r.error_details)
        if not error_message:
            run = _active_runs.get(str(r.id))
            if run:
                error_message = run.get("error")
        if not error_message and r.status == "failed":
            error_message = "Unknown ETL error (no output captured). Check backend logs."
        response.append(
            {
                "id": str(r.id),
                "mode": r.mode,
                "status": r.status,
                "rows_inserted": r.rows_inserted or 0,
                "rows_skipped": r.rows_skipped or 0,
                "duration_sec": r.duration_sec or 0,
                "progress_pct": r.progress_pct or 0,
                "error": error_message,
                "error_raw": r.error_details,
                "started_at": (r.started_at.isoformat() if r.started_at else None),
                "completed_at": (r.completed_at.isoformat() if r.completed_at else None),
                "current_step": r.current_step,
            }
        )
    return response
