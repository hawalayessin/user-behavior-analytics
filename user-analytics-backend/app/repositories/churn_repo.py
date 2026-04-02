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


def get_global_churn_rate(db: Session, start_date: date | datetime | None = None, end_date: date | datetime | None = None) -> dict[str, Any]:
    if start_date is None or end_date is None:
        start, end = get_default_window(db, days=30, source="churn")
    else:
        start, end = _normalize_range(db, start_date, end_date, source="churn")

    churned = (
        db.query(func.count(Subscription.id))
        .filter(Subscription.status.in_(["cancelled", "expired"]))
        .filter(Subscription.subscription_end_date.isnot(None))
        .filter(Subscription.subscription_end_date >= start)
        .filter(Subscription.subscription_end_date <= end)
        .scalar()
        or 0
    )

    if churned == 0:
        churned = (
            db.query(func.count(UserActivity.id))
            .filter(UserActivity.activity_type == "churn_event")
            .filter(UserActivity.activity_datetime >= start)
            .filter(UserActivity.activity_datetime <= end)
            .scalar()
            or 0
        )

    churned_ever = (
        db.query(func.count(Subscription.id))
        .filter(Subscription.status.in_(["cancelled", "expired"]))
        .scalar()
        or 0
    )
    total_ever = db.query(func.count(Subscription.id)).scalar() or 1
    snapshot_rate = round(churned_ever / total_ever * 100, 2)

    monthly_metrics = _compute_monthly_churn_metrics(db, start_date, end_date)

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
) -> dict[str, Any]:
    if start_date is None or end_date is None:
        period_start, period_end = get_default_window(db, days=30, source="billing")
    else:
        period_start, period_end = _normalize_range(db, start_date, end_date, source="billing")

    row = db.execute(
        text(
            """
            WITH unsubs AS (
                SELECT COUNT(*) AS cnt
                FROM unsubscriptions u
                WHERE u.unsubscription_datetime >= :start_dt
                  AND u.unsubscription_datetime <= :end_dt
            ),
            active_start AS (
                SELECT COUNT(DISTINCT s.user_id) AS cnt
                FROM subscriptions s
                WHERE s.subscription_start_date <= :start_dt
                  AND (s.subscription_end_date IS NULL OR s.subscription_end_date > :start_dt)
            )
            SELECT
                unsubs.cnt AS unsub_count,
                active_start.cnt AS active_count,
                CASE
                    WHEN active_start.cnt > 0 THEN ROUND(unsubs.cnt * 100.0 / active_start.cnt, 2)
                    ELSE 0
                END AS churn_rate
            FROM unsubs, active_start
            """
        ),
        {"start_dt": period_start, "end_dt": period_end},
    ).fetchone()

    if not row:
        return {"start": period_start, "end": period_end, "unsub_count": 0, "active_count": 0, "churn_rate": 0.0}

    return {
        "start": period_start,
        "end": period_end,
        "unsub_count": int(row.unsub_count or 0),
        "active_count": int(row.active_count or 0),
        "churn_rate": float(row.churn_rate or 0),
    }


def get_avg_lifetime_days(db: Session, start_date: date | datetime | None = None, end_date: date | datetime | None = None) -> float:
    start, end = _normalize_range(db, start_date, end_date, source="subscription")
    result = db.execute(
        text(
            """
            WITH dedup AS (
                SELECT DISTINCT ON (user_id, service_id, subscription_start_date)
                    user_id,
                    service_id,
                    subscription_start_date,
                    subscription_end_date,
                    status
                FROM subscriptions
                WHERE subscription_end_date IS NOT NULL
                    AND subscription_start_date IS NOT NULL
                    AND status IN ('cancelled', 'expired')
                    AND subscription_end_date >= :start_dt
                    AND subscription_end_date <= :end_dt
                ORDER BY user_id, service_id, subscription_start_date, id DESC
            )
            SELECT AVG(
                EXTRACT(epoch FROM (subscription_end_date - subscription_start_date)) / 86400.0
            )
            FROM dedup
            WHERE subscription_end_date > subscription_start_date
                AND subscription_end_date - subscription_start_date > interval '1 day'
            """
        ),
        {"start_dt": start, "end_dt": end},
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
) -> dict[str, Any]:
    metrics = _compute_monthly_churn_metrics(db, start_date, end_date)
    return {
        "rate": float(metrics.get("churn_rate", 0) or 0),
        "churned": int(metrics.get("unsub_count", 0) or 0),
        "total": int(metrics.get("active_count", 0) or 0),
    }


def get_churn_breakdown(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
) -> dict[str, Any]:
    if start_date is None or end_date is None:
        start_date, end_date = get_default_window(db, days=30, source="billing")
    breakdown = get_voluntary_vs_technical_churn(db, start_date, end_date)
    voluntary_count = int(breakdown.get("voluntary_count", 0) or 0)
    technical_count = int(breakdown.get("technical_count", 0) or 0)
    return {
        "total": voluntary_count + technical_count,
        "voluntary": {
            "count": voluntary_count,
            "rate": float(breakdown.get("voluntary_rate", 0) or 0),
        },
        "technical": {
            "count": technical_count,
            "rate": float(breakdown.get("technical_rate", 0) or 0),
        },
    }


def get_churn_trend_daily(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
) -> list[dict[str, Any]]:
    start, end = _normalize_range(db, start_date, end_date, source="churn")

    churn_rows = (
        db.query(
            cast(func.date_trunc("day", Unsubscription.unsubscription_datetime), String).label("day"),
            func.count(Unsubscription.id).label("churned"),
        )
        .filter(Unsubscription.unsubscription_datetime >= start)
        .filter(Unsubscription.unsubscription_datetime <= end)
        .group_by(func.date_trunc("day", Unsubscription.unsubscription_datetime))
        .order_by(func.date_trunc("day", Unsubscription.unsubscription_datetime))
        .all()
    )

    new_rows = (
        db.query(
            cast(func.date_trunc("day", Subscription.subscription_start_date), String).label("day"),
            func.count(Subscription.id).label("new_subs"),
        )
        .filter(Subscription.subscription_start_date >= start)
        .filter(Subscription.subscription_start_date <= end)
        .group_by(func.date_trunc("day", Subscription.subscription_start_date))
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
) -> list[dict[str, Any]]:
    start, end = _normalize_range(db, start_date, end_date, source="churn")

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
            GROUP BY s.id, s.name
            ORDER BY churned DESC
            """
        ),
        {"start_dt": start, "end_dt": end},
    ).fetchall()

    return [
        {"service_name": row.service_name, "churned": int(row.churned or 0)}
        for row in rows
    ]


def get_lifetime_distribution(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
) -> list[dict[str, Any]]:
    start, end = _normalize_range(db, start_date, end_date, source="subscription")

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
            ) t
            """
        ),
        {"start_dt": start, "end_dt": end},
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
) -> list[dict[str, Any]]:
    start, end = _normalize_range(db, start_date, end_date, source="subscription")

    rows = (
        db.query(
            Cohort.cohort_date,
            func.sum(Cohort.total_users).label("total_users"),
            func.avg(Cohort.retention_d7).label("d7_rate"),
            func.avg(Cohort.retention_d14).label("d14_rate"),
            func.avg(Cohort.retention_d30).label("d30_rate"),
        )
        .filter(Cohort.cohort_date >= start.date())
        .filter(Cohort.cohort_date <= end.date())
        .group_by(Cohort.cohort_date)
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
