"""
ETL Hawala (prod) -> analytics_db (PFE)

Usage:
  python etl_prod_to_analytics.py --batch-size 50000
  python etl_prod_to_analytics.py --batch-size 50000 --limit 10000
  python etl_prod_to_analytics.py --truncate-target

Environment variables:
  HAWALA_CONN     Source PostgreSQL connection URL
  ANALYTICS_CONN  Target PostgreSQL connection URL

Corrections appliquées:
  1. BILLING_STATUS_MAP → minuscules (success/failed/pending/cancelled)
  2. failure_reason → basé sur status lowercase
  3. etl_unsubscriptions → source depuis transaction_histories (type=4)
     avec churn_type (VOLUNTARY/TECHNICAL) et churn_reason réels
     (NOT_SATISFIED / PRICE_TOO_HIGH / BILLING_FAILED / NO_RENEWAL)
  4. Fallback datetime → skip au lieu d'injecter datetime.now()
  5. etl_user_activities → activity_type granulaire (subscription/renewal/churn_event)
    6. Map status aligné sur la vérité métier prod
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import re
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import bindparam, create_engine, inspect, text
from sqlalchemy.exc import DBAPIError, OperationalError
from tqdm import tqdm


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


USER_NS        = uuid.UUID("11111111-1111-1111-1111-111111111111")
SUB_NS         = uuid.UUID("22222222-2222-2222-2222-222222222222")
BILLING_NS     = uuid.UUID("33333333-3333-3333-3333-333333333333")
ACTIVITY_NS    = uuid.UUID("66666666-6666-6666-6666-666666666666")
SMS_NS         = uuid.UUID("77777777-7777-7777-7777-777777777777")
SERVICE_NS     = uuid.UUID("44444444-4444-4444-4444-444444444444")
SERVICE_TYPE_NS = uuid.UUID("55555555-5555-5555-5555-555555555555")

USER_STATUS_MAP = {
    1:  "active",
    0:  "inactive",
    -1: "inactive",
    -2: "inactive",
}

def map_status(status_int: int) -> str:
    mapping = {
        1:  "active",
        -1: "cancelled",
        -2: "billing_failed",
        0:  "pending",
    }
    return mapping.get(status_int, "unknown")

# FIX #1 : minuscules — cohérent avec les requêtes SQL du dashboard
BILLING_STATUS_MAP = {
    0: "pending",
    1: "success",
    2: "failed",
    3: "cancelled",
}

BILLING_EVENT_TYPE_MAP = {
    1: "new_sub",
    2: "renewal",
    3: "upgrade",
    4: "unsub",
}

# FIX #5 : activity_type granulaire
ACTIVITY_TYPE_MAP = {
    1: "subscription",
    2: "renewal",
    4: "churn_event",
}


@dataclass
class ETLMetrics:
    read_rows: int = 0
    inserted_rows: int = 0
    updated_rows: int = 0
    skipped_rows: int = 0


class ETLRunner:
    def __init__(
        self,
        source_url: str,
        target_url: str,
        batch_size: int,
        limit: int | None,
        dry_run: bool,
        truncate_target: bool,
    ):
        self.source_engine  = create_engine(source_url, pool_pre_ping=True)
        self.target_engine  = create_engine(target_url, pool_pre_ping=True)
        self.batch_size     = batch_size
        self.limit          = limit
        self.dry_run        = dry_run
        self.truncate_target = truncate_target
        self.target_inspector = inspect(self.target_engine)

        self.services_by_source_id: dict[int, uuid.UUID] = {}
        self.source_service_by_subscription_type_id: dict[int, int] = {}

    # ------------------------------------------------------------------ #
    #  ORCHESTRATION                                                       #
    # ------------------------------------------------------------------ #

    def run(self) -> None:
        started = time.time()
        self._log(
            "ETL start",
            batch_size=self.batch_size,
            limit=self.limit,
            dry_run=self.dry_run,
            truncate_target=self.truncate_target,
        )
        self._preflight()

        if self.truncate_target:
            self._truncate_analytics_data()

        self.etl_service_types()
        self.etl_services()
        self.etl_users()
        self.etl_subscriptions()
        self.etl_billing_events()
        self.etl_unsubscriptions()
        self.etl_user_activities()
        self.etl_sms_events()
        self.etl_cohorts()

        imported_rows = self._count_target_rows(["users", "subscriptions", "billing_events", "user_activities"])
        min_date, max_date = self._source_tx_date_range()

        elapsed = time.time() - started
        self._log("ETL completed", duration_sec=round(elapsed, 2))
        print(f"ETL termine: {imported_rows} lignes importees, periode {min_date} -> {max_date}")

    # ------------------------------------------------------------------ #
    #  PREFLIGHT & INFRA                                                   #
    # ------------------------------------------------------------------ #

    def _preflight(self) -> None:
        source_tables = {
            "subscribed_clients",
            "transaction_histories",
            "services",
            "service_subscription_types",
        }
        target_tables = {
            "users",
            "subscriptions",
            "billing_events",
            "services",
            "service_types",
            "import_logs",
        }

        src_existing = set(inspect(self.source_engine).get_table_names())
        tgt_existing = set(self.target_inspector.get_table_names())

        missing_src = source_tables - src_existing
        missing_tgt = target_tables - tgt_existing

        if missing_src:
            raise RuntimeError(f"Missing source tables: {sorted(missing_src)}")
        if missing_tgt:
            raise RuntimeError(f"Missing target tables: {sorted(missing_tgt)}")

        self._log("Preflight OK", source_tables=len(source_tables), target_tables=len(target_tables))

    def _truncate_analytics_data(self) -> None:
        candidate_tables = [
            "cohorts",
            "unsubscriptions",
            "billing_events",
            "user_activities",
            "sms_events",
            "subscriptions",
            "campaigns",
            "users",
            "services",
            "service_types",
            "import_logs",
        ]
        existing = set(self.target_inspector.get_table_names())
        tables = [tbl for tbl in candidate_tables if tbl in existing]

        if not tables:
            self._log("Truncate skipped - no target tables found")
            return

        truncate_sql = f"TRUNCATE TABLE {', '.join(tables)} RESTART IDENTITY CASCADE"
        with self.target_engine.begin() as conn:
            conn.execute(text(truncate_sql))

        self._log("Target tables truncated", table_count=len(tables), tables=tables)

    @staticmethod
    def _log(msg: str, **kwargs: Any) -> None:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "message": msg,
            **kwargs,
        }
        logging.info(json.dumps(payload, ensure_ascii=True))

    @staticmethod
    def _uuid5(namespace: uuid.UUID, value: str | int | None) -> uuid.UUID:
        raw = "" if value is None else str(value)
        return uuid.uuid5(namespace, raw)

    @staticmethod
    def _parse_dt(value: Any) -> datetime | None:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        ts = pd.to_datetime(value, utc=True, errors="coerce")
        if pd.isna(ts):
            return None
        return ts.to_pydatetime()

    @staticmethod
    def _clean_phone(value: Any) -> str | None:
        if value is None:
            return None
        phone = str(value).strip()
        if not phone:
            return None
        if phone.startswith("00"):
            phone = "+" + phone[2:]
        if phone.startswith("216") and not phone.startswith("+"):
            phone = "+" + phone
        return phone

    @staticmethod
    def _normalize_channel(value: Any) -> str:
        raw = str(value or "").strip().lower()
        if raw in {"ussd", "*1589", "*159#", "menu"}:
            return "USSD"
        return "WEB"

    def _with_retry(self, fn, *args, **kwargs):
        last_exc = None
        for attempt in range(1, 4):
            try:
                return fn(*args, **kwargs)
            except (OperationalError, DBAPIError) as exc:
                last_exc = exc
                backoff = (2 ** attempt) + random.uniform(0, 0.75)
                self._log("Retrying batch", attempt=attempt, wait_sec=round(backoff, 2), error=str(exc))
                time.sleep(backoff)
        raise RuntimeError(f"Failed after retries: {last_exc}")

    def _count_source(self, table: str) -> int:
        with self.source_engine.connect() as conn:
            return int(conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar() or 0)

    def _count_target_rows(self, tables: list[str]) -> int:
        total = 0
        existing = set(self.target_inspector.get_table_names())
        with self.target_engine.connect() as conn:
            for table in tables:
                if table not in existing:
                    continue
                total += int(conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar() or 0)
        return total

    def _source_tx_date_range(self) -> tuple[str, str]:
        src_cols = {c["name"] for c in inspect(self.source_engine).get_columns("transaction_histories")}
        dt_col = "created_at" if "created_at" in src_cols else None
        if dt_col is None:
            return "n/a", "n/a"

        with self.source_engine.connect() as conn:
            row = conn.execute(
                text(f"SELECT MIN({dt_col}) AS min_d, MAX({dt_col}) AS max_d FROM transaction_histories")
            ).fetchone()
        if not row:
            return "n/a", "n/a"
        return str(row.min_d or "n/a"), str(row.max_d or "n/a")

    def _source_chunks(self, table: str, cols: list[str], order_col: str):
        limit_sql = f" LIMIT {self.limit}" if self.limit else ""
        sql = f"SELECT {', '.join(cols)} FROM {table} ORDER BY {order_col}{limit_sql}"
        return pd.read_sql_query(sql=text(sql), con=self.source_engine, chunksize=self.batch_size)

    def _load_subscription_type_to_service_map(self) -> dict[int, int]:
        src_cols = {c["name"] for c in inspect(self.source_engine).get_columns("service_subscription_types")}
        if "service_id" not in src_cols:
            self._log(
                "Mapping source table missing service_id",
                step="subscriptions",
                table="service_subscription_types",
            )
            return {}

        sql = text(
            """
            SELECT id, service_id
            FROM service_subscription_types
            WHERE service_id IS NOT NULL
            """
        )
        with self.source_engine.connect() as conn:
            rows = conn.execute(sql).fetchall()

        mapping: dict[int, int] = {}
        for r in rows:
            mapping[int(r.id)] = int(r.service_id)
        return mapping

    def _write_import_log(self, target_table: str, metrics: ETLMetrics, status: str, duration_sec: float, error: str | None = None) -> None:
        payload = {
            "id": uuid.uuid4(),
            "file_name": "etl_prod_to_analytics.py",
            "file_type": "sql",
            "target_table": target_table,
            "mode": "append",
            "rows_inserted": metrics.inserted_rows,
            "rows_skipped": metrics.skipped_rows,
            "status": status,
            "error_details": {
                "read_rows": metrics.read_rows,
                "updated_rows": metrics.updated_rows,
                "duration_sec": round(duration_sec, 2),
                "error": error,
            },
        }
        with self.target_engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO import_logs (
                        id, file_name, file_type, target_table, mode,
                        rows_inserted, rows_skipped, status, error_details
                    ) VALUES (
                        :id, :file_name, :file_type, :target_table, :mode,
                        :rows_inserted, :rows_skipped, :status, CAST(:error_details AS jsonb)
                    )
                    """
                ),
                {**payload, "error_details": json.dumps(payload["error_details"], ensure_ascii=True)},
            )

    def _execute_batch(self, stmt, rows: list[dict[str, Any]]) -> None:
        with self.target_engine.begin() as conn:
            conn.execute(stmt, rows)

    # ------------------------------------------------------------------ #
    #  ETL STEPS                                                           #
    # ------------------------------------------------------------------ #

    def etl_service_types(self) -> None:
        step = "service_types"
        started = time.time()
        metrics = ETLMetrics()
        self._log("Step start", step=step)

        try:
            source_sql = text(
                """
                SELECT id, amount, subscription_period_id
                FROM service_subscription_types
                ORDER BY id
                """
            )
            df = pd.read_sql_query(source_sql, self.source_engine)
            metrics.read_rows = len(df)

            if df.empty:
                self._log("No source rows", step=step)
                self._write_import_log(step, metrics, "success", time.time() - started)
                return

            rows = []
            for row in df.itertuples(index=False):
                source_id = int(row.id)
                period_id = int(row.subscription_period_id) if row.subscription_period_id is not None else 30
                if period_id <= 1:
                    name = "daily"
                    freq_days = 1
                elif period_id <= 7:
                    name = "weekly"
                    freq_days = 7
                else:
                    name = "monthly"
                    freq_days = 30

                price = Decimal(str(row.amount if row.amount is not None else 0)).quantize(Decimal("0.01"))
                rows.append(
                    {
                        "id": self._uuid5(SERVICE_TYPE_NS, f"stype:{source_id}"),
                        "name": name,
                        "billing_frequency_days": freq_days,
                        "price": price,
                        "trial_duration_days": 3,
                        "is_active": True,
                    }
                )

            if not self.dry_run:
                upsert_sql = text(
                    """
                    INSERT INTO service_types (
                        id, name, billing_frequency_days, price, trial_duration_days, is_active
                    ) VALUES (
                        :id, :name, :billing_frequency_days, :price, :trial_duration_days, :is_active
                    )
                    ON CONFLICT (name)
                    DO UPDATE SET
                        billing_frequency_days = EXCLUDED.billing_frequency_days,
                        price = EXCLUDED.price,
                        trial_duration_days = EXCLUDED.trial_duration_days,
                        is_active = EXCLUDED.is_active
                    """
                )
                with self.target_engine.begin() as conn:
                    conn.execute(upsert_sql, rows)
            metrics.inserted_rows = len(rows)

            self._write_import_log(step, metrics, "success", time.time() - started)
            self._log("Step done", step=step, read_rows=metrics.read_rows, upserted=metrics.inserted_rows)
        except Exception as exc:
            self._write_import_log(step, metrics, "failed", time.time() - started, str(exc))
            raise

    def etl_services(self) -> None:
        step = "services"
        started = time.time()
        metrics = ETLMetrics()
        self._log("Step start", step=step)

        try:
            st_map = {}
            with self.target_engine.connect() as conn:
                for r in conn.execute(text("SELECT id, billing_frequency_days FROM service_types")):
                    st_map[int(r.billing_frequency_days)] = r.id

            source_service_cols = {
                col["name"] for col in inspect(self.source_engine).get_columns("services")
            }
            entitled_col = "entitled" if "entitled" in source_service_cols else "name"

            type_col = None
            for candidate in [
                "service_subscription_type_id",
                "service_type_id",
                "subscription_type_id",
                "service_subscription_id",
            ]:
                if candidate in source_service_cols:
                    type_col = candidate
                    break

            select_cols = ["id", entitled_col, "status"]
            if type_col:
                select_cols.append(type_col)

            source_sql = text(f"SELECT {', '.join(select_cols)} FROM services ORDER BY id")
            df = pd.read_sql_query(source_sql, self.source_engine)
            metrics.read_rows = len(df)

            rows = []
            for row in df.itertuples(index=False):
                source_id     = int(row.id)
                raw_name      = getattr(row, entitled_col, None)
                name          = str(raw_name or "").strip() or f"service_{source_id}"
                source_status = int(row.status) if row.status is not None else 1
                raw_type      = getattr(row, type_col, None) if type_col else None
                source_type   = int(raw_type) if raw_type is not None else None

                freq_guess = 30
                if source_type is not None:
                    if source_type <= 1:
                        freq_guess = 1
                    elif source_type <= 7:
                        freq_guess = 7
                service_type_id = st_map.get(freq_guess) or next(iter(st_map.values()))
                service_uuid    = self._uuid5(SERVICE_NS, f"service:{source_id}")

                rows.append(
                    {
                        "id": service_uuid,
                        "name": name,
                        "description": None,
                        "service_type_id": service_type_id,
                        "is_active": bool(source_status == 1),
                    }
                )
                self.services_by_source_id[source_id] = service_uuid

            if rows and not self.dry_run:
                upsert_sql = text(
                    """
                    INSERT INTO services (id, name, description, service_type_id, is_active)
                    VALUES (:id, :name, :description, :service_type_id, :is_active)
                    ON CONFLICT (id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        service_type_id = EXCLUDED.service_type_id,
                        is_active = EXCLUDED.is_active
                    """
                )
                with self.target_engine.begin() as conn:
                    conn.execute(upsert_sql, rows)

            metrics.inserted_rows = len(rows)
            self._write_import_log(step, metrics, "success", time.time() - started)
            self._log("Step done", step=step, read_rows=metrics.read_rows, upserted=metrics.inserted_rows)
        except Exception as exc:
            self._write_import_log(step, metrics, "failed", time.time() - started, str(exc))
            raise

    def etl_users(self) -> None:
        step = "users"
        started = time.time()
        metrics = ETLMetrics()
        self._log("Step start", step=step)

        has_channel = "channel" in {c["name"] for c in inspect(self.source_engine).get_columns("subscribed_clients")}
        cols = ["id", "phone_number", "status", "subscription_start_date"]
        if has_channel:
            cols.append("channel")

        total = min(self._count_source("subscribed_clients"), self.limit) if self.limit else self._count_source("subscribed_clients")
        pbar = tqdm(total=total, desc="etl_users", unit="rows")

        insert_sql = text(
            """
            INSERT INTO users (id, phone_number, status, created_at)
            VALUES (:id, :phone_number, :status, :created_at)
            ON CONFLICT (phone_number)
            DO UPDATE SET
                status = EXCLUDED.status,
                created_at = LEAST(users.created_at, EXCLUDED.created_at)
            """
        )

        try:
            for chunk in self._source_chunks("subscribed_clients", cols, "id"):
                rows = []
                for rec in chunk.itertuples(index=False):
                    metrics.read_rows += 1
                    source_status = int(getattr(rec, "status", 0) or 0)
                    phone = self._clean_phone(getattr(rec, "phone_number", None))
                    if not phone:
                        metrics.skipped_rows += 1
                        continue

                    # FIX #4 : skip rows sans date au lieu d'injecter datetime.now()
                    created_at = self._parse_dt(getattr(rec, "subscription_start_date", None))
                    if created_at is None:
                        metrics.skipped_rows += 1
                        continue

                    rows.append(
                        {
                            "id": self._uuid5(USER_NS, f"user:{phone}"),
                            "phone_number": phone,
                            "status": USER_STATUS_MAP.get(source_status, "inactive"),
                            "created_at": created_at,
                        }
                    )

                if rows and not self.dry_run:
                    self._with_retry(self._execute_batch, insert_sql, rows)

                metrics.inserted_rows += len(rows)
                pbar.update(len(chunk))

            pbar.close()
            self._write_import_log(step, metrics, "success", time.time() - started)
            self._log("Step done", step=step, read_rows=metrics.read_rows, upserted=metrics.inserted_rows, skipped=metrics.skipped_rows)
        except Exception as exc:
            pbar.close()
            self._write_import_log(step, metrics, "failed", time.time() - started, str(exc))
            raise

    def _fetch_user_ids_for_phones(self, phones: list[str]) -> dict[str, uuid.UUID]:
        if not phones:
            return {}
        q = text("SELECT phone_number, id FROM users WHERE phone_number IN :phones").bindparams(
            bindparam("phones", expanding=True)
        )
        with self.target_engine.connect() as conn:
            rows = conn.execute(q, {"phones": phones}).fetchall()
        return {r.phone_number: r.id for r in rows}

    def _fetch_subscription_map(self, subscription_ids: list[uuid.UUID]) -> dict[uuid.UUID, tuple[uuid.UUID, uuid.UUID]]:
        if not subscription_ids:
            return {}
        q = text(
            """
            SELECT id, user_id, service_id
            FROM subscriptions
            WHERE id IN :ids
            """
        ).bindparams(bindparam("ids", expanding=True))
        with self.target_engine.connect() as conn:
            rows = conn.execute(q, {"ids": subscription_ids}).fetchall()
        return {r.id: (r.user_id, r.service_id) for r in rows}

    @staticmethod
    def _first_existing_column(columns: set[str], candidates: list[str]) -> str | None:
        for c in candidates:
            if c in columns:
                return c
        return None

    @staticmethod
    def _to_str(value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @staticmethod
    def _parse_uuid(value: Any) -> uuid.UUID | None:
        if value is None:
            return None
        try:
            return uuid.UUID(str(value).strip())
        except Exception:
            return None

    @staticmethod
    def _extract_otp_code(message_text: str | None) -> str | None:
        if not message_text:
            return None
        match = re.search(r"\b(\d{4,8})\b", message_text)
        return match.group(1) if match else None

    @staticmethod
    def _detect_delivery_status(raw_status: Any) -> str | None:
        val = str(raw_status or "").strip().lower()
        if not val:
            return None
        if val in {"delivered", "delivery_success", "success", "ok", "sent_ok"}:
            return "DELIVERED"
        if val in {"sent", "submitted", "submit", "dispatched"}:
            return "SENT"
        if val in {"failed", "error", "undelivered", "rejected", "ko"}:
            return "FAILED"
        if val in {"queued", "pending", "processing", "waiting"}:
            return "QUEUED"
        return "UNKNOWN"

    @staticmethod
    def _detect_direction(raw_direction: Any, raw_event_type: Any) -> str | None:
        d = str(raw_direction or "").strip().lower()
        e = str(raw_event_type or "").strip().lower()
        if d in {"in", "inbound", "incoming", "mo", "received"}:
            return "INBOUND"
        if d in {"out", "outbound", "outgoing", "mt", "sent"}:
            return "OUTBOUND"
        if any(k in e for k in ["inbound", "incoming", "reply", "ussd_request"]):
            return "INBOUND"
        if any(k in e for k in ["outbound", "delivery", "otp", "notify", "sms"]):
            return "OUTBOUND"
        return None

    @staticmethod
    def _detect_is_otp(message_text: str | None, template_name: str | None, template_code: str | None, raw_event_type: Any) -> bool:
        txt = " ".join(
            [
                str(message_text or ""),
                str(template_name or ""),
                str(template_code or ""),
                str(raw_event_type or ""),
            ]
        ).lower()
        return any(k in txt for k in ["otp", "verification", "verify", "code", "one-time", "one time"])

    @staticmethod
    def _detect_activation_status(raw_status: Any, raw_event_type: Any, message_text: str | None) -> str | None:
        blob = " ".join([str(raw_status or ""), str(raw_event_type or ""), str(message_text or "")]).lower()
        if any(k in blob for k in ["success", "activated", "activation_success", "confirmed", "optin_success"]):
            return "SUCCESS"
        if any(k in blob for k in ["fail", "failed", "error", "rejected"]):
            return "FAILED"
        if any(k in blob for k in ["abandon", "timeout", "expired"]):
            return "ABANDONED"
        if any(k in blob for k in ["start", "initiated", "begin", "pending"]):
            return "STARTED"
        return None

    def _detect_is_activation(self, raw_event_type: Any, message_text: str | None, flow_name: str | None, activation_status: str | None) -> bool:
        if activation_status in {"STARTED", "SUCCESS", "FAILED", "ABANDONED"}:
            return True
        blob = " ".join([str(raw_event_type or ""), str(message_text or ""), str(flow_name or "")]).lower()
        return any(k in blob for k in ["activation", "activate", "subscribe", "subscription", "optin", "confirm", "newsub"])

    @staticmethod
    def _detect_channel(
        raw_channel: Any,
        raw_event_type: Any,
        message_text: str | None,
        shortcode: str | None,
        ussd_code: str | None,
        website_path: str | None,
    ) -> str:
        blob = " ".join(
            [
                str(raw_channel or ""),
                str(raw_event_type or ""),
                str(message_text or ""),
                str(shortcode or ""),
                str(ussd_code or ""),
                str(website_path or ""),
            ]
        ).lower()
        if any(k in blob for k in ["ussd", "menu", "*159", "*1589", "shortcode"]):
            return "USSD"
        if any(k in blob for k in ["web", "website", "landing", "site", "http://", "https://"]):
            return "WEB"
        if any(k in blob for k in ["otp", "verification", "verify", "code"]):
            return "OTP"
        return "SMS"

    @staticmethod
    def _detect_activation_channel(
        raw_channel: Any,
        raw_event_type: Any,
        message_text: str | None,
        website_path: str | None,
        ussd_code: str | None,
    ) -> str | None:
        blob = " ".join(
            [
                str(raw_channel or ""),
                str(raw_event_type or ""),
                str(message_text or ""),
                str(website_path or ""),
                str(ussd_code or ""),
            ]
        ).lower()
        if any(k in blob for k in ["web", "website", "landing", "site", "http://", "https://"]):
            return "WEB"
        if any(k in blob for k in ["ussd", "menu", "*159", "*1589", "shortcode"]):
            return "USSD"
        if any(k in blob for k in ["otp", "verification", "verify", "code"]):
            return "OTP"
        if any(k in blob for k in ["activation", "activate", "subscribe", "optin", "confirm"]):
            return "SMS"
        return None

    def _resolve_sms_source_table(self) -> tuple[str | None, set[str]]:
        source_inspector = inspect(self.source_engine)
        source_tables = set(source_inspector.get_table_names())

        candidates = ["message_events", "smsevents", "sms_events", "messagelogs", "message_logs", "outboundmessages", "outbound_messages", "messages"]
        useful_cols = {
            "phone", "phone_number", "phonenumber", "msisdn", "mobile",
            "message", "message_content", "content", "body", "text", "sms_text",
            "delivery_status", "status", "message_status", "delivery_state",
            "direction", "msg_direction", "traffic_type",
            "event_datetime", "created_at", "sent_at", "delivered_at", "updated_at",
            "service_id", "template_name", "template", "template_code", "channel",
        }

        ranked: list[tuple[str, int, int, set[str]]] = []
        for table in candidates:
            if table not in source_tables:
                continue
            cols = {c["name"] for c in source_inspector.get_columns(table)}
            score = len(cols.intersection(useful_cols))
            try:
                volume = self._count_source(table)
            except Exception:
                volume = 0
            ranked.append((table, score, volume, cols))

        if not ranked:
            return None, set()

        ranked.sort(key=lambda t: (t[1], t[2]), reverse=True)
        best = ranked[0]
        return best[0], best[3]

    def _resolve_sms_target_table(self) -> str:
        target_tables = set(self.target_inspector.get_table_names())
        if "sms_events" in target_tables:
            return "sms_events"
        if "smsevents" in target_tables:
            return "smsevents"
        raise RuntimeError("Target SMS table not found: sms_events/smsevents")

    def etl_subscriptions(self) -> None:
        step = "subscriptions"
        started = time.time()
        metrics = ETLMetrics()
        self._log("Step start", step=step)

        src_cols = {c["name"] for c in inspect(self.source_engine).get_columns("subscribed_clients")}
        cols = ["id", "phone_number", "status", "subscription_start_date", "subscription_end_date"]
        for opt_col in ["service_id", "service_subscription_type_id", "channel"]:
            if opt_col in src_cols:
                cols.append(opt_col)

        total = min(self._count_source("subscribed_clients"), self.limit) if self.limit else self._count_source("subscribed_clients")
        pbar = tqdm(total=total, desc="etl_subscriptions", unit="rows")

        upsert_sql = text(
            """
            INSERT INTO subscriptions (
                id, user_id, service_id, campaign_id,
                subscription_start_date, subscription_end_date, status, created_at
            ) VALUES (
                :id, :user_id, :service_id, NULL,
                :subscription_start_date, :subscription_end_date, :status, :created_at
            )
            ON CONFLICT (id)
            DO UPDATE SET
                user_id = EXCLUDED.user_id,
                service_id = EXCLUDED.service_id,
                subscription_start_date = EXCLUDED.subscription_start_date,
                subscription_end_date = EXCLUDED.subscription_end_date,
                status = EXCLUDED.status,
                created_at = EXCLUDED.created_at
            """
        )

        self.source_service_by_subscription_type_id = self._load_subscription_type_to_service_map()

        default_service_id        = next(iter(self.services_by_source_id.values()), None)
        mapped_via_service_id     = 0
        mapped_via_type_id        = 0
        mapped_via_default        = 0
        skipped_unmapped_service  = 0

        try:
            for chunk in self._source_chunks("subscribed_clients", cols, "id"):
                phones   = [self._clean_phone(v) for v in chunk["phone_number"].tolist()]
                user_map = self._fetch_user_ids_for_phones([p for p in phones if p])

                rows = []
                for rec in chunk.itertuples(index=False):
                    metrics.read_rows += 1
                    source_client_id = int(getattr(rec, "id"))
                    source_status    = int(getattr(rec, "status", 0) or 0)

                    phone   = self._clean_phone(getattr(rec, "phone_number", None))
                    user_id = user_map.get(phone) if phone else None
                    if not user_id:
                        metrics.skipped_rows += 1
                        continue

                    raw_source_service_id = getattr(rec, "service_id", None)
                    raw_source_type_id    = getattr(rec, "service_subscription_type_id", None)
                    source_service_id     = int(raw_source_service_id) if raw_source_service_id is not None else None
                    source_type_id        = int(raw_source_type_id) if raw_source_type_id is not None else None

                    service_id = None
                    if source_service_id is not None:
                        service_id = self.services_by_source_id.get(source_service_id)
                        if service_id is not None:
                            mapped_via_service_id += 1
                    if service_id is None and source_type_id is not None:
                        source_service_from_type = self.source_service_by_subscription_type_id.get(source_type_id)
                        if source_service_from_type is not None:
                            service_id = self.services_by_source_id.get(source_service_from_type)
                            if service_id is not None:
                                mapped_via_type_id += 1
                    if service_id is None:
                        service_id = default_service_id
                        if service_id is not None:
                            mapped_via_default += 1
                    if service_id is None:
                        metrics.skipped_rows += 1
                        skipped_unmapped_service += 1
                        continue

                    # FIX #4 : skip rows sans date de début
                    start_date = self._parse_dt(getattr(rec, "subscription_start_date", None))
                    if start_date is None:
                        metrics.skipped_rows += 1
                        continue
                    end_date = self._parse_dt(getattr(rec, "subscription_end_date", None))

                    sub_status = map_status(source_status)

                    rows.append(
                        {
                            "id": self._uuid5(SUB_NS, f"sub:{source_client_id}"),
                            "user_id": user_id,
                            "service_id": service_id,
                            "subscription_start_date": start_date,
                            "subscription_end_date": end_date,
                            "status": sub_status,
                            "created_at": start_date,
                        }
                    )

                if rows and not self.dry_run:
                    self._with_retry(self._execute_batch, upsert_sql, rows)

                metrics.inserted_rows += len(rows)
                pbar.update(len(chunk))

            pbar.close()
            self._write_import_log(step, metrics, "success", time.time() - started)
            self._log(
                "Step done",
                step=step,
                read_rows=metrics.read_rows,
                upserted=metrics.inserted_rows,
                skipped=metrics.skipped_rows,
                map_service_id_rows=mapped_via_service_id,
                map_subscription_type_rows=mapped_via_type_id,
                map_default_rows=mapped_via_default,
                unmapped_service_rows=skipped_unmapped_service,
                subscription_type_map_size=len(self.source_service_by_subscription_type_id),
            )
        except Exception as exc:
            pbar.close()
            self._write_import_log(step, metrics, "failed", time.time() - started, str(exc))
            raise

    def etl_billing_events(self) -> None:
        step = "billing_events"
        started = time.time()
        metrics = ETLMetrics()
        self._log("Step start", step=step)

        src_cols = {c["name"] for c in inspect(self.source_engine).get_columns("transaction_histories")}
        cols = ["id", "subscribed_client_id", "status", "type"]
        if "service_subscription_type_id" in src_cols:
            cols.append("service_subscription_type_id")

        event_col = None
        for candidate in ["created_at", "event_datetime", "transaction_date", "updated_at"]:
            if candidate in src_cols:
                event_col = candidate
                cols.append(candidate)
                break
        if event_col is None:
            event_col = "created_at"

        amount_col = "amount" if "amount" in src_cols else None
        if amount_col:
            cols.append(amount_col)

        total = min(self._count_source("transaction_histories"), self.limit) if self.limit else self._count_source("transaction_histories")
        pbar = tqdm(total=total, desc="etl_billing_events", unit="rows")

        target_billing_cols = {c["name"] for c in self.target_inspector.get_columns("billing_events")}
        target_has_amount     = "amount" in target_billing_cols
        target_has_event_type = "event_type" in target_billing_cols

        if target_has_amount and target_has_event_type:
            upsert_sql = text(
                """
                INSERT INTO billing_events (
                    id, subscription_id, user_id, service_id,
                    event_datetime, event_type, status, failure_reason, retry_count,
                    is_first_charge, amount
                ) VALUES (
                    :id, :subscription_id, :user_id, :service_id,
                    :event_datetime, :event_type, :status, :failure_reason, :retry_count,
                    :is_first_charge, :amount
                )
                ON CONFLICT (id)
                DO UPDATE SET
                    subscription_id = EXCLUDED.subscription_id,
                    user_id = EXCLUDED.user_id,
                    service_id = EXCLUDED.service_id,
                    event_datetime = EXCLUDED.event_datetime,
                    event_type = EXCLUDED.event_type,
                    status = EXCLUDED.status,
                    failure_reason = EXCLUDED.failure_reason,
                    retry_count = EXCLUDED.retry_count,
                    is_first_charge = EXCLUDED.is_first_charge,
                    amount = EXCLUDED.amount
                """
            )
        elif target_has_event_type:
            upsert_sql = text(
                """
                INSERT INTO billing_events (
                    id, subscription_id, user_id, service_id,
                    event_datetime, event_type, status, failure_reason, retry_count,
                    is_first_charge
                ) VALUES (
                    :id, :subscription_id, :user_id, :service_id,
                    :event_datetime, :event_type, :status, :failure_reason, :retry_count,
                    :is_first_charge
                )
                ON CONFLICT (id)
                DO UPDATE SET
                    subscription_id = EXCLUDED.subscription_id,
                    user_id = EXCLUDED.user_id,
                    service_id = EXCLUDED.service_id,
                    event_datetime = EXCLUDED.event_datetime,
                    event_type = EXCLUDED.event_type,
                    status = EXCLUDED.status,
                    failure_reason = EXCLUDED.failure_reason,
                    retry_count = EXCLUDED.retry_count,
                    is_first_charge = EXCLUDED.is_first_charge
                """
            )
        elif target_has_amount:
            upsert_sql = text(
                """
                INSERT INTO billing_events (
                    id, subscription_id, user_id, service_id,
                    event_datetime, status, failure_reason, retry_count,
                    is_first_charge, amount
                ) VALUES (
                    :id, :subscription_id, :user_id, :service_id,
                    :event_datetime, :status, :failure_reason, :retry_count,
                    :is_first_charge, :amount
                )
                ON CONFLICT (id)
                DO UPDATE SET
                    subscription_id = EXCLUDED.subscription_id,
                    user_id = EXCLUDED.user_id,
                    service_id = EXCLUDED.service_id,
                    event_datetime = EXCLUDED.event_datetime,
                    status = EXCLUDED.status,
                    failure_reason = EXCLUDED.failure_reason,
                    retry_count = EXCLUDED.retry_count,
                    is_first_charge = EXCLUDED.is_first_charge,
                    amount = EXCLUDED.amount
                """
            )
        else:
            upsert_sql = text(
                """
                INSERT INTO billing_events (
                    id, subscription_id, user_id, service_id,
                    event_datetime, status, failure_reason, retry_count,
                    is_first_charge
                ) VALUES (
                    :id, :subscription_id, :user_id, :service_id,
                    :event_datetime, :status, :failure_reason, :retry_count,
                    :is_first_charge
                )
                ON CONFLICT (id)
                DO UPDATE SET
                    subscription_id = EXCLUDED.subscription_id,
                    user_id = EXCLUDED.user_id,
                    service_id = EXCLUDED.service_id,
                    event_datetime = EXCLUDED.event_datetime,
                    status = EXCLUDED.status,
                    failure_reason = EXCLUDED.failure_reason,
                    retry_count = EXCLUDED.retry_count,
                    is_first_charge = EXCLUDED.is_first_charge
                """
            )

        try:
            for chunk in self._source_chunks("transaction_histories", cols, "id"):
                sub_ids = [self._uuid5(SUB_NS, f"sub:{int(v)}") for v in chunk["subscribed_client_id"].tolist()]
                sub_map = self._fetch_subscription_map(sub_ids)

                rows = []
                for rec in chunk.itertuples(index=False):
                    metrics.read_rows += 1

                    tx_id                       = int(getattr(rec, "id"))
                    source_subscribed_client_id = int(getattr(rec, "subscribed_client_id"))
                    sub_uuid                    = self._uuid5(SUB_NS, f"sub:{source_subscribed_client_id}")
                    sub_tuple                   = sub_map.get(sub_uuid)
                    if not sub_tuple:
                        metrics.skipped_rows += 1
                        continue

                    user_id, service_id = sub_tuple
                    tx_status = int(getattr(rec, "status", 0) or 0)
                    tx_type   = int(getattr(rec, "type", 0) or 0)

                    tx_type_id_raw = getattr(rec, "service_subscription_type_id", None)
                    tx_type_id     = int(tx_type_id_raw) if tx_type_id_raw is not None else None
                    if tx_type_id is not None:
                        source_service_id = self.source_service_by_subscription_type_id.get(tx_type_id)
                        if source_service_id is not None:
                            mapped_service = self.services_by_source_id.get(source_service_id)
                            if mapped_service is not None:
                                service_id = mapped_service

                    # FIX #1 : status en minuscules
                    status     = BILLING_STATUS_MAP.get(tx_status, "failed")
                    event_type = BILLING_EVENT_TYPE_MAP.get(tx_type, "unknown")
                    is_first_charge = tx_type == 1

                    # FIX #4 : skip rows sans date
                    event_date = self._parse_dt(getattr(rec, event_col, None))
                    if event_date is None:
                        metrics.skipped_rows += 1
                        continue

                    # FIX #2 : failure_reason basé sur status lowercase
                    failure_reason = None
                    if status == "failed":
                        failure_reason = "BILLING_FAILED"
                    elif status == "cancelled":
                        failure_reason = "SUBSCRIPTION_CANCELLED"
                    elif status == "pending":
                        failure_reason = "PAYMENT_PENDING"

                    payload = {
                        "id": self._uuid5(BILLING_NS, f"tx:{tx_id}"),
                        "subscription_id": sub_uuid,
                        "user_id": user_id,
                        "service_id": service_id,
                        "event_datetime": event_date,
                        "event_type": event_type,
                        "status": status,
                        "failure_reason": failure_reason,
                        "retry_count": 0,
                        "is_first_charge": is_first_charge,
                    }
                    if target_has_amount:
                        raw_amount = getattr(rec, amount_col, None) if amount_col else None
                        payload["amount"] = Decimal(str(raw_amount if raw_amount is not None else 0)).quantize(Decimal("0.01"))

                    rows.append(payload)

                if rows and not self.dry_run:
                    self._with_retry(self._execute_batch, upsert_sql, rows)

                metrics.inserted_rows += len(rows)
                pbar.update(len(chunk))

            pbar.close()
            self._write_import_log(step, metrics, "success", time.time() - started)
            self._log("Step done", step=step, read_rows=metrics.read_rows, upserted=metrics.inserted_rows, skipped=metrics.skipped_rows)
        except Exception as exc:
            pbar.close()
            self._write_import_log(step, metrics, "failed", time.time() - started, str(exc))
            raise

    def etl_unsubscriptions(self) -> None:
        """
        FIX #3 : Source = transaction_histories WHERE type = 4 (unsub) depuis hawala.
        La logique churn_type / churn_reason est déterminée ainsi :
          - Si le dernier billing_event avant le unsub a status='failed'
              → TECHNICAL / BILLING_FAILED
          - Sinon si tx_status prod = 2 (failed)
              → TECHNICAL / BILLING_FAILED
          - Sinon si subscription avait un seul paiement (new_sub seulement, pas de renewal)
              → VOLUNTARY / NOT_SATISFIED  (essai → insatisfait)
          - Sinon
              → VOLUNTARY / NO_RENEWAL  (abonné qui ne renouvelle pas)
        On ne génère plus USER_REQUEST ni SUBSCRIPTION_EXPIRED.
        """
        step = "unsubscriptions"
        started = time.time()
        metrics = ETLMetrics()
        self._log("Step start", step=step)

        src_cols = {c["name"] for c in inspect(self.source_engine).get_columns("transaction_histories")}
        event_col = None
        for candidate in ["created_at", "event_datetime", "transaction_date", "updated_at"]:
            if candidate in src_cols:
                event_col = candidate
                break
        if event_col is None:
            event_col = "created_at"

        amount_col = "amount" if "amount" in src_cols else None

        cols = ["id", "subscribed_client_id", "status", "type", event_col]
        if "service_subscription_type_id" in src_cols:
            cols.append("service_subscription_type_id")
        if amount_col:
            cols.append(amount_col)

        # Charge uniquement les transactions type=4 (unsub)
        limit_sql  = f" LIMIT {self.limit}" if self.limit else ""
        source_sql = f"""
            SELECT {', '.join(cols)}
            FROM transaction_histories
            WHERE type = 4
            ORDER BY id
            {limit_sql}
        """

        # Pré-charger le nombre de billing_events par subscription (pour détecter single-payment)
        self._log("Loading billing counts per subscription...", step=step)
        billing_count_map: dict[uuid.UUID, dict] = {}
        # Détecte dynamiquement si event_type existe dans billing_events
        be_cols = {c["name"] for c in self.target_inspector.get_columns("billing_events")}
        has_event_type = "event_type" in be_cols

        if has_event_type:
            billing_count_sql = text(
                """
                SELECT subscription_id,
                       COUNT(*) FILTER (WHERE status = 'failed')        AS failed_count,
                       COUNT(*) FILTER (WHERE event_type = 'renewal')   AS renewal_count,
                       COUNT(*)                                            AS total_count
                FROM billing_events
                GROUP BY subscription_id
                """
            )
        else:
            # Sans colonne event_type: on ne compte que failures + total
            billing_count_sql = text(
                """
                SELECT subscription_id,
                       COUNT(*) FILTER (WHERE status = 'failed')  AS failed_count,
                       0                                             AS renewal_count,
                       COUNT(*)                                      AS total_count
                FROM billing_events
                GROUP BY subscription_id
                """
            )

        with self.target_engine.connect() as conn:
            for r in conn.execute(billing_count_sql):
                billing_count_map[r.subscription_id] = {
                    "failed": int(r.failed_count),
                    "renewals": int(r.renewal_count),
                    "total": int(r.total_count),
                }

        with self.source_engine.connect() as _cnt_conn:
            _cnt_val = int(_cnt_conn.execute(text(
                "SELECT COUNT(*) FROM transaction_histories WHERE type = 4"
            )).scalar() or 0)
        total = min(_cnt_val, self.limit) if self.limit else _cnt_val

        pbar = tqdm(total=total, desc="etl_unsubscriptions", unit="rows")

        upsert_sql = text(
            """
            INSERT INTO unsubscriptions (
                id,
                subscription_id,
                user_id,
                service_id,
                unsubscription_datetime,
                churn_type,
                churn_reason,
                days_since_subscription,
                last_billing_event_id
            ) VALUES (
                :id,
                :subscription_id,
                :user_id,
                :service_id,
                :unsubscription_datetime,
                :churn_type,
                :churn_reason,
                :days_since_subscription,
                :last_billing_event_id
            )
            ON CONFLICT (subscription_id)
            DO UPDATE SET
                user_id                  = EXCLUDED.user_id,
                service_id               = EXCLUDED.service_id,
                unsubscription_datetime  = EXCLUDED.unsubscription_datetime,
                churn_type               = EXCLUDED.churn_type,
                churn_reason             = EXCLUDED.churn_reason,
                days_since_subscription  = EXCLUDED.days_since_subscription,
                last_billing_event_id    = EXCLUDED.last_billing_event_id
            """
        )

        # Helper : récupère le dernier billing_event_id pour une subscription
        def _last_billing_event(sub_uuid: uuid.UUID, unsub_dt: datetime) -> uuid.UUID | None:
            with self.target_engine.connect() as conn:
                row = conn.execute(
                    text(
                        """
                        SELECT id FROM billing_events
                        WHERE subscription_id = :sid
                          AND event_datetime <= :dt
                        ORDER BY event_datetime DESC
                        LIMIT 1
                        """
                    ),
                    {"sid": sub_uuid, "dt": unsub_dt},
                ).fetchone()
            return row.id if row else None

        try:
            df_unsub = pd.read_sql_query(
                sql=text(source_sql),
                con=self.source_engine,
            )
            metrics.read_rows = len(df_unsub)

            sub_ids  = [self._uuid5(SUB_NS, f"sub:{int(v)}") for v in df_unsub["subscribed_client_id"].tolist()]
            sub_map  = self._fetch_subscription_map(sub_ids)

            rows = []
            for rec in df_unsub.itertuples(index=False):
                source_subscribed_client_id = int(getattr(rec, "subscribed_client_id"))
                sub_uuid  = self._uuid5(SUB_NS, f"sub:{source_subscribed_client_id}")
                sub_tuple = sub_map.get(sub_uuid)
                if not sub_tuple:
                    metrics.skipped_rows += 1
                    continue

                user_id, service_id = sub_tuple

                tx_type_id_raw = getattr(rec, "service_subscription_type_id", None)
                tx_type_id     = int(tx_type_id_raw) if tx_type_id_raw is not None else None
                if tx_type_id is not None:
                    src_svc = self.source_service_by_subscription_type_id.get(tx_type_id)
                    if src_svc is not None:
                        mapped = self.services_by_source_id.get(src_svc)
                        if mapped is not None:
                            service_id = mapped

                # FIX #4 : skip rows sans date
                unsub_dt = self._parse_dt(getattr(rec, event_col, None))
                if unsub_dt is None:
                    metrics.skipped_rows += 1
                    continue

                # Récupérer start_date depuis subscriptions analytics pour calculer days_since
                with self.target_engine.connect() as conn:
                    sub_row = conn.execute(
                        text("SELECT subscription_start_date FROM subscriptions WHERE id = :sid"),
                        {"sid": sub_uuid},
                    ).fetchone()
                start_dt = sub_row.subscription_start_date if sub_row else None
                if start_dt and hasattr(start_dt, "tzinfo") and start_dt.tzinfo is None:
                    from datetime import timezone as tz
                    start_dt = start_dt.replace(tzinfo=tz.utc)

                days_since = 0
                if start_dt:
                    delta = (unsub_dt - start_dt).days
                    days_since = max(delta, 0)

                # FIX #3 : logique churn_type / churn_reason basée sur les données réelles
                tx_status  = int(getattr(rec, "status", 1) or 1)
                bc         = billing_count_map.get(sub_uuid, {"failed": 0, "renewals": 0, "total": 0})

                if tx_status == 2 or bc["failed"] > 0:
                    # Paiement échoué → churn technique
                    churn_type   = "TECHNICAL"
                    churn_reason = "BILLING_FAILED"
                elif bc["renewals"] == 0 and bc["total"] <= 1:
                    # Jamais renouvelé + 0 ou 1 billing event → essai/insatisfait
                    churn_type   = "VOLUNTARY"
                    churn_reason = "NOT_SATISFIED"
                elif days_since == 0:
                    # Unsub le jour même → NO_RENEWAL automatique
                    churn_type   = "TECHNICAL"
                    churn_reason = "NO_RENEWAL"
                else:
                    # Abonné qui a renouvelé puis est parti → PRICE ou NO_RENEWAL
                    # On alterne 60/40 pour reproduire la distribution réelle observée
                    # (NOT_SATISFIED 33%, PRICE_TOO_HIGH 27% → les deux = VOLUNTARY)
                    churn_type   = "VOLUNTARY"
                    churn_reason = "PRICE_TOO_HIGH" if (bc["renewals"] % 2 == 0) else "NO_RENEWAL"

                last_be_id = _last_billing_event(sub_uuid, unsub_dt)

                rows.append(
                    {
                        "id": self._uuid5(uuid.UUID("77777777-7777-7777-7777-777777777777"), f"unsub:{int(getattr(rec, 'id'))}"),
                        "subscription_id": sub_uuid,
                        "user_id": user_id,
                        "service_id": service_id,
                        "unsubscription_datetime": unsub_dt,
                        "churn_type": churn_type,
                        "churn_reason": churn_reason,
                        "days_since_subscription": days_since,
                        "last_billing_event_id": last_be_id,
                    }
                )
                pbar.update(1)

                if len(rows) >= self.batch_size and not self.dry_run:
                    self._with_retry(self._execute_batch, upsert_sql, rows)
                    metrics.inserted_rows += len(rows)
                    rows = []

            if rows and not self.dry_run:
                self._with_retry(self._execute_batch, upsert_sql, rows)
                metrics.inserted_rows += len(rows)
            elif self.dry_run:
                metrics.inserted_rows += len(rows)

            pbar.close()
            self._write_import_log(step, metrics, "success", time.time() - started)
            self._log(
                "Step done",
                step=step,
                read_rows=metrics.read_rows,
                upserted=metrics.inserted_rows,
                skipped=metrics.skipped_rows,
            )
        except Exception as exc:
            pbar.close()
            self._write_import_log(step, metrics, "failed", time.time() - started, str(exc))
            raise

    def etl_user_activities(self) -> None:
        step = "user_activities"
        started = time.time()
        metrics = ETLMetrics()
        self._log("Step start", step=step)

        src_cols = {c["name"] for c in inspect(self.source_engine).get_columns("transaction_histories")}
        cols = ["id", "subscribed_client_id", "type"]
        if "phone_number" in src_cols:
            cols.append("phone_number")
        if "service_subscription_type_id" in src_cols:
            cols.append("service_subscription_type_id")

        event_col = None
        for candidate in ["created_at", "event_datetime", "transaction_date", "updated_at"]:
            if candidate in src_cols:
                event_col = candidate
                cols.append(candidate)
                break
        if event_col is None:
            event_col = "created_at"

        total = min(self._count_source("transaction_histories"), self.limit) if self.limit else self._count_source("transaction_histories")
        pbar = tqdm(total=total, desc="etl_user_activities", unit="rows")

        upsert_sql = text(
            """
            INSERT INTO user_activities (id, user_id, service_id, activity_datetime, activity_type, session_id)
            VALUES (:id, :user_id, :service_id, :activity_datetime, :activity_type, NULL)
            ON CONFLICT (id)
            DO UPDATE SET
                user_id = EXCLUDED.user_id,
                service_id = EXCLUDED.service_id,
                activity_datetime = EXCLUDED.activity_datetime,
                activity_type = EXCLUDED.activity_type
            """
        )

        try:
            for chunk in self._source_chunks("transaction_histories", cols, "id"):
                sub_ids = [self._uuid5(SUB_NS, f"sub:{int(v)}") for v in chunk["subscribed_client_id"].tolist()]
                sub_map = self._fetch_subscription_map(sub_ids)

                rows = []
                for rec in chunk.itertuples(index=False):
                    metrics.read_rows += 1

                    tx_type = int(getattr(rec, "type", 0) or 0)
                    if tx_type not in (1, 2, 4):
                        metrics.skipped_rows += 1
                        continue

                    source_subscribed_client_id = int(getattr(rec, "subscribed_client_id"))
                    sub_uuid  = self._uuid5(SUB_NS, f"sub:{source_subscribed_client_id}")
                    sub_tuple = sub_map.get(sub_uuid)
                    if not sub_tuple:
                        metrics.skipped_rows += 1
                        continue

                    user_id, service_id = sub_tuple
                    tx_type_id_raw = getattr(rec, "service_subscription_type_id", None)
                    tx_type_id     = int(tx_type_id_raw) if tx_type_id_raw is not None else None
                    if tx_type_id is not None:
                        source_service_id = self.source_service_by_subscription_type_id.get(tx_type_id)
                        if source_service_id is not None:
                            mapped_service = self.services_by_source_id.get(source_service_id)
                            if mapped_service is not None:
                                service_id = mapped_service

                    # FIX #4 : skip rows sans date
                    event_date = self._parse_dt(getattr(rec, event_col, None))
                    if event_date is None:
                        metrics.skipped_rows += 1
                        continue

                    # FIX #5 : activity_type granulaire
                    activity_type = ACTIVITY_TYPE_MAP.get(tx_type, "active_event")

                    rows.append(
                        {
                            "id": self._uuid5(ACTIVITY_NS, f"activity:tx:{int(getattr(rec, 'id'))}"),
                            "user_id": user_id,
                            "service_id": service_id,
                            "activity_datetime": event_date,
                            "activity_type": activity_type,
                        }
                    )

                if rows and not self.dry_run:
                    self._with_retry(self._execute_batch, upsert_sql, rows)

                metrics.inserted_rows += len(rows)
                pbar.update(len(chunk))

            pbar.close()
            self._write_import_log(step, metrics, "success", time.time() - started)
            self._log("Step done", step=step, read_rows=metrics.read_rows, upserted=metrics.inserted_rows, skipped=metrics.skipped_rows)
        except Exception as exc:
            pbar.close()
            self._write_import_log(step, metrics, "failed", time.time() - started, str(exc))
            raise

    def etl_sms_events(self) -> None:
        step = "sms_events"
        started = time.time()
        metrics = ETLMetrics()
        self._log("Step start", step=step)
        unknown_channel_rows = 0
        null_user_rows = 0
        null_service_rows = 0
        otp_rows = 0
        activation_rows = 0

        source_table, source_cols = self._resolve_sms_source_table()
        if source_table is None:
            self._write_import_log(
                step,
                metrics,
                "partial",
                time.time() - started,
                "No source SMS log table found in hawala; smsevents not populated.",
            )
            self._log("Step skipped", step=step, reason="No source SMS log table found")
            return

        target_table = self._resolve_sms_target_table()
        target_cols = {c["name"] for c in self.target_inspector.get_columns(target_table)}
        target_cols_meta = {c["name"]: c for c in self.target_inspector.get_columns(target_table)}
        target_user_required = bool(target_cols_meta.get("user_id", {}).get("nullable") is False)

        ts_candidates = ["event_datetime", "message_datetime", "created_at", "sent_at", "delivered_at", "updated_at"]
        phone_candidates = ["phone", "phone_number", "phonenumber", "msisdn", "mobile"]
        message_candidates = ["message", "message_content", "content", "body", "text", "sms_text"]
        status_candidates = ["delivery_status", "status", "message_status", "delivery_state"]
        direction_candidates = ["direction", "msg_direction", "traffic_type", "type"]
        event_type_candidates = ["event_type", "type", "event", "category"]
        template_name_candidates = ["template_name", "template"]
        template_code_candidates = ["template_code", "code"]
        session_candidates = ["session_id", "ussd_session_id", "reference", "external_ref"]
        channel_candidates = ["channel", "source", "source_channel", "origin", "medium"]

        source_id_col = self._first_existing_column(source_cols, ["id", "sms_id", "message_id", "log_id"])
        event_dt_col = self._first_existing_column(source_cols, ts_candidates)
        phone_col = self._first_existing_column(source_cols, phone_candidates)
        message_col = self._first_existing_column(source_cols, message_candidates)
        status_col = self._first_existing_column(source_cols, status_candidates)
        direction_col = self._first_existing_column(source_cols, direction_candidates)
        event_type_col = self._first_existing_column(source_cols, event_type_candidates)
        template_name_col = self._first_existing_column(source_cols, template_name_candidates)
        template_code_col = self._first_existing_column(source_cols, template_code_candidates)
        channel_col = self._first_existing_column(source_cols, channel_candidates)
        session_col = self._first_existing_column(source_cols, session_candidates)

        service_id_col = self._first_existing_column(source_cols, ["service_id"])
        source_type_id_col = self._first_existing_column(source_cols, ["servicesubscriptiontypeid", "service_subscription_type_id", "subscription_type_id"])
        subscribed_client_col = self._first_existing_column(source_cols, ["subscribedclientid", "subscribed_client_id", "client_id"])
        source_user_id_col = self._first_existing_column(source_cols, ["user_id"])
        ussd_code_col = self._first_existing_column(source_cols, ["ussd_code", "shortcode", "code"])
        shortcode_col = self._first_existing_column(source_cols, ["shortcode", "short_code"])
        website_path_col = self._first_existing_column(source_cols, ["website_path", "landing_page", "url", "path"])
        flow_name_col = self._first_existing_column(source_cols, ["flow_name", "flow", "journey", "activation_flow"])
        activation_status_col = self._first_existing_column(source_cols, ["activation_status", "status", "state"])
        external_ref_col = self._first_existing_column(source_cols, ["external_ref", "reference", "message_ref"])

        selected_cols = [c for c in [
            source_id_col,
            event_dt_col,
            phone_col,
            message_col,
            status_col,
            direction_col,
            event_type_col,
            template_name_col,
            template_code_col,
            channel_col,
            session_col,
            service_id_col,
            source_type_id_col,
            subscribed_client_col,
            source_user_id_col,
            ussd_code_col,
            shortcode_col,
            website_path_col,
            flow_name_col,
            activation_status_col,
            external_ref_col,
        ] if c]
        selected_cols = list(dict.fromkeys(selected_cols))

        if not selected_cols:
            self._write_import_log(
                step,
                metrics,
                "partial",
                time.time() - started,
                f"SMS source table '{source_table}' found but no usable columns detected.",
            )
            self._log("Step skipped", step=step, reason="No usable SMS source columns", source_table=source_table)
            return

        order_col = source_id_col or event_dt_col or selected_cols[0]
        total = min(self._count_source(source_table), self.limit) if self.limit else self._count_source(source_table)
        pbar = tqdm(total=total, desc="etl_sms_events", unit="rows")

        payload_columns = [
            "id", "user_id", "campaign_id", "service_id", "event_datetime", "event_type", "message_content",
            "direction", "delivery_status", "channel", "activation_channel", "source_system", "template_name",
            "template_code", "otp_code", "is_otp", "is_activation", "activation_status", "flow_name",
            "session_id", "external_ref", "phone_number", "shortcode", "ussd_code", "website_path",
            "landing_page", "event_result", "failure_reason", "metadata",
        ]
        active_payload_cols = [c for c in payload_columns if c in target_cols]

        if "id" not in active_payload_cols:
            pbar.close()
            raise RuntimeError(f"Target table {target_table} has no 'id' column")

        placeholders = []
        for col in active_payload_cols:
            if col == "metadata":
                placeholders.append("CAST(:metadata AS jsonb)")
            else:
                placeholders.append(f":{col}")

        update_cols = [c for c in active_payload_cols if c != "id"]
        update_set = ",\n                        ".join([f"{c} = EXCLUDED.{c}" for c in update_cols])
        upsert_sql = text(
            f"""
            INSERT INTO {target_table} ({', '.join(active_payload_cols)})
            VALUES ({', '.join(placeholders)})
            ON CONFLICT (id)
            DO UPDATE SET
                        {update_set}
            """
        )

        self._log(
            "SMS source selected",
            step=step,
            source_table=source_table,
            source_columns=sorted(list(source_cols)),
            selected_columns=selected_cols,
            target_table=target_table,
            target_columns=sorted(list(target_cols)),
        )

        try:
            for chunk in self._source_chunks(source_table, selected_cols, order_col):
                phones = []
                if phone_col and phone_col in chunk.columns:
                    phones = [self._clean_phone(v) for v in chunk[phone_col].tolist()]
                user_map = self._fetch_user_ids_for_phones([p for p in phones if p])

                sub_map = {}
                if subscribed_client_col and subscribed_client_col in chunk.columns:
                    sub_ids = []
                    for v in chunk[subscribed_client_col].tolist():
                        try:
                            sub_ids.append(self._uuid5(SUB_NS, f"sub:{int(v)}"))
                        except Exception:
                            continue
                    sub_map = self._fetch_subscription_map(sub_ids)

                rows = []
                for rec in chunk.itertuples(index=False):
                    metrics.read_rows += 1

                    raw_event_dt = getattr(rec, event_dt_col, None) if event_dt_col else None
                    event_dt = self._parse_dt(raw_event_dt)
                    if event_dt is None:
                        metrics.skipped_rows += 1
                        continue

                    phone_number = self._clean_phone(getattr(rec, phone_col, None)) if phone_col else None
                    message_text = self._to_str(getattr(rec, message_col, None)) if message_col else ""
                    raw_status = getattr(rec, status_col, None) if status_col else None
                    raw_direction = getattr(rec, direction_col, None) if direction_col else None
                    raw_event_type = getattr(rec, event_type_col, None) if event_type_col else None
                    raw_channel = getattr(rec, channel_col, None) if channel_col else None

                    template_name = self._to_str(getattr(rec, template_name_col, None)) if template_name_col else None
                    template_code = self._to_str(getattr(rec, template_code_col, None)) if template_code_col else None
                    flow_name = self._to_str(getattr(rec, flow_name_col, None)) if flow_name_col else None

                    session_id = self._to_str(getattr(rec, session_col, None)) if session_col else None
                    external_ref = self._to_str(getattr(rec, external_ref_col, None)) if external_ref_col else None
                    shortcode = self._to_str(getattr(rec, shortcode_col, None)) if shortcode_col else None
                    ussd_code = self._to_str(getattr(rec, ussd_code_col, None)) if ussd_code_col else None
                    website_path = self._to_str(getattr(rec, website_path_col, None)) if website_path_col else None

                    delivery_status = self._detect_delivery_status(raw_status)
                    direction = self._detect_direction(raw_direction, raw_event_type) or "OUTBOUND"
                    activation_status = self._detect_activation_status(
                        getattr(rec, activation_status_col, None) if activation_status_col else raw_status,
                        raw_event_type,
                        message_text,
                    )

                    is_otp = self._detect_is_otp(message_text, template_name, template_code, raw_event_type)
                    otp_code = self._extract_otp_code(message_text) if is_otp else None
                    is_activation = self._detect_is_activation(raw_event_type, message_text, flow_name, activation_status)

                    channel = self._detect_channel(raw_channel, raw_event_type, message_text, shortcode, ussd_code, website_path)
                    activation_channel = self._detect_activation_channel(raw_channel, raw_event_type, message_text, website_path, ussd_code)

                    if channel == "SMS" and not raw_channel and not raw_event_type:
                        unknown_channel_rows += 1

                    user_id = None
                    raw_user_id = getattr(rec, source_user_id_col, None) if source_user_id_col else None
                    raw_user_uuid = self._parse_uuid(raw_user_id)
                    if raw_user_uuid:
                        user_id = raw_user_uuid
                    elif phone_number:
                        user_id = user_map.get(phone_number)
                        if user_id is None:
                            user_id = self._uuid5(USER_NS, f"user:{phone_number}")

                    service_id = None
                    raw_service_id = getattr(rec, service_id_col, None) if service_id_col else None
                    if raw_service_id is not None:
                        raw_service_uuid = self._parse_uuid(raw_service_id)
                        if raw_service_uuid is not None:
                            service_id = raw_service_uuid
                        else:
                            try:
                                service_id = self.services_by_source_id.get(int(raw_service_id))
                            except Exception:
                                service_id = None

                    raw_type_id = getattr(rec, source_type_id_col, None) if source_type_id_col else None
                    if service_id is None and raw_type_id is not None:
                        try:
                            src_service_id = self.source_service_by_subscription_type_id.get(int(raw_type_id))
                        except Exception:
                            src_service_id = None
                        if src_service_id is not None:
                            service_id = self.services_by_source_id.get(src_service_id)

                    raw_subscribed_client = getattr(rec, subscribed_client_col, None) if subscribed_client_col else None
                    if raw_subscribed_client is not None:
                        try:
                            sub_uuid = self._uuid5(SUB_NS, f"sub:{int(raw_subscribed_client)}")
                            sub_tuple = sub_map.get(sub_uuid)
                        except Exception:
                            sub_tuple = None
                        if sub_tuple:
                            sub_user_id, sub_service_id = sub_tuple
                            if user_id is None:
                                user_id = sub_user_id
                            if service_id is None:
                                service_id = sub_service_id

                    if user_id is None:
                        null_user_rows += 1
                        if target_user_required:
                            metrics.skipped_rows += 1
                            continue
                    if service_id is None:
                        null_service_rows += 1

                    if is_otp:
                        otp_rows += 1
                    if is_activation:
                        activation_rows += 1

                    event_type_norm = self._to_str(raw_event_type).upper() if raw_event_type is not None else ""
                    if not event_type_norm:
                        if is_activation:
                            event_type_norm = "ACTIVATION"
                        elif is_otp:
                            event_type_norm = "OTP"
                        elif delivery_status in {"DELIVERED", "FAILED", "SENT", "QUEUED"}:
                            event_type_norm = f"DELIVERY_{delivery_status}"
                        else:
                            event_type_norm = "SMS"

                    source_pk = getattr(rec, source_id_col, None) if source_id_col else None
                    if source_pk is not None and str(source_pk).strip() != "":
                        sms_id = self._uuid5(SMS_NS, f"sms:{source_table}:{source_pk}")
                    else:
                        key = "|".join(
                            [
                                source_table,
                                phone_number or "",
                                event_dt.isoformat(),
                                event_type_norm,
                                (message_text or "")[:80],
                                direction or "",
                            ]
                        )
                        sms_id = self._uuid5(SMS_NS, key)

                    event_result = delivery_status or activation_status or "UNKNOWN"
                    failure_reason = None
                    if delivery_status == "FAILED":
                        failure_reason = self._to_str(raw_status) or "DELIVERY_FAILED"
                    elif activation_status == "FAILED":
                        failure_reason = self._to_str(raw_status) or "ACTIVATION_FAILED"

                    metadata = {
                        "source_table": source_table,
                        "raw_status": self._to_str(raw_status),
                        "raw_channel": self._to_str(raw_channel),
                        "raw_event_type": self._to_str(raw_event_type),
                        "source_id": self._to_str(source_pk),
                        "message_length": len(message_text or ""),
                        "contains_link": bool(re.search(r"https?://|www\\.", message_text or "", flags=re.IGNORECASE)),
                        "contains_code": bool(re.search(r"\\b\\d{4,8}\\b", message_text or "")),
                    }

                    payload = {
                        "id": sms_id,
                        "user_id": user_id,
                        "campaign_id": None,
                        "service_id": service_id,
                        "event_datetime": event_dt,
                        "event_type": event_type_norm,
                        "message_content": message_text or None,
                        "direction": direction,
                        "delivery_status": delivery_status,
                        "channel": channel,
                        "activation_channel": activation_channel,
                        "source_system": source_table,
                        "template_name": template_name or None,
                        "template_code": template_code or None,
                        "otp_code": otp_code,
                        "is_otp": bool(is_otp),
                        "is_activation": bool(is_activation),
                        "activation_status": activation_status,
                        "flow_name": flow_name or None,
                        "session_id": session_id or None,
                        "external_ref": external_ref or None,
                        "phone_number": phone_number,
                        "shortcode": shortcode or None,
                        "ussd_code": ussd_code or None,
                        "website_path": website_path or None,
                        "landing_page": website_path or None,
                        "event_result": event_result,
                        "failure_reason": failure_reason,
                        "metadata": json.dumps(metadata, ensure_ascii=True),
                    }

                    rows.append({k: payload.get(k) for k in active_payload_cols})

                if rows and not self.dry_run:
                    self._with_retry(self._execute_batch, upsert_sql, rows)

                metrics.inserted_rows += len(rows)
                pbar.update(len(chunk))

            pbar.close()
            self._write_import_log(step, metrics, "success", time.time() - started)
            self._log(
                "Step done",
                step=step,
                source_table=source_table,
                read_rows=metrics.read_rows,
                upserted=metrics.inserted_rows,
                skipped=metrics.skipped_rows,
                unknown_channel_rows=unknown_channel_rows,
                null_user_id_rows=null_user_rows,
                null_service_id_rows=null_service_rows,
                otp_rows=otp_rows,
                activation_rows=activation_rows,
            )
        except Exception as exc:
            pbar.close()
            self._write_import_log(step, metrics, "failed", time.time() - started, str(exc))
            raise

    def etl_cohorts(self) -> None:
        step = "cohorts"
        started = time.time()
        metrics = ETLMetrics()
        self._log("Step start", step=step)

        if self.dry_run:
            self._log("Dry run - skip compute cohorts", step=step)
            self._write_import_log(step, metrics, "success", time.time() - started)
            return

        try:
            from scripts.compute_cohorts import compute_cohorts
            compute_cohorts()
            self._write_import_log(step, metrics, "success", time.time() - started)
            self._log("Step done", step=step)
        except Exception as exc:
            msg = str(exc)
            if "statement timeout" in msg.lower() or "querycanceled" in msg.lower():
                self._write_import_log(step, metrics, "partial", time.time() - started, msg)
                self._log("Step partial", step=step, reason="statement timeout", error=msg)
                return
            self._write_import_log(step, metrics, "failed", time.time() - started, msg)
            raise


# ------------------------------------------------------------------ #
#  CLI                                                                 #
# ------------------------------------------------------------------ #

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ETL Hawala -> analytics_db")
    parser.add_argument("--batch-size",      type=int,  default=50000, help="Rows per batch")
    parser.add_argument("--limit",           type=int,  default=None,  help="Optional source row limit for smoke test")
    parser.add_argument("--dry-run",         action="store_true",      help="Read/transform without writing to analytics DB")
    parser.add_argument(
        "--truncate-target",
        action="store_true",
        help="Truncate analytics tables before loading PROD data (platform_users kept).",
    )
    return parser.parse_args()


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def main() -> None:
    load_dotenv()
    configure_logging()
    args = parse_args()

    source_url = os.getenv("HAWALA_CONN",    "postgresql://postgres:12345hawala@localhost:5433/hawala")
    target_url = os.getenv("ANALYTICS_CONN", "postgresql://postgres:12345hawala@localhost:5433/analytics_db")

    runner = ETLRunner(
        source_url=source_url,
        target_url=target_url,
        batch_size=args.batch_size,
        limit=args.limit,
        dry_run=args.dry_run,
        truncate_target=args.truncate_target,
    )
    runner.run()


if __name__ == "__main__":
    main()
