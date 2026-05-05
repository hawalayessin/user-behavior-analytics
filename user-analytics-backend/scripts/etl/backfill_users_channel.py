"""
Backfill users.channel from prod_db.subscribed_clients.channel.

Usage:
  python scripts/etl/backfill_users_channel.py --batch-size 50000
  python scripts/etl/backfill_users_channel.py --batch-size 50000 --limit 100000
  python scripts/etl/backfill_users_channel.py --dry-run

Environment variables:
  PROD_CONN       Source PostgreSQL connection URL
  ANALYTICS_CONN  Target PostgreSQL connection URL
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from psycopg2.extras import execute_values
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine


def log_json(message: str, **kwargs: Any) -> None:
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "message": message,
        **kwargs,
    }
    print(json.dumps(payload, ensure_ascii=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill users.channel from prod_db subscribed_clients")
    parser.add_argument("--batch-size", type=int, default=50000, help="Rows per source chunk")
    parser.add_argument("--update-batch-size", type=int, default=5000, help="Rows per update batch")
    parser.add_argument("--limit", type=int, default=None, help="Optional source row limit")
    parser.add_argument("--dry-run", action="store_true", help="Compute only, no target writes")
    return parser.parse_args()


def get_engine(env_var: str, default_url: str) -> Engine:
    url = os.getenv(env_var, default_url)
    return create_engine(url, pool_pre_ping=True)


def clean_phone(value: Any) -> str | None:
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


def normalize_channel(value: Any) -> str | None:
    if value is None:
        return None
    raw = str(value).strip().lower()
    if not raw:
        return None
    if raw in {"ussd", "*1589", "*159#", "menu"}:
        return "USSD"
    if "ussd" in raw or "*159" in raw or "*1589" in raw:
        return "USSD"
    return "WEB"


@dataclass
class Metrics:
    read_rows: int = 0
    updated_rows: int = 0
    skipped_rows: int = 0


def preflight(source_engine: Engine, target_engine: Engine) -> None:
    src = set(inspect(source_engine).get_table_names())
    tgt = set(inspect(target_engine).get_table_names())

    required_src = {"subscribed_clients"}
    required_tgt = {"users"}

    missing_src = sorted(required_src - src)
    missing_tgt = sorted(required_tgt - tgt)

    if missing_src:
        raise RuntimeError(f"Missing source tables: {missing_src}")
    if missing_tgt:
        raise RuntimeError(f"Missing target tables: {missing_tgt}")

    src_cols = {c["name"] for c in inspect(source_engine).get_columns("subscribed_clients")}
    if "channel" not in src_cols:
        raise RuntimeError("Source table subscribed_clients is missing column: channel")

    tgt_cols = {c["name"] for c in inspect(target_engine).get_columns("users")}
    if "channel" not in tgt_cols:
        raise RuntimeError("Target table users is missing column: channel")


def source_chunks(source_engine: Engine, cols: list[str], batch_size: int, limit: int | None):
    limit_sql = f" LIMIT {limit}" if limit else ""
    sql = f"SELECT {', '.join(cols)} FROM subscribed_clients ORDER BY id{limit_sql}"
    return pd.read_sql_query(sql=text(sql), con=source_engine, chunksize=batch_size)


def run_backfill(source_engine: Engine, target_engine: Engine, args: argparse.Namespace) -> Metrics:
    metrics = Metrics()

    cols = ["id", "phone_number", "channel"]
    update_sql = text(
        """
        UPDATE users AS u
        SET channel = CASE
            WHEN u.channel IS NULL THEN t.channel
            WHEN u.channel != 'USSD' AND t.channel = 'USSD' THEN 'USSD'
            ELSE u.channel
        END
        FROM tmp_user_channel AS t
        WHERE u.phone_number = t.phone_number
          AND (
            u.channel IS NULL
            OR (u.channel != 'USSD' AND t.channel = 'USSD')
          )
        """
    )

    log_json("backfill_start", batch_size=args.batch_size, limit=args.limit, dry_run=args.dry_run)

    for chunk in source_chunks(source_engine, cols, args.batch_size, args.limit):
        channel_by_phone: dict[str, str] = {}
        for rec in chunk.itertuples(index=False):
            metrics.read_rows += 1
            phone = clean_phone(getattr(rec, "phone_number", None))
            channel = normalize_channel(getattr(rec, "channel", None))

            if not phone or not channel:
                metrics.skipped_rows += 1
                continue

            existing = channel_by_phone.get(phone)
            if existing == "USSD":
                continue
            if channel == "USSD" or existing is None:
                channel_by_phone[phone] = channel

        rows = [(phone, chan) for phone, chan in channel_by_phone.items()]

        if rows and not args.dry_run:
            with target_engine.begin() as conn:
                raw_conn = conn.connection
                cursor = raw_conn.cursor()
                cursor.execute(
                    "CREATE TEMP TABLE tmp_user_channel (phone_number text, channel text) ON COMMIT DROP"
                )
                execute_values(
                    cursor,
                    "INSERT INTO tmp_user_channel (phone_number, channel) VALUES %s",
                    rows,
                    page_size=args.update_batch_size,
                )
                conn.execute(update_sql)
        metrics.updated_rows += len(rows)

    log_json(
        "backfill_done",
        read_rows=metrics.read_rows,
        updated_rows=metrics.updated_rows,
        skipped_rows=metrics.skipped_rows,
    )
    return metrics


def main() -> None:
    load_dotenv()
    args = parse_args()

    source_engine = get_engine("PROD_CONN", "postgresql://postgres:password@localhost:5432/prod_db")
    target_engine = get_engine("ANALYTICS_CONN", "postgresql://postgres:password@localhost:5432/analytics_db")

    preflight(source_engine, target_engine)
    run_backfill(source_engine, target_engine, args)


if __name__ == "__main__":
    main()
