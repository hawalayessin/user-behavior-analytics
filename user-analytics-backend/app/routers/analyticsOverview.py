import asyncio
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from datetime import date, datetime, time, timedelta
from typing import Optional

from app.core.cache import (
    build_cache_key,
    cache_get_json,
    cache_get_or_set_json,
    cache_or_compute,
    invalidate_analytics_cache,
    cache_set_json,
)
from app.core.database import SessionLocal, get_db
from app.core.config import settings
from app.core.dependencies import require_admin
from app.core.date_ranges import resolve_date_range
from app.utils.temporal import (
    get_data_anchor,
    get_day_window,
    get_default_window,
    get_month_window,
    get_week_window,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])

OVERVIEW_CACHE_VERSION = "2026-04-16-churn-rate-base-v5"

_summary_executor = ThreadPoolExecutor(max_workers=7)


async def _run_in_thread(func, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_summary_executor, lambda: func(*args))


def _exec_with_timeout_retry(db: Session, sql_text, params: dict):
    try:
        return db.execute(sql_text, params)
    except OperationalError as exc:
        if "statement timeout" not in str(exc).lower():
            raise
        db.rollback()
        db.execute(text("SET LOCAL statement_timeout = 0"))
        return db.execute(sql_text, params)


def _analytics_cache_key(block: str, params: dict, service_id: Optional[str]) -> str:
    parts = [
        "analytics",
        "summary",
        block,
        service_id or "all",
        str(params.get("last30_start_dt", "")),
        str(params.get("last30_end_dt", "")),
        str(params.get("usage_month_start_dt", "")),
        str(params.get("usage_month_end_dt", "")),
        str(params.get("usage_week_start_dt", "")),
        str(params.get("usage_week_end_dt", "")),
        str(params.get("usage_day_start_dt", "")),
        str(params.get("usage_day_end_dt", "")),
        str(params.get("billing_month_start_dt", "")),
        str(params.get("billing_month_end_dt", "")),
        str(params.get("churn_month_start_dt", "")),
        str(params.get("churn_month_end_dt", "")),
        str(params.get("sms_window_days", "")),
    ]
    return ":".join(parts)


def _to_namespace_row(cached: dict | None):
    if cached is None:
        return None
    return SimpleNamespace(**cached)


def _to_namespace_rows(cached: list[dict] | None):
    if cached is None:
        return None
    return [SimpleNamespace(**item) for item in cached]


def _summary_users_block(params: dict):
    cache_key = _analytics_cache_key("users", params, None)
    cached = _to_namespace_row(cache_get_json(cache_key))
    if cached is not None:
        return cached

    db = SessionLocal()
    try:
        row = db.execute(text("""
            SELECT
                COUNT(*)                                                          AS total_users,
                COUNT(*) FILTER (WHERE status = 'active')                         AS active_users,
                COUNT(*) FILTER (WHERE status = 'inactive')                       AS inactive_users,
                COUNT(*) FILTER (WHERE created_at BETWEEN :last30_start_dt AND :last30_end_dt) AS new_last_30_days
            FROM users
        """), params).fetchone()
        if row is not None:
            cache_set_json(
                cache_key,
                dict(row._mapping),
                settings.ANALYTICS_CACHE_TTL_SECONDS,
            )
        return row
    finally:
        db.close()


def _summary_subscriptions_block(params: dict, service_id: Optional[str]):
    cache_key = _analytics_cache_key("subscriptions", params, service_id)
    cached = _to_namespace_row(cache_get_json(cache_key))
    if cached is not None:
        return cached

    sf_subs = "AND s.service_id = CAST(:service_id AS uuid)" if service_id else ""
    db = SessionLocal()
    try:
        query = text(f"""
            WITH normalized_subs AS (
                SELECT
                    s.user_id,
                    s.subscription_start_date,
                    CASE
                        WHEN LOWER(TRIM(COALESCE(s.status, ''))) IN ('1', 'active', 'subscribed', 'iscrit', 'inscrit')
                            THEN 'subscribed'
                        WHEN LOWER(TRIM(COALESCE(s.status, ''))) IN ('-2', 'billing_failed', 'iscrit avec billing failure', 'inscrit avec billing failure', 'at_risk')
                            THEN 'billing_failed'
                        WHEN LOWER(TRIM(COALESCE(s.status, ''))) IN ('-1', 'cancelled', 'expired', 'inactive', 'unsubscribed', 'desinscrit', 'désinscrit', 'churned')
                            THEN 'unsubscribed'
                        WHEN LOWER(TRIM(COALESCE(s.status, ''))) IN ('0', 'pending', 'trial', 'otp_pending', 'otp non terminer')
                            THEN 'otp_incomplete'
                        ELSE 'unknown'
                    END AS norm_status
                FROM subscriptions s
                WHERE 1=1 {sf_subs}
            )
            SELECT
                COUNT(*) FILTER (WHERE ns.norm_status != 'otp_incomplete') AS total,
                COUNT(*)                                                    AS total_with_pending,
                COUNT(*) FILTER (WHERE ns.norm_status = 'subscribed')      AS active,
                COUNT(*) FILTER (WHERE ns.norm_status = 'billing_failed')  AS billing_failed,
                COUNT(*) FILTER (WHERE ns.norm_status = 'unsubscribed')    AS cancelled,
                COUNT(*) FILTER (WHERE ns.norm_status = 'otp_incomplete')  AS pending,
                COUNT(DISTINCT ns.user_id) FILTER (WHERE ns.norm_status = 'subscribed')     AS active_users,
                COUNT(DISTINCT ns.user_id) FILTER (WHERE ns.norm_status = 'billing_failed') AS at_risk_users,
                COUNT(*) FILTER (
                    WHERE ns.subscription_start_date BETWEEN :last30_start_dt AND :last30_end_dt
                      AND ns.norm_status != 'otp_incomplete'
                ) AS new_last_30_days,
                ROUND(
                    COUNT(*) FILTER (WHERE ns.norm_status = 'subscribed') * 100.0
                    / NULLIF(COUNT(*) FILTER (WHERE ns.norm_status != 'otp_incomplete'), 0), 1
                )                                                      AS conversion_rate_pct
            FROM normalized_subs ns
        """)
        row = _exec_with_timeout_retry(db, query, params).fetchone()
        if row is not None:
            cache_set_json(
                cache_key,
                dict(row._mapping),
                settings.ANALYTICS_CACHE_TTL_SECONDS,
            )
        return row
    finally:
        db.close()


def _summary_churn_block(params: dict, service_id: Optional[str]):
    cache_key = _analytics_cache_key("churn", params, service_id)
    cached = _to_namespace_row(cache_get_json(cache_key))
    if cached is not None:
        return cached

    sf_churn_active = "AND s.service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_churn_rows = "AND u.service_id = CAST(:service_id AS uuid)" if service_id else ""
    db = SessionLocal()
    try:
        row = db.execute(text(f"""
            WITH exposure_base AS (
                SELECT
                    COUNT(DISTINCT s.id) FILTER (
                        WHERE s.subscription_start_date <= :churn_month_start_dt
                          AND (s.subscription_end_date IS NULL OR s.subscription_end_date > :churn_month_start_dt)
                    ) AS active_at_start,
                    COUNT(DISTINCT s.id) FILTER (
                        WHERE s.subscription_start_date > :churn_month_start_dt
                          AND s.subscription_start_date <= :churn_month_end_dt + INTERVAL '1 day'
                          AND s.status != 'pending'
                    ) AS new_in_window
                FROM subscriptions s
                WHERE 1=1
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
                WHERE u.unsubscription_datetime BETWEEN :churn_month_start_dt AND :churn_month_end_dt + INTERVAL '1 day'
                  {sf_churn_rows}
            )
            SELECT
                COUNT(DISTINCT subscription_id)                                            AS total_unsubs,
                COUNT(DISTINCT subscription_id) FILTER (WHERE churn_type = 'VOLUNTARY')    AS voluntary,
                COUNT(DISTINCT subscription_id) FILTER (WHERE churn_type = 'TECHNICAL')    AS technical,
                ROUND(
                    COUNT(DISTINCT subscription_id) FILTER (WHERE churn_type = 'VOLUNTARY') * 100.0
                    / NULLIF(COUNT(DISTINCT subscription_id), 0),
                    1
                )                                                                           AS voluntary_pct,
                ROUND(
                    COUNT(DISTINCT subscription_id) FILTER (WHERE churn_type = 'TECHNICAL') * 100.0
                    / NULLIF(COUNT(DISTINCT subscription_id), 0),
                    1
                )                                                                           AS technical_pct,
                COUNT(DISTINCT subscription_id) FILTER (WHERE days_since_subscription = 1)  AS dropoff_day1,
                COUNT(DISTINCT subscription_id) FILTER (WHERE days_since_subscription = 2)  AS dropoff_day2,
                COUNT(DISTINCT subscription_id) FILTER (WHERE days_since_subscription = 3)  AS dropoff_day3,
                ROUND(
                    COUNT(DISTINCT subscription_id) * 100.0
                    / NULLIF(
                        (SELECT COALESCE(active_at_start, 0) + COALESCE(new_in_window, 0) FROM exposure_base),
                        0
                    ),
                    2
                )                                                                           AS churn_rate_month_pct
            FROM churn_rows
        """), params).fetchone()
        if row is not None:
            cache_set_json(
                cache_key,
                dict(row._mapping),
                settings.ANALYTICS_CACHE_TTL_SECONDS,
            )
        return row
    finally:
        db.close()


def _summary_revenue_block(params: dict, service_id: Optional[str]):
    cache_key = _analytics_cache_key("revenue", params, service_id)
    cached = _to_namespace_row(cache_get_json(cache_key))
    if cached is not None:
        return cached

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
            row = db.execute(revenue_query, params).fetchone()
        except OperationalError as exc:
            # Keep /analytics/summary resilient when the DB enforces short statement_timeout.
            if "statement timeout" not in str(exc).lower():
                raise
            db.rollback()
            db.execute(text("SET LOCAL statement_timeout = 0"))
            row = db.execute(revenue_query, params).fetchone()

        if row is not None:
            cache_set_json(
                cache_key,
                dict(row._mapping),
                settings.ANALYTICS_CACHE_TTL_SECONDS,
            )
        return row
    finally:
        db.close()


def _summary_engagement_block(params: dict, service_id: Optional[str]):
    cache_key = _analytics_cache_key("engagement", params, service_id)
    cached = _to_namespace_row(cache_get_json(cache_key))
    if cached is not None:
        return cached

    sf_eng = "AND service_id = CAST(:service_id AS uuid)" if service_id else ""
    db = SessionLocal()
    try:
        row = db.execute(text(f"""
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
        if row is not None:
            cache_set_json(
                cache_key,
                dict(row._mapping),
                settings.ANALYTICS_CACHE_TTL_SECONDS,
            )
        return row
    finally:
        db.close()


def _summary_top_services_block(params: dict, service_id: Optional[str]):
    cache_key = _analytics_cache_key("top_services", params, service_id)
    cached = _to_namespace_rows(cache_get_json(cache_key))
    if cached is not None:
        return cached

    sf_top = "WHERE s.service_id = CAST(:service_id AS uuid)" if service_id else ""
    db = SessionLocal()
    try:
        rows = db.execute(text(f"""
            SELECT
                srv.name                                             AS service_name,
                COUNT(*)                                             AS total,
                COUNT(*) FILTER (WHERE s.status = 'active')         AS active_subs,
                COUNT(*) FILTER (WHERE s.status = 'billing_failed') AS billing_failed,
                COUNT(*) FILTER (WHERE s.status = 'cancelled')      AS cancelled,
                COUNT(DISTINCT s.user_id) FILTER (WHERE s.status = 'active') AS active_users,
                ROUND(
                    COUNT(*) FILTER (WHERE s.status = 'cancelled') * 100.0
                    / NULLIF(COUNT(*) FILTER (WHERE s.status != 'pending'), 0), 1
                )                                                    AS churn_rate_pct
            FROM subscriptions s
            JOIN services srv ON srv.id = s.service_id
            {sf_top}
            GROUP BY srv.name
            ORDER BY total DESC
        """), params).fetchall()
        cache_set_json(
            cache_key,
            [dict(row._mapping) for row in rows],
            settings.ANALYTICS_CACHE_TTL_SECONDS,
        )
        return rows
    finally:
        db.close()


def _summary_sms_block(params: dict, service_id: Optional[str]):
    cache_key = _analytics_cache_key("sms", params, service_id)
    cached = _to_namespace_row(cache_get_json(cache_key))
    if cached is not None:
        return cached

    sf_sms = "AND se.service_id = CAST(:service_id AS uuid)" if service_id else ""
    db = SessionLocal()
    try:
        row = db.execute(text(f"""
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
        if row is not None:
            cache_set_json(
                cache_key,
                dict(row._mapping),
                settings.ANALYTICS_CACHE_TTL_SECONDS,
            )
        return row
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
        _run_in_thread(_summary_top_services_block, params, service_id),
        _run_in_thread(_summary_sms_block, params, service_id),
    )

    dau        = engagement.dau_today         or 0
    mau        = engagement.mau_current_month or 0
    stickiness = round((dau / mau * 100), 1)  if mau > 0 else 0.0
    billing_failed_from_subs = int(subs.billing_failed or 0)
    billing_success = int(revenue.success_events or 0)
    failed_denominator = billing_success + billing_failed_from_subs
    failed_pct = (
        round((billing_failed_from_subs * 100.0) / failed_denominator, 1)
        if failed_denominator > 0
        else 0.0
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
            "total_with_pending":  subs.total_with_pending,
            "active":              subs.active,
            "billing_failed":      subs.billing_failed,
            "cancelled":           subs.cancelled,
            "pending":             subs.pending,
            "active_users":        subs.active_users,
            "at_risk_users":       subs.at_risk_users,
            "new_last_30_days":    subs.new_last_30_days,
            "trial":               subs.pending,
            "expired":             subs.billing_failed,
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
            "billing_success":    billing_success,
            "billing_failed":     billing_failed_from_subs,
            "failed_pct":         failed_pct,
            "failure_data_note":  None,
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
                "total":          row.total,
                "active_subs":    row.active_subs,
                "billing_failed":  row.billing_failed,
                "cancelled":      row.cancelled,
                "active_users":   row.active_users,
                "churned_subs":   row.cancelled,
                "churn_rate_pct": float(row.churn_rate_pct or 0),
            }
            for row in top_services
        ],
    }


# ══════════════════════════════════════════════════════════════════
# GET /analytics/overview  — données filtrées par date + service
# ══════════════════════════════════════════════════════════════════
def _compute_overview_payload(
    db: Session,
    *,
    start_dt: date,
    end_dt: date,
    start_date: Optional[date],
    end_date: Optional[date],
    service_id: Optional[str],
):
    # For filtered overview requests, engagement windows must follow the selected range.
    # Without explicit filters, keep anchor-based global windows for dashboard defaults.
    if start_date is None and end_date is None:
        usage_day_start, usage_day_end = get_day_window(db, source="usage")
        usage_week_start, usage_week_end = get_week_window(db, source="usage")
        usage_month_start, usage_month_end = get_month_window(db, source="usage")
    else:
        end_dt_ts = datetime.combine(end_dt, time.max)
        start_dt_ts = datetime.combine(start_dt, time.min)

        usage_day_end = end_dt_ts
        usage_day_start = max(start_dt_ts, end_dt_ts - timedelta(hours=24))

        usage_week_end = end_dt_ts
        usage_week_start = max(start_dt_ts, end_dt_ts - timedelta(days=7))

        month_start = end_dt_ts.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        usage_month_start = max(start_dt_ts, month_start)
        usage_month_end = end_dt_ts

    data_anchor = get_data_anchor(db, source="billing")
    usage_anchor = get_data_anchor(db, source="usage")

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

    sf_subs = "AND s.service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_churn_active = "AND s.service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_churn_rows = "AND u.service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_rev = "AND srv.id = CAST(:service_id AS uuid)" if service_id else ""
    sf_eng = "AND service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_top = "AND srv.id = CAST(:service_id AS uuid)" if service_id else ""

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

    subs_query = text(f"""
        WITH normalized_subs AS (
            SELECT
                s.user_id,
                s.subscription_start_date,
                CASE
                    WHEN LOWER(TRIM(COALESCE(s.status, ''))) IN ('1', 'active', 'subscribed', 'iscrit', 'inscrit')
                        THEN 'subscribed'
                    WHEN LOWER(TRIM(COALESCE(s.status, ''))) IN ('-2', 'billing_failed', 'iscrit avec billing failure', 'inscrit avec billing failure', 'at_risk')
                        THEN 'billing_failed'
                    WHEN LOWER(TRIM(COALESCE(s.status, ''))) IN ('-1', 'cancelled', 'expired', 'inactive', 'unsubscribed', 'desinscrit', 'désinscrit', 'churned')
                        THEN 'unsubscribed'
                    WHEN LOWER(TRIM(COALESCE(s.status, ''))) IN ('0', 'pending', 'trial', 'otp_pending', 'otp non terminer')
                        THEN 'otp_incomplete'
                    ELSE 'unknown'
                END AS norm_status
            FROM subscriptions s
            WHERE s.subscription_start_date BETWEEN :start_dt AND :end_dt
            {sf_subs}
        )
        SELECT
            COUNT(*) FILTER (WHERE ns.norm_status != 'otp_incomplete') AS total,
            COUNT(*)                                                    AS total_with_pending,
            COUNT(*) FILTER (WHERE ns.norm_status = 'subscribed')      AS active,
            COUNT(*) FILTER (WHERE ns.norm_status = 'billing_failed')  AS billing_failed,
            COUNT(*) FILTER (WHERE ns.norm_status = 'unsubscribed')    AS cancelled,
            COUNT(*) FILTER (WHERE ns.norm_status = 'otp_incomplete')  AS pending,
            COUNT(DISTINCT ns.user_id) FILTER (WHERE ns.norm_status = 'subscribed')     AS active_users,
            COUNT(DISTINCT ns.user_id) FILTER (WHERE ns.norm_status = 'billing_failed') AS at_risk_users,
            COUNT(*) FILTER (
                WHERE ns.subscription_start_date BETWEEN :start_dt AND :end_dt
                  AND ns.norm_status != 'otp_incomplete'
            ) AS new_last_30_days,
            ROUND(
                COUNT(*) FILTER (WHERE ns.norm_status = 'subscribed') * 100.0
                / NULLIF(COUNT(*) FILTER (WHERE ns.norm_status != 'otp_incomplete'), 0), 1
            )                                                      AS conversion_rate_pct
        FROM normalized_subs ns
    """)
    subs = _exec_with_timeout_retry(db, subs_query, params).fetchone()

    churn = db.execute(text(f"""
        WITH exposure_base AS (
            SELECT
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.subscription_start_date <= :churn_window_start_dt
                      AND (s.subscription_end_date IS NULL OR s.subscription_end_date > :churn_window_start_dt)
                ) AS active_at_start,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.subscription_start_date > :churn_window_start_dt
                      AND s.subscription_start_date <= :churn_window_end_dt + INTERVAL '1 day'
                      AND s.status != 'pending'
                ) AS new_in_window
            FROM subscriptions s
            WHERE 1=1
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
            COUNT(DISTINCT subscription_id)                                            AS total_unsubs,
            COUNT(DISTINCT subscription_id) FILTER (WHERE churn_type = 'VOLUNTARY')    AS voluntary,
            COUNT(DISTINCT subscription_id) FILTER (WHERE churn_type = 'TECHNICAL')    AS technical,
            ROUND(
                COUNT(DISTINCT subscription_id) FILTER (WHERE churn_type = 'VOLUNTARY') * 100.0
                / NULLIF(COUNT(DISTINCT subscription_id), 0),
                1
            )                                                                           AS voluntary_pct,
            ROUND(
                COUNT(DISTINCT subscription_id) FILTER (WHERE churn_type = 'TECHNICAL') * 100.0
                / NULLIF(COUNT(DISTINCT subscription_id), 0),
                1
            )                                                                           AS technical_pct,
            COUNT(DISTINCT subscription_id) FILTER (WHERE days_since_subscription = 1)  AS dropoff_day1,
            COUNT(DISTINCT subscription_id) FILTER (WHERE days_since_subscription = 2)  AS dropoff_day2,
            COUNT(DISTINCT subscription_id) FILTER (WHERE days_since_subscription = 3)  AS dropoff_day3,
            ROUND(
                COUNT(DISTINCT subscription_id) * 100.0
                / NULLIF(
                    (SELECT COALESCE(active_at_start, 0) + COALESCE(new_in_window, 0) FROM exposure_base),
                    0
                ),
                2
            )                                                                           AS churn_rate_month_pct
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

    sf_inactive = """
        AND EXISTS (
            SELECT 1 FROM subscriptions sub
            WHERE sub.user_id = u.id
              AND sub.service_id = CAST(:service_id AS uuid)
        )
    """ if service_id else ""

    engagement_population = db.execute(text(f"""
        WITH scoped_users AS (
            SELECT DISTINCT u.id
            FROM users u
            WHERE u.status NOT IN ('churned', 'cancelled')
            {sf_inactive}
        ),
        active_7d AS (
            SELECT DISTINCT ua.user_id
            FROM user_activities ua
            JOIN scoped_users su ON su.id = ua.user_id
            WHERE ua.activity_datetime BETWEEN :usage_week_start_dt AND :usage_week_end_dt
        )
        SELECT
            (SELECT COUNT(*) FROM scoped_users) AS scoped_users_count,
            (SELECT COUNT(*) FROM active_7d) AS active_7d_users,
            (SELECT COUNT(*) FROM scoped_users su
             LEFT JOIN active_7d a ON a.user_id = su.id
             WHERE a.user_id IS NULL) AS inactive_7d_count
    """), params).fetchone()

    # Engagement trend must follow usage anchor when no explicit filter is provided.
    # This prevents showing a recent empty window when billing/analytics anchors differ from usage.
    trend_end_date = usage_month_end.date() if (start_date is None and end_date is None) else end_dt
    trend_start_dt = max(start_dt, trend_end_date - timedelta(days=179))
    trend_rows = db.execute(text(f"""
        SELECT
            DATE(activity_datetime) AS date,
            COUNT(DISTINCT user_id) AS dau
        FROM user_activities
        WHERE activity_datetime >= CAST(:trend_start_dt AS timestamp)
          AND activity_datetime < CAST(:trend_end_dt AS timestamp) + INTERVAL '1 day'
          {sf_eng}
        GROUP BY DATE(activity_datetime)
        ORDER BY date ASC
    """), {**params, "trend_start_dt": trend_start_dt, "trend_end_dt": trend_end_date}).fetchall()

    dau_by_day = {str(row.date): int(row.dau or 0) for row in trend_rows}
    trend_dates = [
        trend_start_dt + timedelta(days=i)
        for i in range((trend_end_date - trend_start_dt).days + 1)
    ]

    dau = engagement.dau_today or 0
    mau = engagement.mau_current_month or 0
    stickiness = round((dau / mau * 100), 1) if mau > 0 else 0.0
    scoped_users_count = int(engagement_population.scoped_users_count or 0)
    active_7d_users = int(engagement_population.active_7d_users or 0)
    inactive_7d_count = int(engagement_population.inactive_7d_count or 0)
    inactivity_rate_pct = round((inactive_7d_count * 100.0 / scoped_users_count), 1) if scoped_users_count > 0 else 0.0

    stickiness_target_pct = 30.0
    stickiness_component = min((stickiness / stickiness_target_pct) * 100.0, 100.0) if stickiness_target_pct > 0 else 0.0
    inactivity_health = max(0.0, 100.0 - inactivity_rate_pct)
    engagement_score = round((0.65 * stickiness_component) + (0.35 * inactivity_health), 1)

    if engagement_score >= 70:
        engagement_level = "high"
    elif engagement_score >= 45:
        engagement_level = "medium"
    else:
        engagement_level = "low"

    engagement_trend = []
    rolling_window: list[int] = []
    rolling_sum = 0
    for d in trend_dates:
        key = d.isoformat()
        day_dau = dau_by_day.get(key, 0)
        rolling_window.append(day_dau)
        rolling_sum += day_dau
        if len(rolling_window) > 7:
            rolling_sum -= rolling_window.pop(0)
        wau_7d_avg = round(rolling_sum / len(rolling_window), 1) if rolling_window else 0.0
        engagement_trend.append({
            "date": key,
            "dau": day_dau,
            "wau_7d_avg": wau_7d_avg,
        })
    billing_failed_from_subs = int(subs.billing_failed or 0)
    billing_success = int(revenue.success_events or 0)
    failed_denominator = billing_success + billing_failed_from_subs
    failed_pct = (
        round((billing_failed_from_subs * 100.0) / failed_denominator, 1)
        if failed_denominator > 0
        else 0.0
    )

    top_services = db.execute(text(f"""
        SELECT
            srv.name                                             AS service_name,
            COUNT(*)                                             AS total,
            COUNT(*) FILTER (WHERE s.status = 'active')         AS active_subs,
            COUNT(*) FILTER (WHERE s.status = 'billing_failed') AS billing_failed,
            COUNT(*) FILTER (WHERE s.status = 'cancelled')      AS cancelled,
            COUNT(DISTINCT s.user_id) FILTER (WHERE s.status = 'active') AS active_users,
            ROUND(
                COUNT(*) FILTER (WHERE s.status = 'cancelled') * 100.0
                / NULLIF(COUNT(*) FILTER (WHERE s.status != 'pending'), 0), 1
            )                                                    AS churn_rate_pct
        FROM subscriptions s
        JOIN services srv ON srv.id = s.service_id
        WHERE s.subscription_start_date BETWEEN :start_dt AND :end_dt
        {sf_top}
        GROUP BY srv.name
        ORDER BY total DESC
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
        "usage_data_anchor": usage_anchor.strftime("%Y-%m-%d"),
        "filters_applied": {
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "service_id": service_id,
        },
        "users": {
            "total": users.total_users,
            "active": users.active_users,
            "inactive": users.inactive_users,
            "new_last_30_days": users.new_last_30_days,
        },
        "subscriptions": {
            "total": subs.total,
            "total_with_pending": subs.total_with_pending,
            "active": subs.active,
            "billing_failed": subs.billing_failed,
            "cancelled": subs.cancelled,
            "pending": subs.pending,
            "active_users": subs.active_users,
            "at_risk_users": subs.at_risk_users,
            "new_last_30_days": subs.new_last_30_days,
            "trial": subs.pending,
            "expired": subs.billing_failed,
            "conversion_rate_pct": float(subs.conversion_rate_pct or 0),
        },
        "churn": {
            "total": churn.total_unsubs,
            "voluntary": churn.voluntary,
            "technical": churn.technical,
            "voluntary_pct": float(churn.voluntary_pct or 0),
            "technical_pct": float(churn.technical_pct or 0),
            "churn_rate_month_pct": float(churn.churn_rate_month_pct or 0),
            "dropoff": {
                "day1": churn.dropoff_day1,
                "day2": churn.dropoff_day2,
                "day3": churn.dropoff_day3,
            },
        },
        "revenue": {
            "total_revenue": float(revenue.total_revenue or 0),
            "mrr": float(revenue.mrr or 0),
            "arpu_current_month": float(revenue.arpu_current_month or 0),
            "billing_success": billing_success,
            "billing_failed": billing_failed_from_subs,
            "failed_pct": failed_pct,
            "failure_data_note": None,
        },
        "engagement": {
            "dau_today": dau,
            "wau_current_week": engagement.wau_current_week or 0,
            "mau_current_month": mau,
            "stickiness_pct": stickiness,
            "scoped_users_count": scoped_users_count,
            "active_7d_users": active_7d_users,
            "inactive_7d_count": inactive_7d_count,
            "inactivity_rate_pct": inactivity_rate_pct,
            "engagement_score": engagement_score,
            "engagement_level": engagement_level,
            "engagement_thresholds": {
                "high": 70,
                "medium": 45,
                "low": 0,
            },
            "engagement_formula": "0.65*min(stickiness/30*100,100)+0.35*(100-inactivity_rate)",
            "trend": engagement_trend,
        },
        "sms": {
            "otp_templates_pct": float(sms.otp_templates_pct or 0),
            "activation_templates_pct": float(sms.activation_templates_pct or 0),
            "otp_rate_trend_pct": float(sms.otp_rate_trend_pct or 0),
            "activation_rate_trend_pct": float(sms.activation_rate_trend_pct or 0),
            "templates_per_service": float(sms.templates_per_service or 0),
            "total_templates": int(sms.total_templates or 0),
            "total_services": int(sms.total_services or 0),
        },
        "top_services": [
            {
                "name": row.service_name,
                "total": row.total,
                "active_subs": row.active_subs,
                "billing_failed": row.billing_failed,
                "cancelled": row.cancelled,
                "active_users": row.active_users,
                "churned_subs": row.cancelled,
                "churn_rate_pct": float(row.churn_rate_pct or 0),
            }
            for row in top_services
        ],
    }


@router.get("/overview")
def get_overview(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
):
    start_dt, end_dt = resolve_date_range(start_date, end_date, db=db, source="analytics")

    cache_key = build_cache_key(
        "overview",
        {
            "v": OVERVIEW_CACHE_VERSION,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "service_id": service_id or "all",
        },
    )

    return cache_or_compute(
        cache_key,
        settings.OVERVIEW_CACHE_TTL_SECONDS,
        compute_function=lambda: _compute_overview_payload(
            db,
            start_dt=start_dt,
            end_dt=end_dt,
            start_date=start_date,
            end_date=end_date,
            service_id=service_id,
        ),
    )


@router.get("/status/diagnostics")
def get_status_diagnostics(
    db: Session = Depends(get_db),
    service_id: Optional[str] = Query(default=None),
    _: object = Depends(require_admin),
):
    subs_service_filter = "WHERE s.service_id = CAST(:service_id AS uuid)" if service_id else ""
    params = {"service_id": service_id} if service_id else {}

    users_raw_rows = db.execute(
        text(
            """
            SELECT
                COALESCE(NULLIF(TRIM(status), ''), '<null>') AS raw_status,
                COUNT(*) AS count
            FROM users
            GROUP BY 1
            ORDER BY count DESC, raw_status ASC
            """
        )
    ).fetchall()

    users_norm_rows = db.execute(
        text(
            """
            SELECT norm_status, COUNT(*) AS count
            FROM (
                SELECT
                    CASE
                        WHEN LOWER(TRIM(COALESCE(status, ''))) IN ('1', 'active', 'subscribed', 'iscrit', 'inscrit') THEN 'subscribed'
                        WHEN LOWER(TRIM(COALESCE(status, ''))) IN ('-2', 'billing_failed', 'iscrit avec billing failure', 'inscrit avec billing failure', 'at_risk') THEN 'billing_failed'
                        WHEN LOWER(TRIM(COALESCE(status, ''))) IN ('-1', 'cancelled', 'expired', 'inactive', 'unsubscribed', 'desinscrit', 'désinscrit', 'churned') THEN 'unsubscribed'
                        WHEN LOWER(TRIM(COALESCE(status, ''))) IN ('0', 'pending', 'trial', 'otp_pending', 'otp non terminer') THEN 'otp_incomplete'
                        ELSE 'unknown'
                    END AS norm_status
                FROM users
            ) t
            GROUP BY norm_status
            ORDER BY count DESC, norm_status ASC
            """
        )
    ).fetchall()

    subs_raw_rows = db.execute(
        text(
            f"""
            SELECT
                COALESCE(NULLIF(TRIM(s.status), ''), '<null>') AS raw_status,
                COUNT(*) AS count
            FROM subscriptions s
            {subs_service_filter}
            GROUP BY 1
            ORDER BY count DESC, raw_status ASC
            """
        ),
        params,
    ).fetchall()

    subs_norm_rows = db.execute(
        text(
            f"""
            SELECT norm_status, COUNT(*) AS count
            FROM (
                SELECT
                    CASE
                        WHEN LOWER(TRIM(COALESCE(s.status, ''))) IN ('1', 'active', 'subscribed', 'iscrit', 'inscrit') THEN 'subscribed'
                        WHEN LOWER(TRIM(COALESCE(s.status, ''))) IN ('-2', 'billing_failed', 'iscrit avec billing failure', 'inscrit avec billing failure', 'at_risk') THEN 'billing_failed'
                        WHEN LOWER(TRIM(COALESCE(s.status, ''))) IN ('-1', 'cancelled', 'expired', 'inactive', 'unsubscribed', 'desinscrit', 'désinscrit', 'churned') THEN 'unsubscribed'
                        WHEN LOWER(TRIM(COALESCE(s.status, ''))) IN ('0', 'pending', 'trial', 'otp_pending', 'otp non terminer') THEN 'otp_incomplete'
                        ELSE 'unknown'
                    END AS norm_status
                FROM subscriptions s
                {subs_service_filter}
            ) t
            GROUP BY norm_status
            ORDER BY count DESC, norm_status ASC
            """
        ),
        params,
    ).fetchall()

    return {
        "status_reference": {
            "-1": "unsubscribed",
            "1": "subscribed",
            "-2": "billing_failed",
            "0": "otp_incomplete",
        },
        "filters": {
            "service_id": service_id,
        },
        "users": {
            "raw": [
                {"raw_status": r.raw_status, "count": int(r.count or 0)}
                for r in users_raw_rows
            ],
            "normalized": [
                {"status": r.norm_status, "count": int(r.count or 0)}
                for r in users_norm_rows
            ],
        },
        "subscriptions": {
            "raw": [
                {"raw_status": r.raw_status, "count": int(r.count or 0)}
                for r in subs_raw_rows
            ],
            "normalized": [
                {"status": r.norm_status, "count": int(r.count or 0)}
                for r in subs_norm_rows
            ],
        },
    }


@router.post("/cache/invalidate")
def invalidate_analytics(
    service_id: Optional[str] = Query(default=None),
    _: object = Depends(require_admin),
):
    deleted = invalidate_analytics_cache(service_id=service_id)
    return {
        "deleted_keys": deleted,
        "service_id": service_id,
    }