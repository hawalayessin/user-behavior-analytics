import io
import re
import time
import uuid
from datetime import datetime
from typing import Any, Literal

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.import_logs import ImportLog
from app.models.platform_users import PlatformUser


router = APIRouter(prefix="/admin/import", tags=["Admin Import"])

MAX_FILE_BYTES = 10 * 1024 * 1024  # 10MB

TargetTable = Literal["users", "subscriptions", "services"]
ImportMode = Literal["append", "replace"]


def _read_upload_bytes(file: UploadFile) -> bytes:
    raw = file.file.read()
    if raw is None:
        return b""
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large (max 10MB).",
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
    # convert to python datetime (timezone-aware)
    return dt.to_pydatetime()


def _validate_csv_df(df: pd.DataFrame, table: TargetTable) -> tuple[pd.DataFrame, list[dict]]:
    errors: list[dict] = []
    df = df.copy()

    if table == "users":
        required = ["phone_number"]
        allowed_status = {"active", "inactive", "churned", "cancelled", "trial"}

        for col in required:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Missing required column: {col}")

        if "id" not in df.columns:
            df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]
        if "status" not in df.columns:
            df["status"] = "active"
        if "created_at" not in df.columns:
            df["created_at"] = None

        valid_rows = []
        for i, row in df.iterrows():
            row_errors = []
            if not str(row.get("phone_number") or "").strip():
                row_errors.append({"row": int(i) + 1, "field": "phone_number", "error": "missing"})

            st = str(row.get("status") or "active").strip().lower()
            if st not in allowed_status:
                row_errors.append({"row": int(i) + 1, "field": "status", "error": f"valeur invalide: '{st}'"})

            rid = row.get("id")
            if not _is_valid_uuid(rid):
                df.at[i, "id"] = str(uuid.uuid4())

            created_at = _coerce_datetime(row.get("created_at"))
            if row.get("created_at") is not None and created_at is None:
                row_errors.append({"row": int(i) + 1, "field": "created_at", "error": "format date invalide"})
            df.at[i, "created_at"] = created_at
            df.at[i, "status"] = st

            if row_errors:
                errors.extend(row_errors)
            else:
                valid_rows.append(i)

        return df.loc[valid_rows], errors

    if table == "services":
        required = ["name", "billing_type", "price"]

        for col in required:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Missing required column: {col}")

        if "id" not in df.columns:
            df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]

        valid_rows = []
        for i, row in df.iterrows():
            row_errors = []
            if not str(row.get("name") or "").strip():
                row_errors.append({"row": int(i) + 1, "field": "name", "error": "missing"})
            if not str(row.get("billing_type") or "").strip():
                row_errors.append({"row": int(i) + 1, "field": "billing_type", "error": "missing"})
            try:
                float(row.get("price"))
            except Exception:
                row_errors.append({"row": int(i) + 1, "field": "price", "error": "invalid number"})

            rid = row.get("id")
            if not _is_valid_uuid(rid):
                df.at[i, "id"] = str(uuid.uuid4())

            if row_errors:
                errors.extend(row_errors)
            else:
                valid_rows.append(i)

        return df.loc[valid_rows], errors

    # subscriptions
    required = ["user_id", "service_id", "status", "subscription_start_date"]
    allowed_status = {"trial", "active", "cancelled", "expired"}
    for col in required:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Missing required column: {col}")

    if "id" not in df.columns:
        df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]
    if "subscription_end_date" not in df.columns:
        df["subscription_end_date"] = None

    valid_rows = []
    for i, row in df.iterrows():
        row_errors = []

        rid = row.get("id")
        if not _is_valid_uuid(rid):
            df.at[i, "id"] = str(uuid.uuid4())

        for fk in ["user_id", "service_id"]:
            if not _is_valid_uuid(row.get(fk)):
                row_errors.append({"row": int(i) + 1, "field": fk, "error": "invalid uuid"})

        st = str(row.get("status") or "").strip().lower()
        if st not in allowed_status:
            row_errors.append({"row": int(i) + 1, "field": "status", "error": f"valeur invalide: '{st}'"})
        df.at[i, "status"] = st

        start_dt = _coerce_datetime(row.get("subscription_start_date"))
        if start_dt is None:
            row_errors.append({"row": int(i) + 1, "field": "subscription_start_date", "error": "format date invalide"})
        df.at[i, "subscription_start_date"] = start_dt

        end_dt = _coerce_datetime(row.get("subscription_end_date"))
        if row.get("subscription_end_date") is not None and end_dt is None:
            row_errors.append({"row": int(i) + 1, "field": "subscription_end_date", "error": "format date invalide"})
        df.at[i, "subscription_end_date"] = end_dt

        if row_errors:
            errors.extend(row_errors)
        else:
            valid_rows.append(i)

    return df.loc[valid_rows], errors


def _log_import(
    db: Session,
    *,
    admin: PlatformUser,
    file_name: str | None,
    file_type: str,
    target_table: str | None,
    mode: str | None,
    rows_inserted: int,
    rows_skipped: int,
    status_value: str,
    error_details: dict | None,
) -> None:
    log = ImportLog(
        admin_id=admin.id,
        file_name=file_name,
        file_type=file_type,
        target_table=target_table,
        mode=mode,
        rows_inserted=rows_inserted,
        rows_skipped=rows_skipped,
        status=status_value,
        error_details=error_details,
    )
    db.add(log)
    db.commit()


@router.post("/csv")
def import_csv(
    table: TargetTable = Query(...),
    mode: ImportMode = Query("append"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_admin),
):
    t0 = time.perf_counter()

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are allowed.")

    raw = _read_upload_bytes(file)
    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {e}")

    validated_df, errors = _validate_csv_df(df, table)

    report = {
        "total_rows": int(len(df)),
        "valid_rows": int(len(validated_df)),
        "invalid_rows": int(len(df) - len(validated_df)),
        "errors": errors[:200],  # cap
    }

    if len(validated_df) == 0:
        _log_import(
            db,
            admin=current_user,
            file_name=file.filename,
            file_type="csv",
            target_table=table,
            mode=mode,
            rows_inserted=0,
            rows_skipped=int(len(df)),
            status_value="failed",
            error_details={"validation": report},
        )
        raise HTTPException(status_code=400, detail={"validation": report})

    try:
        if mode == "replace":
            db.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))

        rows_inserted = 0
        rows_skipped = int(len(df) - len(validated_df))

        if table == "users":
            records = validated_df[["id", "phone_number", "created_at", "status"]].to_dict(orient="records")
            res = db.execute(
                text("""
                    INSERT INTO users (id, phone_number, created_at, status)
                    VALUES (:id::uuid, :phone_number, COALESCE(:created_at, NOW()), :status)
                    ON CONFLICT (phone_number) DO NOTHING
                """),
                records,
            )
            rows_inserted = res.rowcount or 0

        elif table == "services":
            # Map to existing schema if possible: use id + name, ignore extra columns.
            # If your real DB has billing_type/price in service_types, import will still log the columns,
            # but only id+name will be inserted here.
            records = validated_df[["id", "name"]].to_dict(orient="records")
            res = db.execute(
                text("""
                    INSERT INTO services (id, name, service_type_id, is_active)
                    VALUES (:id::uuid, :name, (SELECT id FROM service_types LIMIT 1), true)
                    ON CONFLICT (id) DO NOTHING
                """),
                records,
            )
            rows_inserted = res.rowcount or 0

        else:  # subscriptions
            records = validated_df[
                ["id", "user_id", "service_id", "status", "subscription_start_date", "subscription_end_date"]
            ].to_dict(orient="records")
            res = db.execute(
                text("""
                    INSERT INTO subscriptions (
                        id, user_id, service_id, status,
                        subscription_start_date, subscription_end_date
                    )
                    VALUES (
                        :id::uuid, :user_id::uuid, :service_id::uuid, :status,
                        :subscription_start_date, :subscription_end_date
                    )
                    ON CONFLICT (id) DO NOTHING
                """),
                records,
            )
            rows_inserted = res.rowcount or 0

        db.commit()

        cohorts_recalculated = False
        if table == "subscriptions":
            from scripts.compute_cohorts import compute_cohorts  # local module

            compute_cohorts()
            cohorts_recalculated = True

        duration_ms = int((time.perf_counter() - t0) * 1000)
        status_value = "success" if len(errors) == 0 else "partial"
        _log_import(
            db,
            admin=current_user,
            file_name=file.filename,
            file_type="csv",
            target_table=table,
            mode=mode,
            rows_inserted=int(rows_inserted),
            rows_skipped=int(rows_skipped),
            status_value=status_value,
            error_details={"validation": report} if errors else None,
        )

        return {
            "success": True,
            "table": table,
            "mode": mode,
            "rows_inserted": int(rows_inserted),
            "rows_skipped": int(rows_skipped),
            "cohorts_recalculated": cohorts_recalculated,
            "duration_ms": duration_ms,
            "validation": report,
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        _log_import(
            db,
            admin=current_user,
            file_name=file.filename,
            file_type="csv",
            target_table=table,
            mode=mode,
            rows_inserted=0,
            rows_skipped=int(len(df)),
            status_value="failed",
            error_details={"error": str(e), "validation": report},
        )
        raise HTTPException(status_code=500, detail=f"Import failed: {e}")


_DANGEROUS_SQL = re.compile(
    r"\b(drop|delete|truncate|alter|update|create)\b",
    flags=re.IGNORECASE,
)
_ALLOWED_SQL = re.compile(
    r"^\s*(insert\s+into|copy)\s+",
    flags=re.IGNORECASE,
)


@router.post("/sql")
def import_sql(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_admin),
):
    if not file.filename or not file.filename.lower().endswith(".sql"):
        raise HTTPException(status_code=400, detail="Only .sql files are allowed.")

    raw = _read_upload_bytes(file)
    sql_text = raw.decode("utf-8", errors="replace")

    if _DANGEROUS_SQL.search(sql_text):
        _log_import(
            db,
            admin=current_user,
            file_name=file.filename,
            file_type="sql",
            target_table=None,
            mode=None,
            rows_inserted=0,
            rows_skipped=0,
            status_value="failed",
            error_details={"error": "dangerous_sql_detected"},
        )
        raise HTTPException(status_code=400, detail="Dangerous SQL detected (DROP/DELETE/TRUNCATE/ALTER/CREATE/UPDATE blocked).")

    statements = [s.strip() for s in sql_text.split(";") if s.strip()]
    for stmt in statements:
        if not _ALLOWED_SQL.match(stmt):
            raise HTTPException(status_code=400, detail="Only INSERT INTO and COPY statements are allowed.")

    executed = 0
    failed = 0
    inserted_into_subs = False

    try:
        db.execute(text("BEGIN"))
        for stmt in statements:
            try:
                if re.search(r"insert\s+into\s+subscriptions\b", stmt, flags=re.IGNORECASE) or re.search(
                    r"copy\s+subscriptions\b", stmt, flags=re.IGNORECASE
                ):
                    inserted_into_subs = True
                db.execute(text(stmt))
                executed += 1
            except Exception:
                failed += 1
                raise
        db.execute(text("COMMIT"))
    except Exception as e:
        db.execute(text("ROLLBACK"))
        _log_import(
            db,
            admin=current_user,
            file_name=file.filename,
            file_type="sql",
            target_table=None,
            mode=None,
            rows_inserted=0,
            rows_skipped=0,
            status_value="failed",
            error_details={"error": str(e)},
        )
        raise HTTPException(status_code=400, detail=f"SQL execution failed: {e}")

    cohorts_recalculated = False
    if inserted_into_subs:
        from scripts.compute_cohorts import compute_cohorts

        compute_cohorts()
        cohorts_recalculated = True

    _log_import(
        db,
        admin=current_user,
        file_name=file.filename,
        file_type="sql",
        target_table="subscriptions" if inserted_into_subs else None,
        mode=None,
        rows_inserted=0,
        rows_skipped=0,
        status_value="success" if failed == 0 else "partial",
        error_details=None,
    )

    return {
        "success": True,
        "statements_executed": executed,
        "statements_failed": failed,
        "cohorts_recalculated": cohorts_recalculated,
    }


@router.get("/history")
def import_history(
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_admin),
):
    logs = (
        db.query(ImportLog)
        .order_by(ImportLog.imported_at.desc())
        .limit(20)
        .all()
    )

    # Join admin name/email from platform_users (not users table)
    admin_map: dict[uuid.UUID, PlatformUser] = {}
    admin_ids = [l.admin_id for l in logs if l.admin_id]
    if admin_ids:
        admins = db.query(PlatformUser).filter(PlatformUser.id.in_(admin_ids)).all()
        admin_map = {a.id: a for a in admins}

    return {
        "history": [
            {
                "id": str(l.id),
                "imported_at": l.imported_at.isoformat() if l.imported_at else None,
                "admin_name": (admin_map.get(l.admin_id).full_name if l.admin_id and l.admin_id in admin_map else None)
                or (admin_map.get(l.admin_id).email if l.admin_id and l.admin_id in admin_map else "—"),
                "file_name": l.file_name,
                "table": l.target_table,
                "mode": l.mode,
                "rows_inserted": l.rows_inserted,
                "rows_skipped": l.rows_skipped,
                "status": l.status,
            }
            for l in logs
        ]
    }

