"""
Seed missing analytics data after ETL from production.
Fills: user_activities, cohorts, unsubscriptions, sms_events, campaigns
Updates: users.last_activity_at

Usage:
  python seed_missing_data.py
  python seed_missing_data.py --dry-run
  python seed_missing_data.py --step user_activities
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from faker import Faker
from sqlalchemy import bindparam, create_engine, text
from sqlalchemy.engine import Engine
from tqdm import tqdm


BATCH_SIZE = 10_000
faker = Faker("fr_FR")


@dataclass
class SeedMetrics:
    read_rows: int = 0
    inserted_rows: int = 0
    skipped_rows: int = 0


def log_json(message: str, **kwargs: Any) -> None:
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "message": message,
        **kwargs,
    }
    print(json.dumps(payload, ensure_ascii=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed missing analytics data")
    parser.add_argument("--dry-run", action="store_true", help="Compute and log only, no DB write")
    parser.add_argument(
        "--step",
        default="all",
        choices=[
            "all",
            "fix_last_activity_at",
            "campaigns",
            "user_activities",
            "cohorts",
            "unsubscriptions",
            "sms_events",
        ],
        help="Run only one step",
    )
    parser.add_argument("--activities", type=int, default=500_000, help="Number of user_activities to generate")
    parser.add_argument("--sms", type=int, default=100_000, help="Number of sms_events to generate")
    parser.add_argument("--campaigns", type=int, default=20, help="Number of campaigns to generate")
    return parser.parse_args()


def get_engine() -> Engine:
    analytics_conn = os.getenv("ANALYTICS_CONN")
    if not analytics_conn:
        raise RuntimeError("ANALYTICS_CONN is required in environment/.env")
    return create_engine(analytics_conn, pool_pre_ping=True)


def random_peak_datetime(last_n_days: int) -> datetime:
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=last_n_days)

    # Bias toward weekdays with telecom usage peaks around 8-12 and 18-22.
    for _ in range(20):
        day = start + timedelta(days=random.randint(0, max(last_n_days - 1, 0)))
        if day.weekday() <= 4 and random.random() < 0.75:
            peak_hour = random.choices(
                population=[8, 9, 10, 11, 18, 19, 20, 21],
                weights=[12, 13, 12, 11, 12, 14, 14, 12],
                k=1,
            )[0]
        else:
            peak_hour = random.randint(7, 23)

        dt = day.replace(
            hour=peak_hour,
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
            microsecond=0,
        )
        if dt <= now:
            return dt

    return now - timedelta(hours=1)


def execute_batch(conn, stmt, rows: list[dict[str, Any]], dry_run: bool) -> int:
    if not rows:
        return 0
    if dry_run:
        return len(rows)
    conn.execute(stmt, rows)
    return len(rows)


def fix_last_activity_at(engine: Engine, dry_run: bool) -> SeedMetrics:
    metrics = SeedMetrics()
    log_json("step_start", step="fix_last_activity_at")

    sql_count = text(
        """
        WITH be AS (
            SELECT user_id, MAX(event_datetime) AS last_be
            FROM billing_events
            GROUP BY user_id
        ),
        sb AS (
            SELECT user_id, MAX(subscription_start_date) AS last_sub
            FROM subscriptions
            GROUP BY user_id
        )
        SELECT COUNT(*)
        FROM users u
        LEFT JOIN be ON be.user_id = u.id
        LEFT JOIN sb ON sb.user_id = u.id
        WHERE u.status = 'active'
          AND (
                u.last_activity_at IS NULL
             OR u.last_activity_at < COALESCE(be.last_be, sb.last_sub, NOW() - INTERVAL '30 days')
          )
        """
    )

    sql_update = text(
        """
        WITH be AS (
            SELECT user_id, MAX(event_datetime) AS last_be
            FROM billing_events
            GROUP BY user_id
        ),
        sb AS (
            SELECT user_id, MAX(subscription_start_date) AS last_sub
            FROM subscriptions
            GROUP BY user_id
        ),
        src AS (
            SELECT
                u.id AS user_id,
                LEAST(
                    NOW(),
                    COALESCE(
                        be.last_be,
                        sb.last_sub + ((FLOOR(random() * 20) + 1)::text || ' days')::interval +
                                      ((FLOOR(random() * 18) + 6)::text || ' hours')::interval,
                        NOW() - INTERVAL '15 days'
                    )
                ) AS new_last_activity
            FROM users u
            LEFT JOIN be ON be.user_id = u.id
            LEFT JOIN sb ON sb.user_id = u.id
            WHERE u.status = 'active'
        )
        UPDATE users u
        SET last_activity_at = src.new_last_activity
        FROM src
        WHERE u.id = src.user_id
          AND (u.last_activity_at IS NULL OR u.last_activity_at <> src.new_last_activity)
        """
    )

    with engine.begin() as conn:
        metrics.read_rows = int(conn.execute(sql_count).scalar() or 0)
        if not dry_run:
            result = conn.execute(sql_update)
            metrics.inserted_rows = int(result.rowcount or 0)
        else:
            metrics.inserted_rows = metrics.read_rows

    log_json(
        "step_done",
        step="fix_last_activity_at",
        candidate_rows=metrics.read_rows,
        updated_rows=metrics.inserted_rows,
        dry_run=dry_run,
    )
    return metrics


def seed_campaigns(engine: Engine, n: int, dry_run: bool) -> SeedMetrics:
    metrics = SeedMetrics()
    log_json("step_start", step="campaigns", target=n)

    with engine.begin() as conn:
        services = conn.execute(text("SELECT id, name FROM services ORDER BY name")).fetchall()
        if not services:
            log_json("step_done", step="campaigns", inserted_rows=0, skipped_rows=n, reason="no_services")
            return metrics

        campaign_types = ["retention", "reactivation", "promotion", "welcome"]
        statuses = ["completed", "sent", "scheduled"]

        stmt = text(
            """
            INSERT INTO campaigns (
                id, name, description, service_id, send_datetime,
                target_size, cost, campaign_type, status, created_at
            ) VALUES (
                :id, :name, :description, :service_id, :send_datetime,
                :target_size, :cost, :campaign_type, :status, :created_at
            )
            ON CONFLICT (id) DO NOTHING
            """
        )

        rows: list[dict[str, Any]] = []
        now = datetime.now(timezone.utc)
        for idx in range(n):
            svc = random.choice(services)
            send_dt = now - timedelta(days=random.randint(1, 180), hours=random.randint(0, 23))
            target_size = random.randint(8_000, 80_000)
            cost = (Decimal(target_size) * Decimal("0.035")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            rows.append(
                {
                    "id": uuid.uuid4(),
                    "name": f"{random.choice(['Campagne', 'Push', 'Promo'])} {svc.name} {idx+1}",
                    "description": faker.sentence(nb_words=12),
                    "service_id": svc.id,
                    "send_datetime": send_dt,
                    "target_size": target_size,
                    "cost": cost,
                    "campaign_type": random.choice(campaign_types),
                    "status": random.choice(statuses),
                    "created_at": send_dt - timedelta(days=random.randint(1, 10)),
                }
            )

            if len(rows) >= BATCH_SIZE:
                metrics.inserted_rows += execute_batch(conn, stmt, rows, dry_run)
                rows.clear()

        metrics.inserted_rows += execute_batch(conn, stmt, rows, dry_run)

    log_json("step_done", step="campaigns", inserted_rows=metrics.inserted_rows, dry_run=dry_run)
    return metrics


def seed_user_activities(engine: Engine, n: int, dry_run: bool) -> SeedMetrics:
    metrics = SeedMetrics()
    log_json("step_start", step="user_activities", target=n)

    activity_types = ["subscription", "renewal", "content_view", "login", "billing"]

    with engine.begin() as conn:
        active_rows = conn.execute(
            text(
                """
                SELECT u.id AS user_id, s.service_id
                FROM users u
                JOIN LATERAL (
                    SELECT service_id
                    FROM subscriptions su
                    WHERE su.user_id = u.id
                    ORDER BY su.subscription_start_date DESC
                    LIMIT 1
                ) s ON TRUE
                WHERE u.status = 'active'
                """
            )
        ).fetchall()

        inactive_rows = conn.execute(
            text(
                """
                SELECT u.id AS user_id, s.service_id
                FROM users u
                JOIN LATERAL (
                    SELECT service_id
                    FROM subscriptions su
                    WHERE su.user_id = u.id
                    ORDER BY su.subscription_start_date DESC
                    LIMIT 1
                ) s ON TRUE
                WHERE u.status = 'inactive'
                ORDER BY random()
                LIMIT 300000
                """
            )
        ).fetchall()

        if not active_rows and not inactive_rows:
            log_json("step_done", step="user_activities", inserted_rows=0, reason="no_user_pool")
            return metrics

        metrics.read_rows = len(active_rows) + len(inactive_rows)

        stmt = text(
            """
            INSERT INTO user_activities (
                id, user_id, service_id, activity_datetime, activity_type, session_id
            ) VALUES (
                :id, :user_id, :service_id, :activity_datetime, :activity_type, :session_id
            )
            ON CONFLICT (id) DO NOTHING
            """
        )

        rows: list[dict[str, Any]] = []
        pbar = tqdm(total=n, desc="seed_user_activities", unit="rows")

        for _ in range(n):
            use_active = random.random() < 0.70
            pool = active_rows if use_active and active_rows else inactive_rows
            if not pool:
                pool = active_rows
            user = random.choice(pool)
            dt = random_peak_datetime(90)

            rows.append(
                {
                    "id": uuid.uuid4(),
                    "user_id": user.user_id,
                    "service_id": user.service_id,
                    "activity_datetime": dt,
                    "activity_type": random.choices(
                        population=activity_types,
                        weights=[8, 20, 42, 20, 10],
                        k=1,
                    )[0],
                    "session_id": str(uuid.uuid4()) if random.random() < 0.85 else None,
                }
            )

            if len(rows) >= BATCH_SIZE:
                metrics.inserted_rows += execute_batch(conn, stmt, rows, dry_run)
                rows.clear()
                pbar.update(BATCH_SIZE)

        if rows:
            inserted = execute_batch(conn, stmt, rows, dry_run)
            metrics.inserted_rows += inserted
            pbar.update(len(rows))

        pbar.close()

    log_json("step_done", step="user_activities", inserted_rows=metrics.inserted_rows, dry_run=dry_run)
    return metrics


def compute_and_insert_cohorts(engine: Engine, dry_run: bool) -> SeedMetrics:
    metrics = SeedMetrics()
    log_json("step_start", step="cohorts")

    sql_count = text(
        """
        WITH first_paid AS (
            SELECT DISTINCT ON (user_id, service_id)
                user_id,
                service_id,
                subscription_start_date AS first_paid_date
            FROM subscriptions
            WHERE status IN ('active', 'cancelled', 'expired')
            ORDER BY user_id, service_id, subscription_start_date ASC
        )
        SELECT COUNT(*)
        FROM (
            SELECT date_trunc('month', first_paid_date)::date AS cohort_date, service_id
            FROM first_paid
            GROUP BY 1, 2
        ) q
        """
    )

    sql_insert = text(
        """
        WITH first_paid AS (
            SELECT DISTINCT ON (user_id, service_id)
                user_id,
                service_id,
                subscription_start_date AS first_paid_date
            FROM subscriptions
            WHERE status IN ('active', 'cancelled', 'expired')
            ORDER BY user_id, service_id, subscription_start_date ASC
        ),
        cohort_base AS (
            SELECT
                date_trunc('month', fp.first_paid_date)::date AS cohort_date,
                fp.service_id,
                COUNT(*) AS total_users
            FROM first_paid fp
            GROUP BY 1, 2
        ),
        retention_calc AS (
            SELECT
                date_trunc('month', fp.first_paid_date)::date AS cohort_date,
                fp.service_id,
                COUNT(*) FILTER (
                    WHERE EXISTS (
                        SELECT 1
                        FROM subscriptions s2
                        WHERE s2.user_id = fp.user_id
                          AND s2.service_id = fp.service_id
                          AND s2.subscription_start_date <= fp.first_paid_date + INTERVAL '7 days'
                          AND COALESCE(s2.subscription_end_date, 'infinity'::timestamp) >= fp.first_paid_date + INTERVAL '7 days'
                    )
                ) AS active_d7,
                COUNT(*) FILTER (
                    WHERE EXISTS (
                        SELECT 1
                        FROM subscriptions s2
                        WHERE s2.user_id = fp.user_id
                          AND s2.service_id = fp.service_id
                          AND s2.subscription_start_date <= fp.first_paid_date + INTERVAL '14 days'
                          AND COALESCE(s2.subscription_end_date, 'infinity'::timestamp) >= fp.first_paid_date + INTERVAL '14 days'
                    )
                ) AS active_d14,
                COUNT(*) FILTER (
                    WHERE EXISTS (
                        SELECT 1
                        FROM subscriptions s2
                        WHERE s2.user_id = fp.user_id
                          AND s2.service_id = fp.service_id
                          AND s2.subscription_start_date <= fp.first_paid_date + INTERVAL '30 days'
                          AND COALESCE(s2.subscription_end_date, 'infinity'::timestamp) >= fp.first_paid_date + INTERVAL '30 days'
                    )
                ) AS active_d30
            FROM first_paid fp
            GROUP BY 1, 2
        )
        INSERT INTO cohorts (
            id, cohort_date, service_id, total_users,
            retention_d7, retention_d14, retention_d30, calculated_at
        )
        SELECT
            gen_random_uuid(),
            cb.cohort_date,
            cb.service_id,
            cb.total_users,
            ROUND(100.0 * COALESCE(rc.active_d7, 0) / NULLIF(cb.total_users, 0), 2),
            ROUND(100.0 * COALESCE(rc.active_d14, 0) / NULLIF(cb.total_users, 0), 2),
            ROUND(100.0 * COALESCE(rc.active_d30, 0) / NULLIF(cb.total_users, 0), 2),
            NOW()
        FROM cohort_base cb
        LEFT JOIN retention_calc rc
            ON rc.cohort_date = cb.cohort_date
           AND rc.service_id = cb.service_id
        ON CONFLICT (cohort_date, service_id) DO NOTHING
        """
    )

    with engine.begin() as conn:
        metrics.read_rows = int(conn.execute(sql_count).scalar() or 0)
        if not dry_run:
            res = conn.execute(sql_insert)
            metrics.inserted_rows = int(res.rowcount or 0)
        else:
            metrics.inserted_rows = metrics.read_rows

    log_json("step_done", step="cohorts", candidate_rows=metrics.read_rows, inserted_rows=metrics.inserted_rows, dry_run=dry_run)
    return metrics


def derive_unsubscriptions(engine: Engine, dry_run: bool) -> SeedMetrics:
    metrics = SeedMetrics()
    log_json("step_start", step="unsubscriptions")

    with engine.begin() as conn:
        total = int(
            conn.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM subscriptions s
                    WHERE s.status IN ('cancelled', 'expired')
                    """
                )
            ).scalar()
            or 0
        )
        metrics.read_rows = total

        select_sql = text(
            """
            SELECT
                s.id AS subscription_id,
                s.user_id,
                s.service_id,
                s.subscription_start_date,
                COALESCE(s.subscription_end_date, s.subscription_start_date + INTERVAL '3 days') AS unsub_dt,
                s.status,
                (
                    SELECT be.id
                    FROM billing_events be
                    WHERE be.subscription_id = s.id
                    ORDER BY be.event_datetime DESC
                    LIMIT 1
                ) AS last_billing_event_id
            FROM subscriptions s
            WHERE s.status IN ('cancelled', 'expired')
            ORDER BY s.subscription_start_date
            LIMIT :limit OFFSET :offset
            """
        )

        insert_sql = text(
            """
            INSERT INTO unsubscriptions (
                id, subscription_id, user_id, service_id, unsubscription_datetime,
                churn_type, churn_reason, days_since_subscription, last_billing_event_id
            ) VALUES (
                :id, :subscription_id, :user_id, :service_id, :unsubscription_datetime,
                :churn_type, :churn_reason, :days_since_subscription, :last_billing_event_id
            )
            ON CONFLICT (subscription_id) DO NOTHING
            """
        )

        pbar = tqdm(total=total, desc="derive_unsubscriptions", unit="rows")
        offset = 0
        while offset < total:
            chunk = conn.execute(select_sql, {"limit": BATCH_SIZE, "offset": offset}).fetchall()
            if not chunk:
                break

            rows: list[dict[str, Any]] = []
            for rec in chunk:
                days_since = int(max((rec.unsub_dt - rec.subscription_start_date).days, 0))
                if rec.status == "expired":
                    churn_type = "TECHNICAL"
                    churn_reason = random.choices(
                        ["BILLING_FAILED", "NO_RENEWAL"],
                        weights=[65, 35],
                        k=1,
                    )[0]
                else:
                    churn_type = "VOLUNTARY"
                    churn_reason = random.choices(
                        ["PRICE_TOO_HIGH", "NOT_SATISFIED"],
                        weights=[45, 55],
                        k=1,
                    )[0]

                rows.append(
                    {
                        "id": uuid.uuid4(),
                        "subscription_id": rec.subscription_id,
                        "user_id": rec.user_id,
                        "service_id": rec.service_id,
                        "unsubscription_datetime": rec.unsub_dt,
                        "churn_type": churn_type,
                        "churn_reason": churn_reason,
                        "days_since_subscription": days_since,
                        "last_billing_event_id": rec.last_billing_event_id,
                    }
                )

            metrics.inserted_rows += execute_batch(conn, insert_sql, rows, dry_run)
            offset += len(chunk)
            pbar.update(len(chunk))

        pbar.close()

    log_json(
        "step_done",
        step="unsubscriptions",
        candidate_rows=metrics.read_rows,
        inserted_rows=metrics.inserted_rows,
        dry_run=dry_run,
    )
    return metrics


def seed_sms_events(engine: Engine, n: int, dry_run: bool) -> SeedMetrics:
    metrics = SeedMetrics()
    log_json("step_start", step="sms_events", target=n)

    event_types = [
        "subscription_confirm",
        "renewal_reminder",
        "billing_failed",
        "unsubscription_confirm",
    ]

    with engine.begin() as conn:
        user_service_pool = conn.execute(
            text(
                """
                SELECT DISTINCT ON (u.id)
                    u.id AS user_id,
                    s.service_id
                FROM users u
                JOIN subscriptions s ON s.user_id = u.id
                ORDER BY u.id, s.subscription_start_date DESC
                LIMIT 400000
                """
            )
        ).fetchall()

        campaign_ids = [r.id for r in conn.execute(text("SELECT id FROM campaigns ORDER BY send_datetime DESC LIMIT 200")).fetchall()]

        if not user_service_pool:
            log_json("step_done", step="sms_events", inserted_rows=0, reason="no_user_pool")
            return metrics

        metrics.read_rows = len(user_service_pool)

        stmt = text(
            """
            INSERT INTO sms_events (
                id, user_id, campaign_id, service_id, event_datetime,
                event_type, message_content, direction, delivery_status
            ) VALUES (
                :id, :user_id, :campaign_id, :service_id, :event_datetime,
                :event_type, :message_content, :direction, :delivery_status
            )
            ON CONFLICT (id) DO NOTHING
            """
        )

        rows: list[dict[str, Any]] = []
        pbar = tqdm(total=n, desc="seed_sms_events", unit="rows")

        for _ in range(n):
            us = random.choice(user_service_pool)
            direction = "outbound" if random.random() < 0.80 else "inbound"
            delivery_status = random.choices(
                ["delivered", "failed", "pending"],
                weights=[85, 10, 5],
                k=1,
            )[0]

            rows.append(
                {
                    "id": uuid.uuid4(),
                    "user_id": us.user_id,
                    "campaign_id": random.choice(campaign_ids) if campaign_ids and random.random() < 0.65 else None,
                    "service_id": us.service_id,
                    "event_datetime": random_peak_datetime(90),
                    "event_type": random.choice(event_types),
                    "message_content": faker.sentence(nb_words=10),
                    "direction": direction,
                    "delivery_status": delivery_status,
                }
            )

            if len(rows) >= BATCH_SIZE:
                metrics.inserted_rows += execute_batch(conn, stmt, rows, dry_run)
                rows.clear()
                pbar.update(BATCH_SIZE)

        if rows:
            inserted = execute_batch(conn, stmt, rows, dry_run)
            metrics.inserted_rows += inserted
            pbar.update(len(rows))

        pbar.close()

    log_json("step_done", step="sms_events", inserted_rows=metrics.inserted_rows, dry_run=dry_run)
    return metrics


def run_step(step: str, engine: Engine, args: argparse.Namespace) -> None:
    if step == "fix_last_activity_at":
        fix_last_activity_at(engine, args.dry_run)
    elif step == "campaigns":
        seed_campaigns(engine, args.campaigns, args.dry_run)
    elif step == "user_activities":
        seed_user_activities(engine, args.activities, args.dry_run)
    elif step == "cohorts":
        compute_and_insert_cohorts(engine, args.dry_run)
    elif step == "unsubscriptions":
        derive_unsubscriptions(engine, args.dry_run)
    elif step == "sms_events":
        seed_sms_events(engine, args.sms, args.dry_run)
    else:
        raise ValueError(f"Unsupported step: {step}")


def main() -> None:
    # Local lazy env loading to avoid hard dependency if shell env already set.
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:
        pass

    started = time.time()
    args = parse_args()
    engine = get_engine()

    steps = [
        "fix_last_activity_at",
        "campaigns",
        "user_activities",
        "cohorts",
        "unsubscriptions",
        "sms_events",
    ]
    if args.step != "all":
        steps = [args.step]

    log_json("seed_start", dry_run=args.dry_run, step=args.step, batch_size=BATCH_SIZE)

    for step in steps:
        run_step(step, engine, args)

    elapsed = round(time.time() - started, 2)
    log_json("seed_done", duration_sec=elapsed)


if __name__ == "__main__":
    main()
