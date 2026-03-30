"""
ETL Hawala (prod) -> analytics_db (PFE)

Usage:
  python etl_prod_to_analytics.py --batch-size 50000
  python etl_prod_to_analytics.py --batch-size 50000 --limit 10000

Environment variables:
  HAWALA_CONN     Source PostgreSQL connection URL
  ANALYTICS_CONN  Target PostgreSQL connection URL
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import bindparam, create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError, OperationalError
from tqdm import tqdm


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


USER_NS = uuid.UUID("11111111-1111-1111-1111-111111111111")
SUB_NS = uuid.UUID("22222222-2222-2222-2222-222222222222")
BILLING_NS = uuid.UUID("33333333-3333-3333-3333-333333333333")
ACTIVITY_NS = uuid.UUID("66666666-6666-6666-6666-666666666666")
SERVICE_NS = uuid.UUID("44444444-4444-4444-4444-444444444444")
SERVICE_TYPE_NS = uuid.UUID("55555555-5555-5555-5555-555555555555")

USER_STATUS_MAP = {
    1: "active",
    0: "inactive",
    -1: "inactive",
    -2: "inactive",
}

SUB_STATUS_MAP = {
    1: "active",
    0: "trial",
    -1: "cancelled",
    -2: "expired",
}

BILLING_STATUS_MAP = {
    0: "PENDING",
    1: "SUCCESS",
    2: "FAILED",
    3: "CANCELLED",
}

BILLING_EVENT_TYPE_MAP = {
    1: "new_sub",
    2: "renewal",
    3: "upgrade",
    4: "unsub",
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
        self.source_engine = create_engine(source_url, pool_pre_ping=True)
        self.target_engine = create_engine(target_url, pool_pre_ping=True)
        self.batch_size = batch_size
        self.limit = limit
        self.dry_run = dry_run
        self.truncate_target = truncate_target
        self.target_inspector = inspect(self.target_engine)

        self.services_by_source_id: dict[int, uuid.UUID] = {}
        self.source_service_by_subscription_type_id: dict[int, int] = {}

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
        self.etl_user_activities()
        self.etl_cohorts()

        imported_rows = self._count_target_rows(["users", "subscriptions", "billing_events", "user_activities"])
        min_date, max_date = self._source_tx_date_range()

        elapsed = time.time() - started
        self._log("ETL completed", duration_sec=round(elapsed, 2))
        print(f"ETL termine: {imported_rows} lignes importees, periode {min_date} -> {max_date}")

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
        # Keep platform_users intact; clear analytics/business data before fresh PROD load.
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
        if phone.startswith("216"):
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
            else:
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

            source_sql = text(
                f"SELECT {', '.join(select_cols)} FROM services ORDER BY id"
            )
            df = pd.read_sql_query(source_sql, self.source_engine)
            metrics.read_rows = len(df)

            rows = []
            for row in df.itertuples(index=False):
                source_id = int(row.id)
                raw_name = getattr(row, entitled_col, None)
                name = str(raw_name or "").strip() or f"service_{source_id}"
                source_status = int(row.status) if row.status is not None else 1
                raw_type = getattr(row, type_col, None) if type_col else None
                source_type = int(raw_type) if raw_type is not None else None

                freq_guess = 30
                if source_type is not None:
                    if source_type <= 1:
                        freq_guess = 1
                    elif source_type <= 7:
                        freq_guess = 7
                service_type_id = st_map.get(freq_guess) or next(iter(st_map.values()))
                service_uuid = self._uuid5(SERVICE_NS, f"service:{source_id}")

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

                    created_at = self._parse_dt(getattr(rec, "subscription_start_date", None))
                    if created_at is None:
                        created_at = datetime.now(timezone.utc)

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
                subscription_start_date, subscription_end_date, status
            ) VALUES (
                :id, :user_id, :service_id, NULL,
                :subscription_start_date, :subscription_end_date, :status
            )
            ON CONFLICT (id)
            DO UPDATE SET
                user_id = EXCLUDED.user_id,
                service_id = EXCLUDED.service_id,
                subscription_start_date = EXCLUDED.subscription_start_date,
                subscription_end_date = EXCLUDED.subscription_end_date,
                status = EXCLUDED.status
            """
        )

        self.source_service_by_subscription_type_id = self._load_subscription_type_to_service_map()

        default_service_id = next(iter(self.services_by_source_id.values()), None)
        mapped_via_service_id = 0
        mapped_via_type_id = 0
        mapped_via_default = 0
        skipped_unmapped_service = 0

        try:
            for chunk in self._source_chunks("subscribed_clients", cols, "id"):
                phones = [self._clean_phone(v) for v in chunk["phone_number"].tolist()]
                user_map = self._fetch_user_ids_for_phones([p for p in phones if p])

                rows = []
                for rec in chunk.itertuples(index=False):
                    metrics.read_rows += 1
                    source_client_id = int(getattr(rec, "id"))
                    source_status = int(getattr(rec, "status", 0) or 0)

                    phone = self._clean_phone(getattr(rec, "phone_number", None))
                    user_id = user_map.get(phone) if phone else None
                    if not user_id:
                        metrics.skipped_rows += 1
                        continue

                    raw_source_service_id = getattr(rec, "service_id", None)
                    raw_source_type_id = getattr(rec, "service_subscription_type_id", None)
                    source_service_id = int(raw_source_service_id) if raw_source_service_id is not None else None
                    source_type_id = int(raw_source_type_id) if raw_source_type_id is not None else None

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

                    start_date = self._parse_dt(getattr(rec, "subscription_start_date", None))
                    if start_date is None:
                        start_date = datetime.now(timezone.utc)
                    end_date = self._parse_dt(getattr(rec, "subscription_end_date", None))

                    rows.append(
                        {
                            "id": self._uuid5(SUB_NS, f"sub:{source_client_id}"),
                            "user_id": user_id,
                            "service_id": service_id,
                            "subscription_start_date": start_date,
                            "subscription_end_date": end_date,
                            "status": SUB_STATUS_MAP.get(source_status, "trial"),
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
        target_has_amount = "amount" in target_billing_cols
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

                    tx_id = int(getattr(rec, "id"))
                    source_subscribed_client_id = int(getattr(rec, "subscribed_client_id"))
                    sub_uuid = self._uuid5(SUB_NS, f"sub:{source_subscribed_client_id}")
                    sub_tuple = sub_map.get(sub_uuid)
                    if not sub_tuple:
                        metrics.skipped_rows += 1
                        continue

                    user_id, service_id = sub_tuple
                    tx_status = int(getattr(rec, "status", 0) or 0)
                    tx_type = int(getattr(rec, "type", 0) or 0)

                    # Prefer service resolved from transaction type mapping when available.
                    tx_type_id_raw = getattr(rec, "service_subscription_type_id", None)
                    tx_type_id = int(tx_type_id_raw) if tx_type_id_raw is not None else None
                    if tx_type_id is not None:
                        source_service_id = self.source_service_by_subscription_type_id.get(tx_type_id)
                        if source_service_id is not None:
                            mapped_service = self.services_by_source_id.get(source_service_id)
                            if mapped_service is not None:
                                service_id = mapped_service

                    status = BILLING_STATUS_MAP.get(tx_status, "FAILED")
                    event_type = BILLING_EVENT_TYPE_MAP.get(tx_type, "unknown")
                    is_first_charge = tx_type == 1

                    event_date = self._parse_dt(getattr(rec, event_col, None))
                    if event_date is None:
                        event_date = datetime.now(timezone.utc)

                    payload = {
                        "id": self._uuid5(BILLING_NS, f"tx:{tx_id}"),
                        "subscription_id": sub_uuid,
                        "user_id": user_id,
                        "service_id": service_id,
                        "event_datetime": event_date,
                        "event_type": event_type,
                        "status": status,
                        "failure_reason": None if status == "SUCCESS" else "SOURCE_STATUS_NOT_SUCCESS",
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
                    sub_uuid = self._uuid5(SUB_NS, f"sub:{source_subscribed_client_id}")
                    sub_tuple = sub_map.get(sub_uuid)
                    if not sub_tuple:
                        metrics.skipped_rows += 1
                        continue

                    user_id, service_id = sub_tuple
                    tx_type_id_raw = getattr(rec, "service_subscription_type_id", None)
                    tx_type_id = int(tx_type_id_raw) if tx_type_id_raw is not None else None
                    if tx_type_id is not None:
                        source_service_id = self.source_service_by_subscription_type_id.get(tx_type_id)
                        if source_service_id is not None:
                            mapped_service = self.services_by_source_id.get(source_service_id)
                            if mapped_service is not None:
                                service_id = mapped_service

                    event_date = self._parse_dt(getattr(rec, event_col, None))
                    if event_date is None:
                        event_date = datetime.now(timezone.utc)

                    rows.append(
                        {
                            "id": self._uuid5(ACTIVITY_NS, f"activity:tx:{int(getattr(rec, 'id'))}"),
                            "user_id": user_id,
                            "service_id": service_id,
                            "activity_datetime": event_date,
                            "activity_type": "churn_event" if tx_type == 4 else "active_event",
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

    def etl_cohorts(self) -> None:
        step = "cohorts"
        started = time.time()
        metrics = ETLMetrics(read_rows=0, inserted_rows=0)
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
            self._write_import_log(step, metrics, "failed", time.time() - started, str(exc))
            raise

    def _execute_batch(self, stmt, rows: list[dict[str, Any]]) -> None:
        with self.target_engine.begin() as conn:
            conn.execute(stmt, rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ETL Hawala -> analytics_db")
    parser.add_argument("--batch-size", type=int, default=50000, help="Rows per batch")
    parser.add_argument("--limit", type=int, default=None, help="Optional source row limit for smoke test")
    parser.add_argument("--dry-run", action="store_true", help="Read/transform without writing to analytics DB")
    parser.add_argument(
        "--truncate-target",
        action="store_true",
        help="Truncate analytics tables before loading PROD data (platform_users kept).",
    )
    return parser.parse_args()


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )


def main() -> None:
    load_dotenv()
    configure_logging()
    args = parse_args()

    source_url = os.getenv("HAWALA_CONN", "postgresql://postgres:password@localhost:5432/hawala")
    target_url = os.getenv("ANALYTICS_CONN", "postgresql://postgres:password@localhost:5432/analytics_db")

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
