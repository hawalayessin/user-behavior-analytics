import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from datetime import date
from typing import Optional

from app.core.database import SessionLocal, get_db
from app.core.date_ranges import resolve_date_range
from app.utils.temporal import (
    get_data_anchor,
    get_day_window,
    get_default_window,
    get_month_window,
    get_week_window,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])

_summary_executor = ThreadPoolExecutor(max_workers=7)


async def _run_in_thread(func, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_summary_executor, lambda: func(*args))


def _summary_users_block(params: dict):
    db = SessionLocal()
    try:
        return db.execute(text("""
            SELECT
                COUNT(*)                                                          AS total_users,
                COUNT(*) FILTER (WHERE status = 'active')                         AS active_users,
                COUNT(*) FILTER (WHERE status = 'inactive')                       AS inactive_users,
                COUNT(*) FILTER (WHERE created_at BETWEEN :last30_start_dt AND :last30_end_dt) AS new_last_30_days
            FROM users
        """), params).fetchone()
    finally:
        db.close()


def _summary_subscriptions_block(params: dict, service_id: Optional[str]):
    sf_subs = "AND s.service_id = CAST(:service_id AS uuid)" if service_id else ""
    db = SessionLocal()
    try:
        return db.execute(text(f"""
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
    finally:
        db.close()


def _summary_churn_block(params: dict, service_id: Optional[str]):
    sf_churn_active = "AND s.service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_churn_rows = "AND u.service_id = CAST(:service_id AS uuid)" if service_id else ""
    db = SessionLocal()
    try:
        return db.execute(text(f"""
            WITH active_start AS (
                SELECT COUNT(DISTINCT s.id) AS active_count
                FROM subscriptions s
                WHERE s.subscription_start_date <= :churn_month_start_dt
                    AND (s.subscription_end_date IS NULL OR s.subscription_end_date > :churn_month_start_dt)
                                        {sf_churn_active}
            ),
            churn_rows AS (
                SELECT
                                        u.subscription_id,
                                        u.service_id,
                                        u.unsubscription_datetime AS churn_dt,
                                        u.churn_type AS churn_type,
                    COALESCE(
                      u.days_since_subscription,
                                            EXTRACT(DAY FROM (u.unsubscription_datetime - s.subscription_start_date))::int
                    ) AS days_since_subscription
                                FROM unsubscriptions u
                                JOIN subscriptions s ON s.id = u.subscription_id
                                WHERE u.unsubscription_datetime BETWEEN :churn_month_start_dt AND :churn_month_end_dt
                                    {sf_churn_rows}
            )
            SELECT
                COUNT(*)                                                         AS total_unsubs,
                COUNT(*) FILTER (WHERE churn_type = 'VOLUNTARY')                 AS voluntary,
                COUNT(*) FILTER (WHERE churn_type = 'TECHNICAL')                 AS technical,
                ROUND(COUNT(*) FILTER (WHERE churn_type = 'VOLUNTARY') * 100.0
                    / NULLIF(COUNT(*), 0), 1)                                    AS voluntary_pct,
                ROUND(COUNT(*) FILTER (WHERE churn_type = 'TECHNICAL') * 100.0
                    / NULLIF(COUNT(*), 0), 1)                                    AS technical_pct,
                COUNT(*) FILTER (WHERE days_since_subscription = 1)              AS dropoff_day1,
                COUNT(*) FILTER (WHERE days_since_subscription = 2)              AS dropoff_day2,
                COUNT(*) FILTER (WHERE days_since_subscription = 3)              AS dropoff_day3,
                ROUND(
                    COUNT(*) FILTER (
                        WHERE churn_dt BETWEEN :churn_month_start_dt AND :churn_month_end_dt
                    ) * 100.0
                    / NULLIF((SELECT active_count FROM active_start), 0), 2
                )                                                                AS churn_rate_month_pct
            FROM churn_rows
        """), params).fetchone()
    finally:
        db.close()


def _summary_revenue_block(params: dict, service_id: Optional[str]):
    sf_rev = "AND srv.id = CAST(:service_id AS uuid)" if service_id else ""
    revenue_query = text(f"""
            SELECT
                ROUND(SUM(st.price) FILTER (WHERE be.status = 'success'), 2)      AS total_revenue,
                COUNT(*) FILTER (WHERE be.status = 'success')                     AS success_events,
                COUNT(*) FILTER (WHERE be.status = 'failed')                      AS failed_events,
                COUNT(*) FILTER (WHERE be.status IN ('failed', 'cancelled', 'pending')) AS non_success_events,
                ROUND(COUNT(*) FILTER (WHERE be.status = 'failed') * 100.0
                    / NULLIF(COUNT(*), 0), 1)                                     AS failed_pct,
                ROUND(SUM(st.price) FILTER (
                    WHERE be.status = 'success'
                    AND be.event_datetime BETWEEN :billing_month_start_dt AND :billing_month_end_dt
                ), 2)                                                              AS mrr,
                ROUND(
                    SUM(st.price) FILTER (
                        WHERE be.status = 'success'
                        AND be.event_datetime BETWEEN :billing_month_start_dt AND :billing_month_end_dt
                    ) / NULLIF(COUNT(DISTINCT s.user_id) FILTER (
                        WHERE be.status = 'success'
                        AND be.event_datetime BETWEEN :billing_month_start_dt AND :billing_month_end_dt
                    ), 0), 2
                )                                                                  AS arpu_current_month
            FROM billing_events be
            JOIN subscriptions  s   ON s.id   = be.subscription_id
            JOIN services       srv ON srv.id = s.service_id
            JOIN service_types  st  ON st.id  = srv.service_type_id
            WHERE 1=1 {sf_rev}
        """)
    db = SessionLocal()
    try:
        try:
            return db.execute(revenue_query, params).fetchone()
        except OperationalError as exc:
            # Keep /analytics/summary resilient when the DB enforces short statement_timeout.
            if "statement timeout" not in str(exc).lower():
                raise
            db.rollback()
            db.execute(text("SET LOCAL statement_timeout = 0"))
            return db.execute(revenue_query, params).fetchone()
    finally:
        db.close()


def _summary_engagement_block(params: dict, service_id: Optional[str]):
    sf_eng = "AND service_id = CAST(:service_id AS uuid)" if service_id else ""
    db = SessionLocal()
    try:
        return db.execute(text(f"""
            SELECT
                COUNT(DISTINCT user_id) FILTER (
                    WHERE activity_datetime BETWEEN :usage_day_start_dt AND :usage_day_end_dt
                )                                                    AS dau_today,
                COUNT(DISTINCT user_id) FILTER (
                    WHERE activity_datetime BETWEEN :usage_month_start_dt AND :usage_month_end_dt
                )                                                    AS mau_current_month,
                COUNT(DISTINCT user_id) FILTER (
                    WHERE activity_datetime BETWEEN :usage_week_start_dt AND :usage_week_end_dt
                )                                                    AS wau_current_week
            FROM user_activities
            WHERE 1=1 {sf_eng}
        """), params).fetchone()
    finally:
        db.close()


def _summary_top_services_block():
    db = SessionLocal()
    try:
        return db.execute(text("""
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
        """), {}).fetchall()
    finally:
        db.close()


def _summary_sms_block(params: dict, service_id: Optional[str]):
    sf_sms = "AND se.service_id = CAST(:service_id AS uuid)" if service_id else ""
    db = SessionLocal()
    try:
        return db.execute(text(f"""
            WITH anchor AS (
                SELECT MAX(event_datetime) AS ts
                FROM sms_events
            ),
            cur AS (
                SELECT se.*
                FROM sms_events se
                CROSS JOIN anchor a
                WHERE a.ts IS NOT NULL
                  AND se.event_datetime > a.ts - (:sms_window_days || ' days')::interval
                  AND se.event_datetime <= a.ts
                  {sf_sms}
            ),
            prev AS (
                SELECT se.*
                FROM sms_events se
                CROSS JOIN anchor a
                WHERE a.ts IS NOT NULL
                  AND se.event_datetime > a.ts - ((:sms_window_days * 2) || ' days')::interval
                  AND se.event_datetime <= a.ts - (:sms_window_days || ' days')::interval
                  {sf_sms}
            ),
            cur_rates AS (
                SELECT
                    COALESCE(
                        ROUND(COUNT(*) FILTER (WHERE is_otp = true) * 100.0 / NULLIF(COUNT(*), 0), 1),
                        0
                    ) AS otp_templates_pct,
                    COALESCE(
                        ROUND(COUNT(*) FILTER (WHERE is_activation = true) * 100.0 / NULLIF(COUNT(*), 0), 1),
                        0
                    ) AS activation_templates_pct,
                    COALESCE(
                        ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT service_id), 0), 1),
                        0
                    ) AS templates_per_service,
                    COUNT(*) AS total_templates,
                    COUNT(DISTINCT service_id) AS total_services
                FROM cur
            ),
            prev_rates AS (
                SELECT
                    COALESCE(
                        ROUND(COUNT(*) FILTER (WHERE is_otp = true) * 100.0 / NULLIF(COUNT(*), 0), 1),
                        0
                    ) AS otp_templates_pct,
                    COALESCE(
                        ROUND(COUNT(*) FILTER (WHERE is_activation = true) * 100.0 / NULLIF(COUNT(*), 0), 1),
                        0
                    ) AS activation_templates_pct
                FROM prev
            )
            SELECT
                cr.otp_templates_pct AS otp_templates_pct,
                cr.activation_templates_pct AS activation_templates_pct,
                ROUND(cr.otp_templates_pct - pr.otp_templates_pct, 1) AS otp_rate_trend_pct,
                ROUND(cr.activation_templates_pct - pr.activation_templates_pct, 1) AS activation_rate_trend_pct,
                cr.templates_per_service AS templates_per_service,
                cr.total_templates AS total_templates,
                cr.total_services AS total_services
            FROM cur_rates cr
            CROSS JOIN prev_rates pr
        """), params).fetchone()
    finally:
        db.close()


# ══════════════════════════════════════════════════════════════════
# GET /analytics/summary  — données globales SANS filtre de date
# ══════════════════════════════════════════════════════════════════
@router.get("/summary")
async def get_summary(
    db:         Session = Depends(get_db),
    service_id: Optional[str] = Query(default=None),
):
    summary_anchor = get_data_anchor(db, source="analytics")
    last30_start, last30_end = get_default_window(db, days=30, source="analytics")
    usage_month_start, usage_month_end = get_month_window(db, source="usage")
    usage_week_start, usage_week_end = get_week_window(db, source="usage")
    usage_day_start, usage_day_end = get_day_window(db, source="usage")
    billing_month_start, billing_month_end = get_month_window(db, source="billing")
    churn_month_start, churn_month_end = get_default_window(db, days=30, source="billing")

    params  = {
        "service_id": service_id,
        "last30_start_dt": last30_start,
        "last30_end_dt": last30_end,
        "usage_month_start_dt": usage_month_start,
        "usage_month_end_dt": usage_month_end,
        "usage_week_start_dt": usage_week_start,
        "usage_week_end_dt": usage_week_end,
        "usage_day_start_dt": usage_day_start,
        "usage_day_end_dt": usage_day_end,
        "billing_month_start_dt": billing_month_start,
        "billing_month_end_dt": billing_month_end,
        "churn_month_start_dt": churn_month_start,
        "churn_month_end_dt": churn_month_end,
        "sms_window_days": 30,
    }
    users, subs, churn, revenue, engagement, top_services, sms = await asyncio.gather(
        _run_in_thread(_summary_users_block, params),
        _run_in_thread(_summary_subscriptions_block, params, service_id),
        _run_in_thread(_summary_churn_block, params, service_id),
        _run_in_thread(_summary_revenue_block, params, service_id),
        _run_in_thread(_summary_engagement_block, params, service_id),
        _run_in_thread(_summary_top_services_block),
        _run_in_thread(_summary_sms_block, params, service_id),
    )

    dau        = engagement.dau_today         or 0
    mau        = engagement.mau_current_month or 0
    stickiness = round((dau / mau * 100), 1)  if mau > 0 else 0.0
    failure_data_note = (
        "N/A - aucun echec enregistre dans la source"
        if int(revenue.non_success_events or 0) == 0 and int(revenue.success_events or 0) > 0
        else None
    )

    return {
        "generated_at": summary_anchor.isoformat(),
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
            "failed_pct":         None if failure_data_note else float(revenue.failed_pct or 0),
            "failure_data_note":  failure_data_note,
        },
        "engagement": {
            "dau_today":         dau,
            "wau_current_week":  engagement.wau_current_week or 0,
            "mau_current_month": mau,
            "stickiness_pct":    stickiness,
        },
        "sms": {
            "otp_templates_pct":         float(sms.otp_templates_pct or 0),
            "activation_templates_pct":  float(sms.activation_templates_pct or 0),
            "otp_rate_trend_pct":        float(sms.otp_rate_trend_pct or 0),
            "activation_rate_trend_pct": float(sms.activation_rate_trend_pct or 0),
            "templates_per_service":     float(sms.templates_per_service or 0),
            "total_templates":           int(sms.total_templates or 0),
            "total_services":            int(sms.total_services or 0),
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
    start_dt, end_dt = resolve_date_range(start_date, end_date, db=db, source="analytics")

    usage_day_start, usage_day_end = get_day_window(db, source="usage")
    usage_week_start, usage_week_end = get_week_window(db, source="usage")
    usage_month_start, usage_month_end = get_month_window(db, source="usage")
    data_anchor = get_data_anchor(db, source="billing")

    if start_date is None and end_date is None:
        churn_window_start, churn_window_end = get_default_window(db, days=30, source="billing")
        sms_window_days = 30
    else:
        churn_window_start = start_dt
        churn_window_end = end_dt
        sms_window_days = max((end_dt - start_dt).days + 1, 1)

    params = {
        "start_dt": start_dt,
        "end_dt": end_dt,
        "churn_window_start_dt": churn_window_start,
        "churn_window_end_dt": churn_window_end,
        "service_id": service_id,
        "usage_day_start_dt": usage_day_start,
        "usage_day_end_dt": usage_day_end,
        "usage_week_start_dt": usage_week_start,
        "usage_week_end_dt": usage_week_end,
        "usage_month_start_dt": usage_month_start,
        "usage_month_end_dt": usage_month_end,
        "sms_window_days": sms_window_days,
    }

    sf_subs = "AND srv.id = CAST(:service_id AS uuid)" if service_id else ""
    sf_churn_active = "AND s.service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_churn_rows = "AND u.service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_rev = "AND srv.id = CAST(:service_id AS uuid)" if service_id else ""
    sf_eng = "AND service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_top = "AND srv.id = CAST(:service_id AS uuid)" if service_id else ""
    sj_subs = "JOIN services srv ON srv.id = s.service_id" if service_id else ""

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
                WITH active_start AS (
                    SELECT COUNT(DISTINCT s.id) AS active_count
                    FROM subscriptions s
                    WHERE s.subscription_start_date <= :churn_window_start_dt
                        AND (s.subscription_end_date IS NULL OR s.subscription_end_date > :churn_window_start_dt)
                                                {sf_churn_active}
                ),
                churn_rows AS (
          SELECT
                        u.subscription_id,
                        u.service_id,
                        u.unsubscription_datetime AS churn_dt,
                        u.churn_type AS churn_type,
            COALESCE(
              u.days_since_subscription,
                            EXTRACT(DAY FROM (u.unsubscription_datetime - s.subscription_start_date))::int
            ) AS days_since_subscription
                    FROM unsubscriptions u
                    JOIN subscriptions s ON s.id = u.subscription_id
                    WHERE u.unsubscription_datetime BETWEEN :churn_window_start_dt AND :churn_window_end_dt + INTERVAL '1 day'
                        {sf_churn_rows}
        )
        SELECT
            COUNT(*)                                                         AS total_unsubs,
            COUNT(*) FILTER (WHERE churn_type = 'VOLUNTARY')                 AS voluntary,
            COUNT(*) FILTER (WHERE churn_type = 'TECHNICAL')                 AS technical,
            ROUND(COUNT(*) FILTER (WHERE churn_type = 'VOLUNTARY') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                    AS voluntary_pct,
            ROUND(COUNT(*) FILTER (WHERE churn_type = 'TECHNICAL') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                    AS technical_pct,
            COUNT(*) FILTER (WHERE days_since_subscription = 1)              AS dropoff_day1,
            COUNT(*) FILTER (WHERE days_since_subscription = 2)              AS dropoff_day2,
            COUNT(*) FILTER (WHERE days_since_subscription = 3)              AS dropoff_day3,
            ROUND(
                COUNT(*) FILTER (
                    WHERE churn_dt BETWEEN :churn_window_start_dt AND :churn_window_end_dt + INTERVAL '1 day'
                ) * 100.0
                / NULLIF((SELECT active_count FROM active_start), 0), 2
            )                                                                AS churn_rate_month_pct
        FROM churn_rows
    """), params).fetchone()

    revenue = db.execute(text(f"""
        SELECT
            ROUND(SUM(st.price) FILTER (WHERE be.status = 'success'), 2)      AS total_revenue,
            COUNT(*) FILTER (WHERE be.status = 'success')                     AS success_events,
            COUNT(*) FILTER (WHERE be.status = 'failed')                      AS failed_events,
            COUNT(*) FILTER (WHERE be.status IN ('failed', 'cancelled', 'pending')) AS non_success_events,
            ROUND(COUNT(*) FILTER (WHERE be.status = 'failed') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                     AS failed_pct,
            ROUND(SUM(st.price) FILTER (
                WHERE be.status = 'success'
                AND be.event_datetime BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
            ), 2)                                                              AS mrr,
            ROUND(
                SUM(st.price) FILTER (
                    WHERE be.status = 'success'
                    AND be.event_datetime BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
                ) / NULLIF(COUNT(DISTINCT s.user_id) FILTER (
                    WHERE be.status = 'success'
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
                WHERE activity_datetime BETWEEN :usage_day_start_dt AND :usage_day_end_dt
            )                                                    AS dau_today,
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime BETWEEN :usage_month_start_dt AND :usage_month_end_dt
            )                                                    AS mau_current_month,
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime BETWEEN :usage_week_start_dt AND :usage_week_end_dt
            )                                                    AS wau_current_week
        FROM user_activities
        WHERE activity_datetime BETWEEN :usage_month_start_dt AND :usage_month_end_dt
        {sf_eng}
    """), params).fetchone()

    dau        = engagement.dau_today         or 0
    mau        = engagement.mau_current_month or 0
    stickiness = round((dau / mau * 100), 1)  if mau > 0 else 0.0
    failure_data_note = (
        "N/A - aucun echec enregistre dans la source"
        if int(revenue.non_success_events or 0) == 0 and int(revenue.success_events or 0) > 0
        else None
    )

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

    sms = db.execute(text(f"""
        WITH anchor AS (
            SELECT MAX(event_datetime) AS ts
            FROM sms_events
        ),
        cur AS (
            SELECT se.*
            FROM sms_events se
            CROSS JOIN anchor a
            WHERE a.ts IS NOT NULL
              AND se.event_datetime > a.ts - (:sms_window_days || ' days')::interval
              AND se.event_datetime <= a.ts
              {"AND se.service_id = CAST(:service_id AS uuid)" if service_id else ""}
        ),
        prev AS (
            SELECT se.*
            FROM sms_events se
            CROSS JOIN anchor a
            WHERE a.ts IS NOT NULL
              AND se.event_datetime > a.ts - ((:sms_window_days * 2) || ' days')::interval
              AND se.event_datetime <= a.ts - (:sms_window_days || ' days')::interval
              {"AND se.service_id = CAST(:service_id AS uuid)" if service_id else ""}
        ),
        cur_rates AS (
            SELECT
                COALESCE(
                    ROUND(COUNT(*) FILTER (WHERE is_otp = true) * 100.0 / NULLIF(COUNT(*), 0), 1),
                    0
                ) AS otp_templates_pct,
                COALESCE(
                    ROUND(COUNT(*) FILTER (WHERE is_activation = true) * 100.0 / NULLIF(COUNT(*), 0), 1),
                    0
                ) AS activation_templates_pct,
                COALESCE(
                    ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT service_id), 0), 1),
                    0
                ) AS templates_per_service,
                COUNT(*) AS total_templates,
                COUNT(DISTINCT service_id) AS total_services
            FROM cur
        ),
        prev_rates AS (
            SELECT
                COALESCE(
                    ROUND(COUNT(*) FILTER (WHERE is_otp = true) * 100.0 / NULLIF(COUNT(*), 0), 1),
                    0
                ) AS otp_templates_pct,
                COALESCE(
                    ROUND(COUNT(*) FILTER (WHERE is_activation = true) * 100.0 / NULLIF(COUNT(*), 0), 1),
                    0
                ) AS activation_templates_pct
            FROM prev
        )
        SELECT
            cr.otp_templates_pct AS otp_templates_pct,
            cr.activation_templates_pct AS activation_templates_pct,
            ROUND(cr.otp_templates_pct - pr.otp_templates_pct, 1) AS otp_rate_trend_pct,
            ROUND(cr.activation_templates_pct - pr.activation_templates_pct, 1) AS activation_rate_trend_pct,
            cr.templates_per_service AS templates_per_service,
            cr.total_templates AS total_templates,
            cr.total_services AS total_services
        FROM cur_rates cr
        CROSS JOIN prev_rates pr
    """), params).fetchone()

    return {
        "generated_at": data_anchor.isoformat(),
        "data_anchor": data_anchor.strftime("%Y-%m-%d"),
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
            "failed_pct":         None if failure_data_note else float(revenue.failed_pct or 0),
            "failure_data_note":  failure_data_note,
        },
        "engagement": {
            "dau_today":         dau,
            "wau_current_week":  engagement.wau_current_week or 0,
            "mau_current_month": mau,
            "stickiness_pct":    stickiness,
        },
        "sms": {
            "otp_templates_pct":         float(sms.otp_templates_pct or 0),
            "activation_templates_pct":  float(sms.activation_templates_pct or 0),
            "otp_rate_trend_pct":        float(sms.otp_rate_trend_pct or 0),
            "activation_rate_trend_pct": float(sms.activation_rate_trend_pct or 0),
            "templates_per_service":     float(sms.templates_per_service or 0),
            "total_templates":           int(sms.total_templates or 0),
            "total_services":            int(sms.total_services or 0),
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