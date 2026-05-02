"""Post-fix verification for prod_db -> analytics data pipeline."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

DATA_START_DATE = "2025-09-01"


def _load_env() -> None:
    script_dir = Path(__file__).resolve().parent
    backend_env = script_dir.parent / ".env"
    root_env = script_dir.parent.parent / ".env"

    if backend_env.exists():
        load_dotenv(backend_env)
    if root_env.exists():
        load_dotenv(root_env, override=False)


def _scalar(conn, sql: str, params: dict | None = None):
    return conn.execute(text(sql), params or {}).scalar()


def verify() -> int:
    _load_env()
    PROD_CONN = os.getenv("PROD_CONN", "postgresql://postgres:password@localhost:5432/prod_db")
    analytics_conn = os.getenv("ANALYTICS_CONN", os.getenv("DATABASE_URL", "postgresql://postgres:12345prod_db@localhost:5433/analytics_db"))

    prod_engine = create_engine(PROD_CONN, pool_pre_ping=True)
    analytics_engine = create_engine(analytics_conn, pool_pre_ping=True)

    print("== VERIFY PROD DB ==")
    with prod_engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT MIN(created_at) AS min_d, MAX(created_at) AS max_d, COUNT(*) AS total
                FROM transaction_histories
                """
            )
        ).fetchone()
        print(f"PROD transaction_histories: total={int(row.total or 0)} range={row.min_d} -> {row.max_d}")

    print("\n== VERIFY ANALYTICS DB ==")
    has_error = False
    with analytics_engine.connect() as conn:
        for table in ["billing_events", "user_activities", "subscriptions", "cohorts"]:
            try:
                count = _scalar(conn, f"SELECT COUNT(*) FROM {table}")
                print(f"ANALYTICS {table}: {int(count or 0)} rows")
            except Exception as exc:  # noqa: BLE001
                has_error = True
                print(f"ANALYTICS {table}: ERROR - {exc}")

        filtered_count = _scalar(
            conn,
            """
            SELECT COUNT(*)
            FROM billing_events
            WHERE DATE(event_datetime) >= :start_date
            """,
            {"start_date": DATA_START_DATE},
        )
        print(f"ANALYTICS billing_events with {DATA_START_DATE} filter: {int(filtered_count or 0)} rows")

        if int(filtered_count or 0) == 0:
            has_error = True
            print("WARNING: analytics_db appears empty for the real date window; rerun ETL.")
        else:
            print("OK: analytics_db is populated for the expected data window.")

    return 1 if has_error else 0


if __name__ == "__main__":
    raise SystemExit(verify())


