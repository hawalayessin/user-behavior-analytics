from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone, date, timedelta
from typing import Optional

from app.core.database import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ══════════════════════════════════════════════════════════════════
# GET /analytics/summary  — données globales SANS filtre de date
# ══════════════════════════════════════════════════════════════════
@router.get("/summary")
def get_summary(
    db:         Session = Depends(get_db),
    service_id: Optional[str] = Query(default=None),
):
    params  = {"service_id": service_id}
    sf_subs = "AND s.service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_churn= "AND s.service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_rev  = "AND srv.id = CAST(:service_id AS uuid)"       if service_id else ""
    sf_eng  = "AND service_id = CAST(:service_id AS uuid)"   if service_id else ""

    users = db.execute(text("""
        SELECT
            COUNT(*)                                                          AS total_users,
            COUNT(*) FILTER (WHERE status = 'active')                         AS active_users,
            COUNT(*) FILTER (WHERE status = 'inactive')                       AS inactive_users,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days')  AS new_last_30_days
        FROM users
    """), params).fetchone()

    subs = db.execute(text(f"""
        SELECT
            COUNT(*)                                               AS total,
            COUNT(*) FILTER (WHERE s.status = 'active')           AS active,
            COUNT(*) FILTER (WHERE s.status = 'trial')            AS trial,
            COUNT(*) FILTER (WHERE s.status = 'expired')          AS expired,
            COUNT(*) FILTER (WHERE s.status = 'cancelled')        AS cancelled,
            ROUND(
                COUNT(*) FILTER (WHERE s.status = 'active') * 100.0
                / NULLIF(
                    COUNT(*) FILTER (WHERE s.status IN ('active','expired'))
                    + COUNT(*) FILTER (
                        WHERE s.status = 'cancelled'
                        AND (s.subscription_end_date - s.subscription_start_date)
                            <= INTERVAL '3 days'
                    ), 0
                ), 1
            )                                                      AS conversion_rate_pct
        FROM subscriptions s
        WHERE 1=1 {sf_subs}
    """), params).fetchone()

    churn = db.execute(text(f"""
        SELECT
            COUNT(*)                                                         AS total_unsubs,
            COUNT(*) FILTER (WHERE u.churn_type = 'VOLUNTARY')               AS voluntary,
            COUNT(*) FILTER (WHERE u.churn_type = 'TECHNICAL')               AS technical,
            ROUND(COUNT(*) FILTER (WHERE u.churn_type = 'VOLUNTARY') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                    AS voluntary_pct,
            ROUND(COUNT(*) FILTER (WHERE u.churn_type = 'TECHNICAL') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                    AS technical_pct,
            COUNT(*) FILTER (WHERE u.days_since_subscription = 1)            AS dropoff_day1,
            COUNT(*) FILTER (WHERE u.days_since_subscription = 2)            AS dropoff_day2,
            COUNT(*) FILTER (WHERE u.days_since_subscription = 3)            AS dropoff_day3,
            ROUND(
                COUNT(*) FILTER (
                    WHERE u.unsubscription_datetime >= NOW() - INTERVAL '30 days'
                ) * 100.0
                / NULLIF((
                    SELECT COUNT(*) FROM subscriptions WHERE status = 'active'
                ), 0), 2
            )                                                                AS churn_rate_month_pct
        FROM unsubscriptions u
        JOIN subscriptions s ON s.id = u.subscription_id
        WHERE 1=1 {sf_churn}
    """), params).fetchone()

    revenue = db.execute(text(f"""
        SELECT
            ROUND(SUM(st.price) FILTER (WHERE be.status = 'SUCCESS'), 2)      AS total_revenue,
            COUNT(*) FILTER (WHERE be.status = 'SUCCESS')                     AS success_events,
            COUNT(*) FILTER (WHERE be.status = 'FAILED')                      AS failed_events,
            ROUND(COUNT(*) FILTER (WHERE be.status = 'FAILED') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                     AS failed_pct,
            ROUND(SUM(st.price) FILTER (
                WHERE be.status = 'SUCCESS'
                AND be.event_datetime >= NOW() - INTERVAL '30 days'
            ), 2)                                                              AS mrr,
            ROUND(
                SUM(st.price) FILTER (
                    WHERE be.status = 'SUCCESS'
                    AND be.event_datetime >= NOW() - INTERVAL '30 days'
                ) / NULLIF(COUNT(DISTINCT be.user_id) FILTER (
                    WHERE be.status = 'SUCCESS'
                    AND be.event_datetime >= NOW() - INTERVAL '30 days'
                ), 0), 2
            )                                                                  AS arpu_current_month
        FROM billing_events be
        JOIN subscriptions  s   ON s.id   = be.subscription_id
        JOIN services       srv ON srv.id = s.service_id
        JOIN service_types  st  ON st.id  = srv.service_type_id
        WHERE 1=1 {sf_rev}
    """), params).fetchone()

    engagement = db.execute(text(f"""
        SELECT
            COUNT(DISTINCT user_id) FILTER (
                WHERE DATE(activity_datetime) = CURRENT_DATE
            )                                                    AS dau_today,
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime >= NOW() - INTERVAL '30 days'
            )                                                    AS mau_current_month,
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime >= NOW() - INTERVAL '7 days'
            )                                                    AS wau_current_week
        FROM user_activities
        WHERE 1=1 {sf_eng}
    """), params).fetchone()

    dau        = engagement.dau_today         or 0
    mau        = engagement.mau_current_month or 0
    stickiness = round((dau / mau * 100), 1)  if mau > 0 else 0.0

    top_services = db.execute(text("""
        SELECT
            srv.name                                             AS service_name,
            COUNT(*) FILTER (WHERE s.status = 'active')         AS active_subs,
            COUNT(*) FILTER (WHERE s.status = 'cancelled')      AS churned_subs,
            ROUND(
                COUNT(*) FILTER (WHERE s.status = 'cancelled') * 100.0
                / NULLIF(COUNT(*), 0), 1
            )                                                    AS churn_rate_pct
        FROM subscriptions s
        JOIN services srv ON srv.id = s.service_id
        GROUP BY srv.name
        ORDER BY active_subs DESC
    """), params).fetchall()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "users": {
            "total":            users.total_users,
            "active":           users.active_users,
            "inactive":         users.inactive_users,
            "new_last_30_days": users.new_last_30_days,
        },
        "subscriptions": {
            "total":               subs.total,
            "active":              subs.active,
            "trial":               subs.trial,
            "expired":             subs.expired,
            "cancelled":           subs.cancelled,
            "conversion_rate_pct": float(subs.conversion_rate_pct or 0),
        },
        "churn": {
            "total":                churn.total_unsubs,
            "voluntary":            churn.voluntary,
            "technical":            churn.technical,
            "voluntary_pct":        float(churn.voluntary_pct        or 0),
            "technical_pct":        float(churn.technical_pct        or 0),
            "churn_rate_month_pct": float(churn.churn_rate_month_pct or 0),
            "dropoff": {
                "day1": churn.dropoff_day1,
                "day2": churn.dropoff_day2,
                "day3": churn.dropoff_day3,
            },
        },
        "revenue": {
            "total_revenue":      float(revenue.total_revenue      or 0),
            "mrr":                float(revenue.mrr                or 0),
            "arpu_current_month": float(revenue.arpu_current_month or 0),
            "billing_success":    revenue.success_events,
            "billing_failed":     revenue.failed_events,
            "failed_pct":         float(revenue.failed_pct         or 0),
        },
        "engagement": {
            "dau_today":         dau,
            "wau_current_week":  engagement.wau_current_week or 0,
            "mau_current_month": mau,
            "stickiness_pct":    stickiness,
        },
        "top_services": [
            {
                "name":           row.service_name,
                "active_subs":    row.active_subs,
                "churned_subs":   row.churned_subs,
                "churn_rate_pct": float(row.churn_rate_pct or 0),
            }
            for row in top_services
        ],
    }


# ══════════════════════════════════════════════════════════════════
# GET /analytics/overview  — données filtrées par date + service
# ══════════════════════════════════════════════════════════════════
@router.get("/overview")
def get_overview(
    db:         Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date:   Optional[date] = Query(default=None),
    service_id: Optional[str]  = Query(default=None),
):
    end_dt   = end_date   or date.today()
    start_dt = start_date or (end_dt - timedelta(days=30))

    params = {"start_dt": start_dt, "end_dt": end_dt, "service_id": service_id}

    sf_subs  = "AND srv.id = CAST(:service_id AS uuid)"       if service_id else ""
    sf_churn = "AND s.service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_rev   = "AND srv.id = CAST(:service_id AS uuid)"       if service_id else ""
    sf_eng   = "AND service_id = CAST(:service_id AS uuid)"   if service_id else ""
    sf_top   = "AND srv.id = CAST(:service_id AS uuid)"       if service_id else ""
    sj_subs  = "JOIN services srv ON srv.id = s.service_id"   if service_id else ""

    users = db.execute(text("""
        SELECT
            COUNT(*)                                                          AS total_users,
            COUNT(*) FILTER (WHERE status = 'active')                         AS active_users,
            COUNT(*) FILTER (WHERE status = 'inactive')                       AS inactive_users,
            COUNT(*) FILTER (
                WHERE created_at BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
            )                                                                 AS new_last_30_days
        FROM users
    """), params).fetchone()

    subs = db.execute(text(f"""
        SELECT
            COUNT(*)                                               AS total,
            COUNT(*) FILTER (WHERE s.status = 'active')           AS active,
            COUNT(*) FILTER (WHERE s.status = 'trial')            AS trial,
            COUNT(*) FILTER (WHERE s.status = 'expired')          AS expired,
            COUNT(*) FILTER (WHERE s.status = 'cancelled')        AS cancelled,
            ROUND(
                COUNT(*) FILTER (WHERE s.status = 'active') * 100.0
                / NULLIF(
                    COUNT(*) FILTER (WHERE s.status IN ('active','expired'))
                    + COUNT(*) FILTER (
                        WHERE s.status = 'cancelled'
                        AND (s.subscription_end_date - s.subscription_start_date)
                            <= INTERVAL '3 days'
                    ), 0
                ), 1
            )                                                      AS conversion_rate_pct
        FROM subscriptions s
        {sj_subs}
        WHERE s.subscription_start_date BETWEEN :start_dt AND :end_dt
        {sf_subs}
    """), params).fetchone()

    churn = db.execute(text(f"""
        SELECT
            COUNT(*)                                                         AS total_unsubs,
            COUNT(*) FILTER (WHERE u.churn_type = 'VOLUNTARY')               AS voluntary,
            COUNT(*) FILTER (WHERE u.churn_type = 'TECHNICAL')               AS technical,
            ROUND(COUNT(*) FILTER (WHERE u.churn_type = 'VOLUNTARY') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                    AS voluntary_pct,
            ROUND(COUNT(*) FILTER (WHERE u.churn_type = 'TECHNICAL') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                    AS technical_pct,
            COUNT(*) FILTER (WHERE u.days_since_subscription = 1)            AS dropoff_day1,
            COUNT(*) FILTER (WHERE u.days_since_subscription = 2)            AS dropoff_day2,
            COUNT(*) FILTER (WHERE u.days_since_subscription = 3)            AS dropoff_day3,
            ROUND(
                COUNT(*) FILTER (
                    WHERE u.unsubscription_datetime BETWEEN :start_dt AND :end_dt
                ) * 100.0
                / NULLIF((
                    SELECT COUNT(*) FROM subscriptions WHERE status = 'active'
                ), 0), 2
            )                                                                AS churn_rate_month_pct
        FROM unsubscriptions u
        JOIN subscriptions s ON s.id = u.subscription_id
        WHERE u.unsubscription_datetime
              BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
        {sf_churn}
    """), params).fetchone()

    revenue = db.execute(text(f"""
        SELECT
            ROUND(SUM(st.price) FILTER (WHERE be.status = 'SUCCESS'), 2)      AS total_revenue,
            COUNT(*) FILTER (WHERE be.status = 'SUCCESS')                     AS success_events,
            COUNT(*) FILTER (WHERE be.status = 'FAILED')                      AS failed_events,
            ROUND(COUNT(*) FILTER (WHERE be.status = 'FAILED') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                     AS failed_pct,
            ROUND(SUM(st.price) FILTER (
                WHERE be.status = 'SUCCESS'
                AND be.event_datetime BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
            ), 2)                                                              AS mrr,
            ROUND(
                SUM(st.price) FILTER (
                    WHERE be.status = 'SUCCESS'
                    AND be.event_datetime BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
                ) / NULLIF(COUNT(DISTINCT be.user_id) FILTER (
                    WHERE be.status = 'SUCCESS'
                    AND be.event_datetime BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
                ), 0), 2
            )                                                                  AS arpu_current_month
        FROM billing_events be
        JOIN subscriptions  s   ON s.id   = be.subscription_id
        JOIN services       srv ON srv.id = s.service_id
        JOIN service_types  st  ON st.id  = srv.service_type_id
        WHERE be.event_datetime
              BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
        {sf_rev}
    """), params).fetchone()

    engagement = db.execute(text(f"""
        SELECT
            COUNT(DISTINCT user_id) FILTER (
                WHERE DATE(activity_datetime) = :end_dt
            )                                                    AS dau_today,
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime
                      BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
            )                                                    AS mau_current_month,
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime
                      BETWEEN :end_dt - INTERVAL '7 days'
                          AND :end_dt + INTERVAL '1 day'
            )                                                    AS wau_current_week
        FROM user_activities
        WHERE activity_datetime
              BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
        {sf_eng}
    """), params).fetchone()

    dau        = engagement.dau_today         or 0
    mau        = engagement.mau_current_month or 0
    stickiness = round((dau / mau * 100), 1)  if mau > 0 else 0.0

    top_services = db.execute(text(f"""
        SELECT
            srv.name                                             AS service_name,
            COUNT(*) FILTER (WHERE s.status = 'active')         AS active_subs,
            COUNT(*) FILTER (WHERE s.status = 'cancelled')      AS churned_subs,
            ROUND(
                COUNT(*) FILTER (WHERE s.status = 'cancelled') * 100.0
                / NULLIF(COUNT(*), 0), 1
            )                                                    AS churn_rate_pct
        FROM subscriptions s
        JOIN services srv ON srv.id = s.service_id
        WHERE s.subscription_start_date BETWEEN :start_dt AND :end_dt
        {sf_top}
        GROUP BY srv.name
        ORDER BY active_subs DESC
    """), params).fetchall()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "filters_applied": {
            "start_date": start_dt.isoformat(),
            "end_date":   end_dt.isoformat(),
            "service_id": service_id,
        },
        "users": {
            "total":            users.total_users,
            "active":           users.active_users,
            "inactive":         users.inactive_users,
            "new_last_30_days": users.new_last_30_days,
        },
        "subscriptions": {
            "total":               subs.total,
            "active":              subs.active,
            "trial":               subs.trial,
            "expired":             subs.expired,
            "cancelled":           subs.cancelled,
            "conversion_rate_pct": float(subs.conversion_rate_pct or 0),
        },
        "churn": {
            "total":                churn.total_unsubs,
            "voluntary":            churn.voluntary,
            "technical":            churn.technical,
            "voluntary_pct":        float(churn.voluntary_pct        or 0),
            "technical_pct":        float(churn.technical_pct        or 0),
            "churn_rate_month_pct": float(churn.churn_rate_month_pct or 0),
            "dropoff": {
                "day1": churn.dropoff_day1,
                "day2": churn.dropoff_day2,
                "day3": churn.dropoff_day3,
            },
        },
        "revenue": {
            "total_revenue":      float(revenue.total_revenue      or 0),
            "mrr":                float(revenue.mrr                or 0),
            "arpu_current_month": float(revenue.arpu_current_month or 0),
            "billing_success":    revenue.success_events,
            "billing_failed":     revenue.failed_events,
            "failed_pct":         float(revenue.failed_pct         or 0),
        },
        "engagement": {
            "dau_today":         dau,
            "wau_current_week":  engagement.wau_current_week or 0,
            "mau_current_month": mau,
            "stickiness_pct":    stickiness,
        },
        "top_services": [
            {
                "name":           row.service_name,
                "active_subs":    row.active_subs,
                "churned_subs":   row.churned_subs,
                "churn_rate_pct": float(row.churn_rate_pct or 0),
            }
            for row in top_services
        ],
    }