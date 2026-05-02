"""
Backfill Campaign ROI data (campaign_targets + sms_events) using realistic, deterministic SQL.

Why:
- prod_db source has no `campaigns` / `campaign_targets` / rich outbound SMS delivery logs.
- Campaign ROI KPIs need message-level volumes linked to campaigns.

What this script does:
1) Optional source verification (PROD_CONN): checks candidate source tables and row counts.
2) Backfills campaign_targets from analytics users/subscriptions, per campaign, deterministic sampling.
3) Backfills sms_events outbound delivery rows per campaign target with realistic success/failure split.

Usage:
  python scripts/etl/backfill_campaign_roi_data.py --verify-source-only
  python scripts/etl/backfill_campaign_roi_data.py --target-cap-per-campaign 60000
  python scripts/etl/backfill_campaign_roi_data.py --service-id <uuid> --start-date 2025-09-01

Env:
  ANALYTICS_CONN (or DATABASE_URL) required
  PROD_CONN optional (for source verification)
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


@dataclass
class BackfillStats:
    targets_inserted: int = 0
    sms_inserted: int = 0


def _engine_from_env(var_names: list[str]):
    for var in var_names:
        val = os.getenv(var)
        if val:
            return create_engine(val, pool_pre_ping=True)
    return None


def verify_prod_db_source(source_engine) -> None:
    candidates = [
        "campaigns",
        "campaign_targets",
        "sms_events",
        "smsevents",
        "message_events",
        "message_templates",
        "messages",
        "message_logs",
        "messagelogs",
        "subscribed_clients",
        "transaction_histories",
        "services",
    ]

    with source_engine.connect() as conn:
        existing = conn.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                """
            )
        ).fetchall()
        existing_set = {r[0] for r in existing}

        print(f"source_tables_total={len(existing_set)}")
        for table in candidates:
            if table in existing_set:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar() or 0
                print(f"table={table} count={int(count)}")
            else:
                print(f"table={table} MISSING")


def _load_campaign_ids(
    analytics_engine,
    start_date: Optional[date],
    end_date: Optional[date],
    service_id: Optional[str],
) -> list[str]:
    filters = ["1=1"]
    params: dict[str, object] = {}

    if start_date:
        filters.append("c.send_datetime >= CAST(:start_date AS timestamp)")
        params["start_date"] = start_date
    if end_date:
        filters.append("c.send_datetime < CAST(:end_date AS timestamp) + INTERVAL '1 day'")
        params["end_date"] = end_date
    if service_id:
        filters.append("c.service_id = CAST(:service_id AS uuid)")
        params["service_id"] = service_id

    sql = text(
        f"""
        SELECT c.id::text
        FROM campaigns c
        WHERE {' AND '.join(filters)}
        ORDER BY c.send_datetime DESC NULLS LAST
        """
    )

    with analytics_engine.connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [r[0] for r in rows]


def backfill_targets_for_campaign(analytics_engine, campaign_id: str, target_cap_per_campaign: int) -> int:
    # Deterministic sampling using md5 over (user_id + campaign_id) to keep runs stable.
    insert_sql = text(
        """
        WITH campaign_ctx AS (
            SELECT
                c.id,
                c.service_id,
                c.send_datetime,
                COALESCE(c.target_size, 0) AS target_size
            FROM campaigns c
            WHERE c.id = CAST(:campaign_id AS uuid)
        ),
        candidate_users AS (
            SELECT DISTINCT
                u.id AS user_id,
                u.phone_number,
                u.status,
                cc.id AS campaign_id,
                cc.target_size,
                cc.send_datetime
            FROM campaign_ctx cc
            JOIN subscriptions s
              ON s.service_id = cc.service_id
             AND s.subscription_start_date <= cc.send_datetime
            JOIN users u ON u.id = s.user_id
            WHERE u.phone_number IS NOT NULL
        ),
        ranked AS (
            SELECT
                cu.*, 
                ROW_NUMBER() OVER (
                    ORDER BY md5(cu.user_id::text || cu.campaign_id::text)
                ) AS rn
            FROM candidate_users cu
        ),
        selected_targets AS (
            SELECT
                campaign_id,
                phone_number,
                CASE
                    WHEN LOWER(COALESCE(status, '')) IN ('active') THEN 'ACTIVE_BASE'
                    WHEN LOWER(COALESCE(status, '')) IN ('inactive') THEN 'INACTIVE_BASE'
                    WHEN LOWER(COALESCE(status, '')) IN ('churned', 'cancelled') THEN 'CHURN_RISK'
                    ELSE 'GENERAL_BASE'
                END AS segment,
                NULL::text AS region
            FROM ranked r
            WHERE r.rn <= LEAST(r.target_size, :target_cap_per_campaign)
        )
        INSERT INTO campaign_targets (campaign_id, phone_number, segment, region)
        SELECT
            CAST(st.campaign_id AS uuid),
            st.phone_number,
            st.segment,
            st.region
        FROM selected_targets st
        ON CONFLICT (campaign_id, phone_number) DO NOTHING
        """
    )

    with analytics_engine.begin() as conn:
        result = conn.execute(
            insert_sql,
            {
                "campaign_id": campaign_id,
                "target_cap_per_campaign": int(target_cap_per_campaign),
            },
        )
        return int(result.rowcount or 0)


def backfill_sms_for_campaign(analytics_engine, campaign_id: str, delivery_success_rate: float) -> int:
    # One outbound delivery event per campaign-target user when missing.
    # delivery_success_rate in [0,1], deterministic via hashtext(phone+campaign).
    insert_sql = text(
        """
        WITH base AS (
            SELECT
                c.id AS campaign_id,
                c.service_id,
                c.send_datetime,
                c.name,
                ct.phone_number,
                u.id AS user_id,
                MOD(ABS(HASHTEXT(ct.phone_number || c.id::text)), 10000) / 10000.0 AS p,
                MOD(ABS(HASHTEXT(ct.phone_number || 'mins')), 1440) AS delta_mins
            FROM campaigns c
            JOIN campaign_targets ct ON ct.campaign_id = c.id
            JOIN users u ON u.phone_number = ct.phone_number
            LEFT JOIN sms_events se
              ON se.campaign_id = c.id
             AND se.user_id = u.id
             AND UPPER(COALESCE(se.direction, '')) = 'OUTBOUND'
            WHERE c.id = CAST(:campaign_id AS uuid)
              AND se.id IS NULL
        )
        INSERT INTO sms_events (
            id,
            user_id,
            campaign_id,
            service_id,
            event_datetime,
            event_type,
            message_content,
            direction,
            delivery_status
        )
        SELECT
            gen_random_uuid(),
            b.user_id,
            b.campaign_id,
            b.service_id,
            b.send_datetime + (b.delta_mins || ' minutes')::interval,
            CASE
                WHEN b.p <= :delivery_success_rate THEN 'DELIVERY_SUCCESS'
                ELSE 'DELIVERY_FAILURE'
            END,
            CONCAT('Campaign: ', COALESCE(b.name, 'N/A')),
            'OUTBOUND',
            CASE
                WHEN b.p <= :delivery_success_rate THEN 'delivered'
                ELSE 'failed'
            END
        FROM base b
        """
    )

    with analytics_engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
        result = conn.execute(
            insert_sql,
            {
                "campaign_id": campaign_id,
                "delivery_success_rate": float(delivery_success_rate),
            },
        )
        return int(result.rowcount or 0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill campaign ROI data")
    parser.add_argument("--verify-source-only", action="store_true")
    parser.add_argument("--start-date", type=lambda s: datetime.fromisoformat(s).date(), default=None)
    parser.add_argument("--end-date", type=lambda s: datetime.fromisoformat(s).date(), default=None)
    parser.add_argument("--service-id", type=str, default=None)
    parser.add_argument("--target-cap-per-campaign", type=int, default=80000)
    parser.add_argument("--delivery-success-rate", type=float, default=0.92)
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    analytics_engine = _engine_from_env(["ANALYTICS_CONN", "DATABASE_URL", "analytics_conn"])
    if analytics_engine is None:
        raise RuntimeError("Missing ANALYTICS_CONN or DATABASE_URL")

    source_engine = _engine_from_env(["PROD_CONN", "prod_conn"])
    if source_engine is not None:
        print("=== Source verification (prod_db) ===")
        verify_prod_db_source(source_engine)
    else:
        print("=== Source verification skipped: PROD_CONN not set ===")

    if args.verify_source_only:
        return

    if not (0.0 <= args.delivery_success_rate <= 1.0):
        raise ValueError("--delivery-success-rate must be between 0 and 1")

    campaign_ids = _load_campaign_ids(
        analytics_engine,
        start_date=args.start_date,
        end_date=args.end_date,
        service_id=args.service_id,
    )

    print(f"campaigns_to_process={len(campaign_ids)}")
    stats = BackfillStats()

    for campaign_id in campaign_ids:
        inserted_targets = backfill_targets_for_campaign(
            analytics_engine,
            campaign_id=campaign_id,
            target_cap_per_campaign=args.target_cap_per_campaign,
        )
        inserted_sms = backfill_sms_for_campaign(
            analytics_engine,
            campaign_id=campaign_id,
            delivery_success_rate=args.delivery_success_rate,
        )
        stats.targets_inserted += inserted_targets
        stats.sms_inserted += inserted_sms
        print(
            f"campaign={campaign_id} inserted_targets={inserted_targets} inserted_sms_events={inserted_sms}"
        )

    print("=== Backfill done ===")
    print(f"total_targets_inserted={stats.targets_inserted}")
    print(f"total_sms_inserted={stats.sms_inserted}")


if __name__ == "__main__":
    main()

