"""
Fix subscriptions.service_id mapping after ETL.

Goal:
- Re-import only subscriptions from hawala.subscribed_clients.
- Resolve service mapping through:
  subscribed_clients.service_subscription_type_id
    -> service_subscription_types.id
    -> service_subscription_types.service_id
    -> analytics services.id (deterministic UUIDv5)

Usage:
  python fix_services_mapping.py --truncate-subscriptions
  python fix_services_mapping.py --dry-run
  python fix_services_mapping.py --batch-size 50000 --limit 100000
"""

from __future__ import annotations

import argparse
import json
import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import bindparam, create_engine, inspect, text
from sqlalchemy.engine import Engine

USER_NS = uuid.UUID("11111111-1111-1111-1111-111111111111")
SUB_NS = uuid.UUID("22222222-2222-2222-2222-222222222222")
SERVICE_NS = uuid.UUID("44444444-4444-4444-4444-444444444444")

SUB_STATUS_MAP = {
    1: "active",
    0: "trial",
    -1: "cancelled",
    -2: "expired",
}


@dataclass
class Metrics:
    read_rows: int = 0
    inserted_rows: int = 0
    skipped_rows: int = 0
    mapped_via_service_id: int = 0
    mapped_via_type_id: int = 0


def log_json(message: str, **kwargs: Any) -> None:
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "message": message,
        **kwargs,
    }
    print(json.dumps(payload, ensure_ascii=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fix subscriptions service mapping in analytics DB")
    parser.add_argument("--batch-size", type=int, default=50000, help="Rows per source chunk")
    parser.add_argument("--limit", type=int, default=None, help="Optional source row limit")
    parser.add_argument("--dry-run", action="store_true", help="Compute only, no target writes")
    parser.add_argument(
        "--truncate-subscriptions",
        action="store_true",
        help="Truncate target subscriptions before re-import",
    )
    return parser.parse_args()


def get_engine(env_var: str, default_url: str) -> Engine:
    url = os.getenv(env_var, default_url)
    return create_engine(url, pool_pre_ping=True)


def parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    return ts.to_pydatetime()


def clean_phone(value: Any) -> str | None:
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


def uuid5(namespace: uuid.UUID, value: str | int | None) -> uuid.UUID:
    raw = "" if value is None else str(value)
    return uuid.uuid5(namespace, raw)


def source_chunks(source_engine: Engine, cols: list[str], batch_size: int, limit: int | None):
    limit_sql = f" LIMIT {limit}" if limit else ""
    sql = f"SELECT {', '.join(cols)} FROM subscribed_clients ORDER BY id{limit_sql}"
    return pd.read_sql_query(sql=text(sql), con=source_engine, chunksize=batch_size)


def fetch_user_map(target_engine: Engine, phones: list[str]) -> dict[str, uuid.UUID]:
    if not phones:
        return {}
    q = text("SELECT phone_number, id FROM users WHERE phone_number IN :phones").bindparams(
        bindparam("phones", expanding=True)
    )
    with target_engine.connect() as conn:
        rows = conn.execute(q, {"phones": phones}).fetchall()
    return {r.phone_number: r.id for r in rows}


def preflight(source_engine: Engine, target_engine: Engine) -> None:
    src = set(inspect(source_engine).get_table_names())
    tgt = set(inspect(target_engine).get_table_names())

    required_src = {"subscribed_clients", "service_subscription_types"}
    required_tgt = {"users", "services", "subscriptions"}

    missing_src = sorted(required_src - src)
    missing_tgt = sorted(required_tgt - tgt)

    if missing_src:
        raise RuntimeError(f"Missing source tables: {missing_src}")
    if missing_tgt:
        raise RuntimeError(f"Missing target tables: {missing_tgt}")


def load_service_mappings(source_engine: Engine, target_engine: Engine) -> tuple[dict[int, uuid.UUID], dict[int, int]]:
    with source_engine.connect() as conn:
        src_services = conn.execute(text("SELECT id FROM services")).fetchall()
        type_rows = conn.execute(
            text(
                """
                SELECT id, service_id
                FROM service_subscription_types
                WHERE service_id IS NOT NULL
                """
            )
        ).fetchall()

    services_by_source_id: dict[int, uuid.UUID] = {}
    for r in src_services:
        source_service_id = int(r.id)
        services_by_source_id[source_service_id] = uuid5(SERVICE_NS, f"service:{source_service_id}")

    source_service_by_subscription_type_id: dict[int, int] = {}
    for r in type_rows:
        source_service_by_subscription_type_id[int(r.id)] = int(r.service_id)

    with target_engine.connect() as conn:
        existing_service_ids = {r.id for r in conn.execute(text("SELECT id FROM services")).fetchall()}

    services_by_source_id = {
        src_id: svc_uuid
        for src_id, svc_uuid in services_by_source_id.items()
        if svc_uuid in existing_service_ids
    }

    return services_by_source_id, source_service_by_subscription_type_id


def maybe_truncate_subscriptions(target_engine: Engine, dry_run: bool) -> None:
    if dry_run:
        log_json("truncate_skipped", reason="dry_run")
        return
    with target_engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE subscriptions RESTART IDENTITY CASCADE"))
    log_json("truncate_done", table="subscriptions")


def run_fix(source_engine: Engine, target_engine: Engine, args: argparse.Namespace) -> Metrics:
    metrics = Metrics()

    src_cols = {c["name"] for c in inspect(source_engine).get_columns("subscribed_clients")}
    cols = ["id", "phone_number", "status", "subscription_start_date", "subscription_end_date"]
    for opt_col in ["service_id", "service_subscription_type_id"]:
        if opt_col in src_cols:
            cols.append(opt_col)

    services_by_source_id, source_service_by_type_id = load_service_mappings(source_engine, target_engine)

    log_json(
        "mapping_loaded",
        services_by_source_id=len(services_by_source_id),
        type_to_service=len(source_service_by_type_id),
    )

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

    total_sql = "SELECT COUNT(*) FROM subscribed_clients"
    if args.limit:
        total = args.limit
    else:
        with source_engine.connect() as conn:
            total = int(conn.execute(text(total_sql)).scalar() or 0)

    log_json("step_start", step="subscriptions_fix", total_source_rows=total, dry_run=args.dry_run)

    for chunk in source_chunks(source_engine, cols, args.batch_size, args.limit):
        phones = [clean_phone(v) for v in chunk["phone_number"].tolist()]
        user_map = fetch_user_map(target_engine, [p for p in phones if p])

        rows: list[dict[str, Any]] = []
        for rec in chunk.itertuples(index=False):
            metrics.read_rows += 1

            source_client_id = int(getattr(rec, "id"))
            source_status = int(getattr(rec, "status", 0) or 0)

            phone = clean_phone(getattr(rec, "phone_number", None))
            user_id = user_map.get(phone) if phone else None
            if not user_id:
                metrics.skipped_rows += 1
                continue

            raw_source_service_id = getattr(rec, "service_id", None)
            raw_source_type_id = getattr(rec, "service_subscription_type_id", None)
            source_service_id = int(raw_source_service_id) if raw_source_service_id is not None else None
            source_type_id = int(raw_source_type_id) if raw_source_type_id is not None else None

            target_service_id = None
            if source_service_id is not None:
                target_service_id = services_by_source_id.get(source_service_id)
                if target_service_id is not None:
                    metrics.mapped_via_service_id += 1

            if target_service_id is None and source_type_id is not None:
                source_service_from_type = source_service_by_type_id.get(source_type_id)
                if source_service_from_type is not None:
                    target_service_id = services_by_source_id.get(source_service_from_type)
                    if target_service_id is not None:
                        metrics.mapped_via_type_id += 1

            if target_service_id is None:
                metrics.skipped_rows += 1
                continue

            start_date = parse_dt(getattr(rec, "subscription_start_date", None))
            if start_date is None:
                start_date = datetime.now(timezone.utc)
            end_date = parse_dt(getattr(rec, "subscription_end_date", None))

            rows.append(
                {
                    "id": uuid5(SUB_NS, f"sub:{source_client_id}"),
                    "user_id": user_id,
                    "service_id": target_service_id,
                    "subscription_start_date": start_date,
                    "subscription_end_date": end_date,
                    "status": SUB_STATUS_MAP.get(source_status, "trial"),
                }
            )

        if rows and not args.dry_run:
            with target_engine.begin() as conn:
                conn.execute(upsert_sql, rows)

        metrics.inserted_rows += len(rows)

        if metrics.read_rows % max(args.batch_size, 1) == 0:
            log_json(
                "progress",
                read_rows=metrics.read_rows,
                upserted_rows=metrics.inserted_rows,
                skipped_rows=metrics.skipped_rows,
            )

    log_json(
        "step_done",
        step="subscriptions_fix",
        read_rows=metrics.read_rows,
        upserted_rows=metrics.inserted_rows,
        skipped_rows=metrics.skipped_rows,
        mapped_via_service_id=metrics.mapped_via_service_id,
        mapped_via_type_id=metrics.mapped_via_type_id,
        dry_run=args.dry_run,
    )
    return metrics


def main() -> None:
    load_dotenv()
    started = time.time()

    args = parse_args()

    source_engine = get_engine("HAWALA_CONN", "postgresql://postgres:password@localhost:5432/hawala")
    target_engine = get_engine("ANALYTICS_CONN", "postgresql://postgres:password@localhost:5432/analytics_db")

    preflight(source_engine, target_engine)

    if args.truncate_subscriptions:
        maybe_truncate_subscriptions(target_engine, args.dry_run)

    run_fix(source_engine, target_engine, args)

    elapsed = round(time.time() - started, 2)
    log_json("fix_done", duration_sec=elapsed)


if __name__ == "__main__":
    main()
