from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any

from sqlalchemy import String, and_, cast, func, text
from sqlalchemy.orm import Session

from app.models.analytics import BillingEvent, Subscription, UserActivity
from app.models.cohorts import Cohort
from app.models.services import Service
from app.models.unsubscriptions import Unsubscription
from app.utils.temporal import get_data_bounds, get_default_window


def _normalize_range(
    db: Session,
    start_date: date | datetime | None,
    end_date: date | datetime | None,
    *,
    source: str = "churn",
) -> tuple[datetime, datetime]:
    data_start, data_end = get_data_bounds(db, source=source)

    start = start_date or data_start
    end = end_date or data_end

    if isinstance(start, date) and not isinstance(start, datetime):
        start = datetime.combine(start, time.min)
    if isinstance(end, date) and not isinstance(end, datetime):
        end = datetime.combine(end, time.max)

    if start < data_start:
        start = data_start
    if end > data_end:
        end = data_end

    if start > end:
        start, end = end, start

    if start < data_start:
        start = data_start
    if end > data_end:
        end = data_end
    if start > end:
        start = end

    return start, end


def _subscription_dedupe_key():
    return func.concat(
        cast(Subscription.user_id, String),
        "|",
        cast(Subscription.service_id, String),
        "|",
        func.to_char(Subscription.subscription_start_date, "YYYY-MM-DD HH24:MI:SS"),
    )


def get_global_churn_rate(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
    service_id: str | None = None,
) -> dict[str, Any]:
    if start_date is None or end_date is None:
        start, end = get_default_window(db, days=30, source="churn")
    else:
        start, end = _normalize_range(db, start_date, end_date, source="churn")

    churned_query = (
        db.query(func.count(Subscription.id))
        .filter(Subscription.status.in_(["cancelled", "expired"]))
        .filter(Subscription.subscription_end_date.isnot(None))
        .filter(Subscription.subscription_end_date >= start)
        .filter(Subscription.subscription_end_date <= end)
    )
    if service_id:
        churned_query = churned_query.filter(Subscription.service_id == service_id)
    churned = churned_query.scalar() or 0

    if churned == 0:
        churn_fallback_query = (
            db.query(func.count(UserActivity.id))
            .filter(UserActivity.activity_type == "churn_event")
            .filter(UserActivity.activity_datetime >= start)
            .filter(UserActivity.activity_datetime <= end)
        )
        if service_id:
            churn_fallback_query = churn_fallback_query.filter(UserActivity.service_id == service_id)
        churned = churn_fallback_query.scalar() or 0

    churned_ever_query = db.query(func.count(Subscription.id)).filter(Subscription.status.in_(["cancelled", "expired"]))
    total_ever_query = db.query(func.count(Subscription.id))
    if service_id:
        churned_ever_query = churned_ever_query.filter(Subscription.service_id == service_id)
        total_ever_query = total_ever_query.filter(Subscription.service_id == service_id)

    churned_ever = churned_ever_query.scalar() or 0
    total_ever = total_ever_query.scalar() or 1
    snapshot_rate = round(churned_ever / total_ever * 100, 2)

    monthly_metrics = _compute_monthly_churn_metrics(db, start_date, end_date, service_id=service_id)

    return {
        "global_churn_rate": snapshot_rate,
        "monthly_churn_rate": float(monthly_metrics["churn_rate"]),
        "churned_total": churned_ever,
        "total_subscriptions": total_ever,
        "period_churned": int(monthly_metrics["unsub_count"]),
        "period_base": int(monthly_metrics["active_count"]),
    }


def _compute_monthly_churn_metrics(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
    service_id: str | None = None,
) -> dict[str, Any]:
    service_filter_unsubs = "AND u.service_id = CAST(:service_id AS uuid)" if service_id else ""
    service_filter_subs = "AND s.service_id = CAST(:service_id AS uuid)" if service_id else ""

    if start_date is None or end_date is None:
        row = db.execute(
            text(
                """
                WITH anchor AS (
                    SELECT MAX(event_datetime) AS ts
                    FROM billing_events
                ),
                period AS (
                    SELECT
                        (anchor.ts - INTERVAL '30 days') AS start_ts,
                        anchor.ts AS end_ts
                    FROM anchor
                    WHERE anchor.ts IS NOT NULL
                ),
                unsubs AS (
                    SELECT COUNT(DISTINCT u.subscription_id) AS cnt
                    FROM unsubscriptions u, period p
                    WHERE u.unsubscription_datetime BETWEEN p.start_ts AND p.end_ts
                      {service_filter_unsubs}
                ),
                active_at_start AS (
                    SELECT COUNT(DISTINCT s.id) AS cnt
                    FROM subscriptions s, period p
                    WHERE s.subscription_start_date <= p.start_ts
                      AND (s.subscription_end_date IS NULL OR s.subscription_end_date > p.start_ts)
                      {service_filter_subs}
                ),
                started_in_period AS (
                    SELECT COUNT(DISTINCT s.id) AS cnt
                    FROM subscriptions s, period p
                    WHERE s.subscription_start_date > p.start_ts
                      AND s.subscription_start_date <= p.end_ts
                      {service_filter_subs}
                )
                SELECT
                    COALESCE(unsubs.cnt, 0) AS unsub_count,
                    (COALESCE(active_at_start.cnt, 0) + COALESCE(started_in_period.cnt, 0)) AS active_count,
                    CASE
                        WHEN (COALESCE(active_at_start.cnt, 0) + COALESCE(started_in_period.cnt, 0)) > 0
                        THEN ROUND(
                            COALESCE(unsubs.cnt, 0) * 100.0
                            / (COALESCE(active_at_start.cnt, 0) + COALESCE(started_in_period.cnt, 0)),
                            2
                        )
                        ELSE 0
                    END AS churn_rate,
                    (SELECT start_ts FROM period LIMIT 1) AS period_start,
                    (SELECT end_ts FROM period LIMIT 1) AS period_end
                FROM unsubs, active_at_start, started_in_period
                """.format(
                    service_filter_unsubs=service_filter_unsubs,
                    service_filter_subs=service_filter_subs,
                )
            )
            ,
            {"service_id": service_id} if service_id else {},
        ).fetchone()
    else:
        period_start, period_end = _normalize_range(db, start_date, end_date, source="billing")
        row = db.execute(
            text(
                """
                WITH period AS (
                    SELECT
                        CAST(:start_dt AS timestamp) AS start_ts,
                        CAST(:end_dt AS timestamp) AS end_ts
                ),
                unsubs AS (
                    SELECT COUNT(DISTINCT u.subscription_id) AS cnt
                    FROM unsubscriptions u, period p
                    WHERE u.unsubscription_datetime BETWEEN p.start_ts AND p.end_ts
                      {service_filter_unsubs}
                ),
                active_at_start AS (
                    SELECT COUNT(DISTINCT s.id) AS cnt
                    FROM subscriptions s, period p
                    WHERE s.subscription_start_date <= p.start_ts
                      AND (s.subscription_end_date IS NULL OR s.subscription_end_date > p.start_ts)
                      {service_filter_subs}
                ),
                started_in_period AS (
                    SELECT COUNT(DISTINCT s.id) AS cnt
                    FROM subscriptions s, period p
                    WHERE s.subscription_start_date > p.start_ts
                      AND s.subscription_start_date <= p.end_ts
                      {service_filter_subs}
                )
                SELECT
                    COALESCE(unsubs.cnt, 0) AS unsub_count,
                    (COALESCE(active_at_start.cnt, 0) + COALESCE(started_in_period.cnt, 0)) AS active_count,
                    CASE
                        WHEN (COALESCE(active_at_start.cnt, 0) + COALESCE(started_in_period.cnt, 0)) > 0
                        THEN ROUND(
                            COALESCE(unsubs.cnt, 0) * 100.0
                            / (COALESCE(active_at_start.cnt, 0) + COALESCE(started_in_period.cnt, 0)),
                            2
                        )
                        ELSE 0
                    END AS churn_rate,
                    (SELECT start_ts FROM period LIMIT 1) AS period_start,
                    (SELECT end_ts FROM period LIMIT 1) AS period_end
                FROM unsubs, active_at_start, started_in_period
                """.format(
                    service_filter_unsubs=service_filter_unsubs,
                    service_filter_subs=service_filter_subs,
                )
            ),
            {
                "start_dt": period_start,
                "end_dt": period_end,
                **({"service_id": service_id} if service_id else {}),
            },
        ).fetchone()

    if not row:
        fallback_start, fallback_end = get_default_window(db, days=30, source="billing")
        return {
            "start": fallback_start,
            "end": fallback_end,
            "unsub_count": 0,
            "active_count": 0,
            "churn_rate": 0.0,
            "message": "No churn events in selected period",
        }

    return {
        "start": row.period_start,
        "end": row.period_end,
        "unsub_count": int(row.unsub_count or 0),
        "active_count": int(row.active_count or 0),
        "churn_rate": float(row.churn_rate or 0),
        "message": "No churn events in selected period" if int(row.unsub_count or 0) == 0 else None,
    }


def get_avg_lifetime_days(db: Session, start_date: date | datetime | None = None, end_date: date | datetime | None = None) -> float:
    return get_avg_lifetime_days_filtered(db, start_date, end_date, service_id=None)


def get_avg_lifetime_days_filtered(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
    service_id: str | None = None,
) -> float:
    start, end = _normalize_range(db, start_date, end_date, source="subscription")
    service_clause = "AND service_id = CAST(:service_id AS uuid)" if service_id else ""
    result = db.execute(
        text(
            """
            WITH dedup AS (
                SELECT DISTINCT ON (user_id, service_id, subscription_start_date)
                    user_id,
                    service_id,
                    subscription_start_date,
                    subscription_end_date
                FROM subscriptions
                WHERE subscription_end_date IS NOT NULL
                    AND subscription_start_date IS NOT NULL
                    AND status IN ('cancelled', 'expired')
                    AND subscription_end_date >= :start_dt
                    AND subscription_end_date <= :end_dt
                    {service_clause}
                ORDER BY user_id, service_id, subscription_start_date, subscription_end_date DESC
            )
            SELECT AVG(
                EXTRACT(epoch FROM (subscription_end_date - subscription_start_date)) / 86400.0
            )
            FROM dedup
            WHERE subscription_end_date > subscription_start_date + interval '1 day'
            """.format(service_clause=service_clause)
        ),
        {
            "start_dt": start,
            "end_dt": end,
            **({"service_id": service_id} if service_id else {}),
        },
    ).scalar()

    return round(float(result), 1) if result else 0.0


def get_trial_vs_paid_churn(db: Session, start_date: date | datetime | None = None, end_date: date | datetime | None = None) -> dict[str, Any]:
    start, end = _normalize_range(db, start_date, end_date, source="churn")

    dedupe_key = _subscription_dedupe_key()

    total_churn = (
        db.query(func.count(UserActivity.id))
        .filter(UserActivity.activity_type == "churn_event")
        .filter(UserActivity.activity_datetime >= start)
        .filter(UserActivity.activity_datetime <= end)
        .scalar()
        or 0
    )

    if total_churn == 0:
        total_churn = (
            db.query(func.count(func.distinct(dedupe_key)))
            .filter(Subscription.status.in_(["cancelled", "expired"]))
            .filter(Subscription.subscription_end_date.isnot(None))
            .filter(Subscription.subscription_end_date >= start)
            .filter(Subscription.subscription_end_date <= end)
            .scalar()
            or 0
        )

    trial_churns = (
        db.query(func.count(func.distinct(dedupe_key)))
        .filter(Subscription.status == "cancelled")
        .filter(Subscription.subscription_end_date.isnot(None))
        .filter(Subscription.subscription_end_date >= start)
        .filter(Subscription.subscription_end_date <= end)
        .join(
            UserActivity,
            and_(
                UserActivity.user_id == Subscription.user_id,
                UserActivity.service_id == Subscription.service_id,
                UserActivity.activity_type == "subscription",
                UserActivity.activity_datetime <= Subscription.subscription_end_date,
            ),
        )
        .scalar()
        or 0
    )

    paid_churns = max(total_churn - trial_churns, 0)
    denom = total_churn or 1

    return {
        "trial_churn_rate": round(trial_churns / denom * 100, 2),
        "paid_churn_rate": round(paid_churns / denom * 100, 2),
        "total_churned": total_churn,
    }


def get_first_bill_churn(db: Session, start_date: date | datetime | None = None, end_date: date | datetime | None = None) -> float:
    start, end = _normalize_range(db, start_date, end_date, source="billing")

    first_charges = (
        db.query(
            BillingEvent.user_id.label("user_id"),
            BillingEvent.service_id.label("service_id"),
            BillingEvent.event_datetime.label("first_charge_date"),
        )
        .filter(BillingEvent.is_first_charge.is_(True))
        .filter(func.lower(BillingEvent.status) == "success")
        .filter(BillingEvent.event_datetime >= start)
        .filter(BillingEvent.event_datetime <= end)
        .subquery()
    )

    first_bill_churns = (
        db.query(func.count(UserActivity.id))
        .join(
            first_charges,
            and_(
                UserActivity.user_id == first_charges.c.user_id,
                UserActivity.service_id == first_charges.c.service_id,
                UserActivity.activity_type == "churn_event",
                UserActivity.activity_datetime >= first_charges.c.first_charge_date,
                UserActivity.activity_datetime <= first_charges.c.first_charge_date + timedelta(days=7),
            ),
        )
        .filter(UserActivity.activity_datetime >= start)
        .filter(UserActivity.activity_datetime <= end)
        .scalar()
        or 0
    )

    total_first_charges = (
        db.query(func.count(BillingEvent.id))
        .filter(BillingEvent.is_first_charge.is_(True))
        .filter(func.lower(BillingEvent.status) == "success")
        .filter(BillingEvent.event_datetime >= start)
        .filter(BillingEvent.event_datetime <= end)
        .scalar()
        or 1
    )

    return round(first_bill_churns / total_first_charges * 100, 2)


def get_voluntary_vs_technical_churn(db: Session, start_date: date | datetime | None = None, end_date: date | datetime | None = None) -> dict[str, Any]:
    start, end = _normalize_range(db, start_date, end_date, source="churn")

    row = db.execute(
        text(
            """
            SELECT
                COUNT(*) FILTER (WHERE status = 'cancelled') as voluntary,
                COUNT(*) FILTER (WHERE status = 'expired') as technical
            FROM subscriptions
            WHERE status IN ('cancelled', 'expired')
              AND subscription_end_date IS NOT NULL
              AND subscription_end_date >= :start_dt
              AND subscription_end_date <= :end_dt
            """
        ),
        {"start_dt": start, "end_dt": end},
    ).fetchone()

    voluntary = int(row.voluntary or 0)
    technical = int(row.technical or 0)

    total = (voluntary + technical) or 1

    return {
        "voluntary_rate": round(voluntary / total * 100, 2),
        "technical_rate": round(technical / total * 100, 2),
        "voluntary_count": voluntary,
        "technical_count": technical,
    }


def get_churn_over_time(db: Session, start_date: date | datetime | None = None, end_date: date | datetime | None = None) -> list[dict[str, Any]]:
    if start_date is None or end_date is None:
        start, end = get_default_window(db, days=30, source="churn")
    else:
        start, end = _normalize_range(db, start_date, end_date, source="churn")

    dedupe_key = _subscription_dedupe_key()

    monthly = (
        db.query(
            func.date_trunc("month", Subscription.subscription_end_date).label("month"),
            func.count(func.distinct(dedupe_key)).label("churned"),
            func.count(func.distinct(dedupe_key)).filter(Subscription.status == "cancelled").label("voluntary"),
            func.count(func.distinct(dedupe_key)).filter(Subscription.status == "expired").label("technical"),
        )
        .filter(Subscription.subscription_end_date.isnot(None))
        .filter(Subscription.status.in_(["cancelled", "expired"]))
        .filter(Subscription.subscription_end_date >= start)
        .filter(Subscription.subscription_end_date <= end)
        .group_by(func.date_trunc("month", Subscription.subscription_end_date))
        .order_by(func.date_trunc("month", Subscription.subscription_end_date))
        .all()
    )

    return [
        {
            "month": row.month.strftime("%Y-%m"),
            "churned": int(row.churned or 0),
            "voluntary": int(row.voluntary or 0),
            "technical": int(row.technical or 0),
        }
        for row in monthly
        if row.month is not None
    ]


def get_monthly_churn_rate(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
    service_id: str | None = None,
) -> dict[str, Any]:
    metrics = _compute_monthly_churn_metrics(db, start_date, end_date, service_id=service_id)
    return {
        "rate": float(metrics.get("churn_rate", 0) or 0),
        "churned": int(metrics.get("unsub_count", 0) or 0),
        "total": int(metrics.get("active_count", 0) or 0),
        "message": metrics.get("message"),
    }


def get_churn_breakdown(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
    service_id: str | None = None,
) -> dict[str, Any]:
    service_filter = "AND u.service_id = CAST(:service_id AS uuid)" if service_id else ""
    if start_date is None or end_date is None:
        row = db.execute(
            text(
                """
                WITH anchor AS (
                    SELECT MAX(event_datetime) AS ts
                    FROM billing_events
                ),
                period AS (
                    SELECT
                        (anchor.ts - INTERVAL '30 days') AS start_ts,
                        anchor.ts AS end_ts
                    FROM anchor
                    WHERE anchor.ts IS NOT NULL
                )
                SELECT
                    COUNT(*) AS total_unsubs,
                    COUNT(*) FILTER (WHERE u.churn_type = 'VOLUNTARY') AS voluntary,
                    COUNT(*) FILTER (WHERE u.churn_type = 'TECHNICAL') AS technical,
                    ROUND(
                        COUNT(*) FILTER (WHERE u.churn_type = 'VOLUNTARY') * 100.0
                        / NULLIF(COUNT(*), 0), 1
                    ) AS voluntary_pct,
                    ROUND(
                        COUNT(*) FILTER (WHERE u.churn_type = 'TECHNICAL') * 100.0
                        / NULLIF(COUNT(*), 0), 1
                    ) AS technical_pct
                FROM unsubscriptions u, period p
                WHERE u.unsubscription_datetime BETWEEN p.start_ts AND p.end_ts
                  {service_filter}
                """.format(service_filter=service_filter)
            )
            ,
            {"service_id": service_id} if service_id else {},
        ).fetchone()
    else:
        normalized_start, normalized_end = _normalize_range(db, start_date, end_date, source="billing")
        row = db.execute(
            text(
                """
                WITH period AS (
                    SELECT
                        CAST(:start_dt AS timestamp) AS start_ts,
                        CAST(:end_dt AS timestamp) AS end_ts
                )
                SELECT
                    COUNT(*) AS total_unsubs,
                    COUNT(*) FILTER (WHERE u.churn_type = 'VOLUNTARY') AS voluntary,
                    COUNT(*) FILTER (WHERE u.churn_type = 'TECHNICAL') AS technical,
                    ROUND(
                        COUNT(*) FILTER (WHERE u.churn_type = 'VOLUNTARY') * 100.0
                        / NULLIF(COUNT(*), 0), 1
                    ) AS voluntary_pct,
                    ROUND(
                        COUNT(*) FILTER (WHERE u.churn_type = 'TECHNICAL') * 100.0
                        / NULLIF(COUNT(*), 0), 1
                    ) AS technical_pct
                FROM unsubscriptions u, period p
                WHERE u.unsubscription_datetime BETWEEN p.start_ts AND p.end_ts
                  {service_filter}
                """.format(service_filter=service_filter)
            ),
            {
                "start_dt": normalized_start,
                "end_dt": normalized_end,
                **({"service_id": service_id} if service_id else {}),
            },
        ).fetchone()

    total = int((row.total_unsubs if row else 0) or 0)
    voluntary_count = int((row.voluntary if row else 0) or 0)
    technical_count = int((row.technical if row else 0) or 0)
    return {
        "total": total,
        "voluntary": {
            "count": voluntary_count,
            "rate": float((row.voluntary_pct if row else 0) or 0),
        },
        "technical": {
            "count": technical_count,
            "rate": float((row.technical_pct if row else 0) or 0),
        },
        "message": "No churn events in selected period" if total == 0 else None,
    }


def get_churn_trend_daily(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
    service_id: str | None = None,
) -> list[dict[str, Any]]:
    start, end = _normalize_range(db, start_date, end_date, source="churn")

    churn_query = (
        db.query(
            cast(func.date_trunc("day", Unsubscription.unsubscription_datetime), String).label("day"),
            func.count(Unsubscription.id).label("churned"),
        )
        .filter(Unsubscription.unsubscription_datetime >= start)
        .filter(Unsubscription.unsubscription_datetime <= end)
    )
    if service_id:
        churn_query = churn_query.filter(Unsubscription.service_id == service_id)

    churn_rows = (
        churn_query.group_by(func.date_trunc("day", Unsubscription.unsubscription_datetime))
        .order_by(func.date_trunc("day", Unsubscription.unsubscription_datetime))
        .all()
    )

    new_query = (
        db.query(
            cast(func.date_trunc("day", Subscription.subscription_start_date), String).label("day"),
            func.count(Subscription.id).label("new_subs"),
        )
        .filter(Subscription.subscription_start_date >= start)
        .filter(Subscription.subscription_start_date <= end)
    )
    if service_id:
        new_query = new_query.filter(Subscription.service_id == service_id)

    new_rows = (
        new_query.group_by(func.date_trunc("day", Subscription.subscription_start_date))
        .order_by(func.date_trunc("day", Subscription.subscription_start_date))
        .all()
    )

    by_day: dict[str, dict[str, Any]] = {}
    for row in churn_rows:
        day = str(row.day)[:10]
        by_day.setdefault(day, {"date": day, "new_subs": 0, "churned": 0})
        by_day[day]["churned"] = int(row.churned or 0)

    for row in new_rows:
        day = str(row.day)[:10]
        by_day.setdefault(day, {"date": day, "new_subs": 0, "churned": 0})
        by_day[day]["new_subs"] = int(row.new_subs or 0)

    return [by_day[k] for k in sorted(by_day.keys())]


def get_churn_by_service(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
    service_id: str | None = None,
) -> list[dict[str, Any]]:
    start, end = _normalize_range(db, start_date, end_date, source="churn")
    service_filter = "AND sub.service_id = CAST(:service_id AS uuid)" if service_id else ""

    rows = db.execute(
        text(
            """
            SELECT s.name as service_name, COUNT(sub.id) as churned
            FROM subscriptions sub
            JOIN services s ON sub.service_id = s.id
            WHERE sub.status IN ('cancelled', 'expired')
              AND sub.subscription_end_date IS NOT NULL
              AND sub.subscription_end_date >= :start_dt
              AND sub.subscription_end_date <= :end_dt
                            {service_filter}
            GROUP BY s.id, s.name
            ORDER BY churned DESC
            """
                        .format(service_filter=service_filter)
        ),
                {
                        "start_dt": start,
                        "end_dt": end,
                        **({"service_id": service_id} if service_id else {}),
                },
    ).fetchall()

    return [
        {"service_name": row.service_name, "churned": int(row.churned or 0)}
        for row in rows
    ]


def get_lifetime_distribution(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
    service_id: str | None = None,
) -> list[dict[str, Any]]:
    start, end = _normalize_range(db, start_date, end_date, source="subscription")
    service_clause = "AND service_id = CAST(:service_id AS uuid)" if service_id else ""

    row = db.execute(
        text(
            """
            SELECT
                COUNT(*) FILTER (WHERE d <= 7) AS b_0_7,
                COUNT(*) FILTER (WHERE d > 7 AND d <= 30) AS b_8_30,
                COUNT(*) FILTER (WHERE d > 30 AND d <= 90) AS b_31_90,
                COUNT(*) FILTER (WHERE d > 90 AND d <= 180) AS b_91_180,
                COUNT(*) FILTER (WHERE d > 180) AS b_181_plus
            FROM (
                SELECT EXTRACT(DAY FROM (subscription_end_date - subscription_start_date))::int AS d
                FROM subscriptions
                WHERE subscription_end_date IS NOT NULL
                  AND subscription_start_date IS NOT NULL
                  AND status IN ('cancelled', 'expired')
                  AND subscription_end_date >= :start_dt
                  AND subscription_end_date <= :end_dt
                  {service_clause}
            ) t
            """
            .format(service_clause=service_clause)
        ),
        {
            "start_dt": start,
            "end_dt": end,
            **({"service_id": service_id} if service_id else {}),
        },
    ).fetchone()

    return [
        {"bucket": "0-7d", "count": int(row.b_0_7 or 0)},
        {"bucket": "8-30d", "count": int(row.b_8_30 or 0)},
        {"bucket": "31-90d", "count": int(row.b_31_90 or 0)},
        {"bucket": "91-180d", "count": int(row.b_91_180 or 0)},
        {"bucket": "181+d", "count": int(row.b_181_plus or 0)},
    ]


def get_retention_cohort(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
    service_id: str | None = None,
) -> list[dict[str, Any]]:
    start, end = _normalize_range(db, start_date, end_date, source="subscription")

    query = (
        db.query(
            Cohort.cohort_date,
            func.sum(Cohort.total_users).label("total_users"),
            func.avg(Cohort.retention_d7).label("d7_rate"),
            func.avg(Cohort.retention_d14).label("d14_rate"),
            func.avg(Cohort.retention_d30).label("d30_rate"),
        )
        .filter(Cohort.cohort_date >= start.date())
        .filter(Cohort.cohort_date <= end.date())
    )
    if service_id:
        query = query.filter(Cohort.service_id == service_id)

    rows = (
        query.group_by(Cohort.cohort_date)
        .order_by(Cohort.cohort_date.desc())
        .limit(12)
        .all()
    )

    return [
        {
            "cohort": row.cohort_date.isoformat(),
            "total": int(row.total_users or 0),
            "d7_rate": round(float(row.d7_rate or 0), 1),
            "d14_rate": round(float(row.d14_rate or 0), 1),
            "d30_rate": round(float(row.d30_rate or 0), 1),
        }
        for row in rows
    ]


def get_reactivation_kpis(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
    service_id: str | None = None,
) -> dict[str, Any]:
    start_dt, end_dt = _normalize_range(db, start_date, end_date, source="churn")
    service_filter = "AND u.service_id = CAST(:service_id AS uuid)" if service_id else ""

    row = db.execute(
        text(
            """
            WITH churn_events AS (
                SELECT
                    u.user_id,
                    u.service_id,
                    u.subscription_id,
                    u.unsubscription_datetime AS churn_date
                FROM unsubscriptions u
                WHERE u.unsubscription_datetime BETWEEN :start_dt AND :end_dt
                  {service_filter}
            ),
            churned_users AS (
                SELECT COUNT(DISTINCT user_id) AS total
                FROM churn_events
            ),
            reactivations AS (
                SELECT
                    c.user_id,
                    c.service_id,
                    c.churn_date,
                    MIN(s.subscription_start_date) AS resub_date
                FROM churn_events c
                JOIN subscriptions s
                  ON s.user_id = c.user_id
                 AND s.service_id = c.service_id
                                 AND s.id <> c.subscription_id
                                 AND s.subscription_start_date >= c.churn_date
                GROUP BY c.user_id, c.service_id, c.churn_date
            ),
            recovered AS (
                SELECT COALESCE(SUM(st.price), 0)::float AS recovered_revenue
                FROM reactivations r
                JOIN billing_events be
                  ON be.user_id = r.user_id
                 AND be.service_id = r.service_id
                 AND be.event_datetime >= r.resub_date
                 AND be.event_datetime <= :end_dt
                 AND LOWER(be.status) = 'success'
                JOIN services srv ON srv.id = be.service_id
                JOIN service_types st ON st.id = srv.service_type_id
            )
            SELECT
                COUNT(DISTINCT r.user_id) AS reactivated_users,
                ROUND(
                    COUNT(DISTINCT r.user_id) * 100.0
                    / NULLIF((SELECT total FROM churned_users), 0),
                    2
                ) AS reactivation_rate,
                ROUND(
                    AVG(EXTRACT(EPOCH FROM (r.resub_date - r.churn_date)) / 86400.0)::numeric,
                    1
                ) AS avg_days_to_resubscribe,
                (SELECT recovered_revenue FROM recovered) AS recovered_revenue
            FROM reactivations r
            """.format(service_filter=service_filter)
        ),
        {
            "start_dt": start_dt,
            "end_dt": end_dt,
            **({"service_id": service_id} if service_id else {}),
        },
    ).fetchone()

    return {
        "reactivated_users": int((row.reactivated_users if row else 0) or 0),
        "reactivation_rate": float((row.reactivation_rate if row else 0) or 0),
        "avg_days_to_resubscribe": float((row.avg_days_to_resubscribe if row else 0) or 0),
        "recovered_revenue": round(float((row.recovered_revenue if row else 0) or 0), 2),
    }


def get_reactivation_by_service(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
    service_id: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    start_dt, end_dt = _normalize_range(db, start_date, end_date, source="churn")
    service_filter = "AND u.service_id = CAST(:service_id AS uuid)" if service_id else ""

    rows = db.execute(
        text(
            """
            WITH churn_events AS (
                SELECT
                    u.user_id,
                    u.service_id,
                    u.subscription_id,
                    u.unsubscription_datetime AS churn_date
                FROM unsubscriptions u
                WHERE u.unsubscription_datetime BETWEEN :start_dt AND :end_dt
                  {service_filter}
            ),
            churned_by_service AS (
                SELECT service_id, COUNT(DISTINCT user_id) AS churned_users
                FROM churn_events
                GROUP BY service_id
            ),
            reactivations AS (
                SELECT
                    c.user_id,
                    c.service_id,
                    MIN(s.subscription_start_date) AS resub_date
                FROM churn_events c
                JOIN subscriptions s
                  ON s.user_id = c.user_id
                 AND s.service_id = c.service_id
                                 AND s.id <> c.subscription_id
                                 AND s.subscription_start_date >= c.churn_date
                GROUP BY c.user_id, c.service_id
            ),
            reactivated_by_service AS (
                SELECT service_id, COUNT(DISTINCT user_id) AS reactivated_users
                FROM reactivations
                GROUP BY service_id
            )
            SELECT
                srv.id AS service_id,
                srv.name AS service_name,
                COALESCE(rbs.reactivated_users, 0) AS reactivated_users,
                ROUND(
                    COALESCE(rbs.reactivated_users, 0) * 100.0
                    / NULLIF(cbs.churned_users, 0),
                    2
                ) AS reactivation_rate
            FROM churned_by_service cbs
            JOIN services srv ON srv.id = cbs.service_id
            LEFT JOIN reactivated_by_service rbs ON rbs.service_id = cbs.service_id
            ORDER BY reactivated_users DESC, service_name ASC
            LIMIT :limit
            """.format(service_filter=service_filter)
        ),
        {
            "start_dt": start_dt,
            "end_dt": end_dt,
            "limit": int(limit),
            **({"service_id": service_id} if service_id else {}),
        },
    ).fetchall()

    return [
        {
            "service_id": str(row.service_id),
            "service_name": row.service_name,
            "reactivated_users": int(row.reactivated_users or 0),
            "reactivation_rate": float(row.reactivation_rate or 0),
        }
        for row in rows
    ]
