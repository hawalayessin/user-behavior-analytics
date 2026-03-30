from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, date, timedelta
from typing import Optional
import uuid

from app.core.database import get_db
from app.core.date_ranges import resolve_date_range
from app.utils.temporal import get_data_anchor

router = APIRouter(prefix="/analytics", tags=["User Activity"])


@router.get("/user-activity")
def get_user_activity(
    db:         Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date:   Optional[date] = Query(default=None),
    service_id: Optional[str]  = Query(default=None),
):
    # If no dates are provided, use the full available range from DB (by service if provided).
    # To avoid generating an enormous time series, we cap the returned trend range to 365 days.
    MAX_TREND_DAYS = 365

    start_dt, end_dt = resolve_date_range(start_date, end_date, db=db, source="usage")
    if (end_dt - start_dt).days > MAX_TREND_DAYS:
        start_dt = end_dt - timedelta(days=MAX_TREND_DAYS)

    subscription_anchor_dt = get_data_anchor(db, source="subscription")

    valid_service_id = None
    if service_id:
        try:
            valid_service_id = str(uuid.UUID(service_id))
        except ValueError:
            valid_service_id = None

    params = {
        "start_dt":   start_dt,
        "end_dt":     end_dt,
        "service_id": valid_service_id,
        "subscription_anchor_dt": subscription_anchor_dt,
    }

    sf_ua       = "AND service_id = CAST(:service_id AS uuid)"  if valid_service_id else ""
    sf_sub      = "AND service_id = CAST(:service_id AS uuid)"  if valid_service_id else ""
    sf_srv      = "AND srv.id = CAST(:service_id AS uuid)"      if valid_service_id else ""
    sf_inactive = """
        AND EXISTS (
            SELECT 1 FROM subscriptions sub
            WHERE sub.user_id    = u.id
              AND sub.service_id = CAST(:service_id AS uuid)
        )
    """ if valid_service_id else ""

    # ── 1. KPIs ───────────────────────────────────────────────
    kpis = db.execute(text(f"""
        SELECT
            COUNT(DISTINCT user_id) FILTER (
                WHERE DATE(activity_datetime) = :end_dt
            ) AS dau_today,

            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime >= CAST(:end_dt AS timestamp) - INTERVAL '7 days'
                  AND activity_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
            ) AS wau_current_week,

            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime >= CAST(:start_dt AS timestamp)
                  AND activity_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
            ) AS mau_current_month

        FROM user_activities
        WHERE activity_datetime >= CAST(:start_dt AS timestamp)
          AND activity_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
        {sf_ua}
    """), params).fetchone()

    dau        = kpis.dau_today         or 0
    mau        = kpis.mau_current_month or 0
    stickiness = round((dau / mau * 100), 1) if mau > 0 else 0.0

    # ── 2. Inactive users ─────────────────────────────────────
    # ✅ CORRIGÉ : inactif = pas d'activité depuis 7j (peu importe status)
    inactive = db.execute(text(f"""
        SELECT COUNT(DISTINCT u.id) AS inactive_count
        FROM users u
        LEFT JOIN user_activities ua
            ON  ua.user_id = u.id
            AND ua.activity_datetime >= CAST(:end_dt AS timestamp) - INTERVAL '7 days'
        WHERE ua.user_id IS NULL
          AND u.status NOT IN ('churned', 'cancelled')
        {sf_inactive}
    """), params).fetchone()

    # ── 3. Average lifetime ───────────────────────────────────
    lifetime = db.execute(text(f"""
        SELECT ROUND(AVG(
            EXTRACT(DAY FROM
                COALESCE(subscription_end_date, CAST(:subscription_anchor_dt AS timestamp)) - subscription_start_date
            )
        ), 0) AS avg_lifetime_days
        FROM subscriptions
        WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
          AND subscription_start_date <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
          AND status IN ('active', 'cancelled', 'expired')
        {sf_sub}
    """), params).fetchone()

    # ── 4. DAU trend ──────────────────────────────────────────
    dau_rows = db.execute(text(f"""
        SELECT
            DATE(activity_datetime) AS date,
            COUNT(DISTINCT user_id) AS dau
        FROM user_activities
        WHERE activity_datetime >= CAST(:start_dt AS timestamp)
          AND activity_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
        {sf_ua}
        GROUP BY DATE(activity_datetime)
        ORDER BY date ASC
    """), params).fetchall()

    dau_map = {str(row.date): row.dau for row in dau_rows}

    # ✅ CORRIGÉ : WAU/MAU rolling depuis DB (distinct users réels)
    wau_rows = db.execute(text(f"""
        SELECT
            DATE(activity_datetime) AS date,
            COUNT(DISTINCT user_id) AS rolling_count
        FROM user_activities
        WHERE activity_datetime >= CAST(:start_dt AS timestamp) - INTERVAL '30 days'
          AND activity_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
        {sf_ua}
        GROUP BY DATE(activity_datetime)
        ORDER BY date ASC
    """), params).fetchall()

    wau_map = {str(row.date): row.rolling_count for row in wau_rows}

    all_dates = [
        start_dt + timedelta(days=i)
        for i in range((end_dt - start_dt).days + 1)
    ]

    dau_trend = []
    for d in all_dates:
        ds  = str(d)
        wau = sum(wau_map.get(str(d - timedelta(days=j)), 0) for j in range(7))
        mau_roll = sum(wau_map.get(str(d - timedelta(days=j)), 0) for j in range(30))
        dau_trend.append({
            "date": ds,
            "dau":  dau_map.get(ds, 0),
            "wau":  wau,
            "mau":  mau_roll,
        })

    # ── 5. Activity heatmap (7×24) ────────────────────────────
    heatmap_rows = db.execute(text(f"""
        SELECT
            TRIM(TO_CHAR(activity_datetime, 'Day')) AS day,
            EXTRACT(HOUR FROM activity_datetime)::int AS hour,
            COUNT(*) AS count
        FROM user_activities
        WHERE activity_datetime >= CAST(:start_dt AS timestamp)
          AND activity_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
        {sf_ua}
        GROUP BY day, hour
        ORDER BY day, hour
    """), params).fetchall()

    day_map = {
        'Monday': 'Lundi', 'Tuesday': 'Mardi', 'Wednesday': 'Mercredi',
        'Thursday': 'Jeudi', 'Friday': 'Vendredi',
        'Saturday': 'Samedi', 'Sunday': 'Dimanche',
    }
    days_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    day_to_idx = {name: idx for idx, name in enumerate(days_fr)}

    heatmap_dict = {(day_idx, h): 0 for day_idx in range(7) for h in range(24)}
    for row in heatmap_rows:
        day_fr = day_map.get(row.day.strip(), row.day.strip())
        day_idx = day_to_idx.get(day_fr)
        if day_idx is None:
            continue
        if (day_idx, row.hour) in heatmap_dict:
            heatmap_dict[(day_idx, row.hour)] = row.count

    activity_heatmap = [
        {"day": day_idx, "hour": h, "count": heatmap_dict[(day_idx, h)]}
        for day_idx in range(7)
        for h in range(24)
    ]

    # ── 5b. User growth (monthly new vs churned) ───────────────
    sf_user_service = """
        AND EXISTS (
            SELECT 1
            FROM subscriptions sub
            WHERE sub.user_id = u.id
              AND sub.service_id = CAST(:service_id AS uuid)
        )
    """ if valid_service_id else ""

    sf_unsub_service = "AND un.service_id = CAST(:service_id AS uuid)" if valid_service_id else ""

    user_growth_rows = db.execute(text(f"""
        WITH months AS (
            SELECT generate_series(
                date_trunc('month', CAST(:start_dt AS timestamp))::date,
                date_trunc('month', CAST(:end_dt AS timestamp))::date,
                interval '1 month'
            )::date AS month_start
        ),
        new_users AS (
            SELECT
                date_trunc('month', u.created_at)::date AS month_start,
                COUNT(DISTINCT u.id) AS new_count
            FROM users u
            WHERE u.created_at >= CAST(:start_dt AS timestamp)
              AND u.created_at <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
            {sf_user_service}
            GROUP BY 1
        ),
        churned_users AS (
            SELECT
                date_trunc('month', un.unsubscription_datetime)::date AS month_start,
                COUNT(DISTINCT un.user_id) AS churn_count
            FROM unsubscriptions un
            WHERE un.unsubscription_datetime >= CAST(:start_dt AS timestamp)
              AND un.unsubscription_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
            {sf_unsub_service}
            GROUP BY 1
        )
        SELECT
            m.month_start,
            COALESCE(nu.new_count, 0)   AS nouveaux,
            COALESCE(cu.churn_count, 0) AS churnes
        FROM months m
        LEFT JOIN new_users nu     ON nu.month_start = m.month_start
        LEFT JOIN churned_users cu ON cu.month_start = m.month_start
        ORDER BY m.month_start ASC
    """), params).fetchall()

    user_growth = [
        {
            "month": row.month_start.strftime("%Y-%m"),
            "nouveaux": int(row.nouveaux or 0),
            "churnés": int(row.churnes or 0),
        }
        for row in user_growth_rows
    ]

    # ── 6. By service ─────────────────────────────────────────
    by_service_rows = db.execute(text(f"""
        SELECT
            srv.name AS service_name,
            COUNT(*) FILTER (WHERE s.status = 'active')  AS active_users,
            COUNT(*) FILTER (WHERE s.status = 'trial')   AS trial_users,
            COUNT(*) FILTER (
                WHERE u.last_activity_at < CAST(:end_dt AS timestamp) - INTERVAL '7 days'
                   OR u.last_activity_at IS NULL
            ) AS inactive_7d,
            COUNT(*) FILTER (
                WHERE u.last_activity_at < CAST(:end_dt AS timestamp) - INTERVAL '30 days'
                   OR u.last_activity_at IS NULL
            ) AS inactive_30d,
            ROUND(AVG(
                EXTRACT(DAY FROM
                    COALESCE(s.subscription_end_date, CAST(:subscription_anchor_dt AS timestamp)) - s.subscription_start_date)
            ), 0) AS avg_lifetime_days,
            ROUND(
                COUNT(DISTINCT ua_today.user_id) * 100.0
                / NULLIF(COUNT(DISTINCT s.user_id), 0)
            , 1) AS stickiness_pct
        FROM subscriptions s
        JOIN services srv ON srv.id = s.service_id
        JOIN users u ON u.id = s.user_id
        LEFT JOIN user_activities ua_today
            ON  ua_today.user_id = s.user_id
            AND DATE(ua_today.activity_datetime) = :end_dt
        WHERE s.subscription_start_date >= CAST(:start_dt AS timestamp)
          AND s.subscription_start_date <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
        {sf_srv}
        GROUP BY srv.id, srv.name
        ORDER BY active_users DESC
    """), params).fetchall()

    # ── 7. Inactivity buckets (EN labels) ──────────────────────
    buckets_rows = db.execute(text("""
        SELECT
            CASE
                WHEN EXTRACT(DAY FROM CAST(:end_dt AS timestamp) - last_activity_at) BETWEEN 1 AND 7
                    THEN '1-7 days'
                WHEN EXTRACT(DAY FROM CAST(:end_dt AS timestamp) - last_activity_at) BETWEEN 8 AND 14
                    THEN '8-14 days'
                WHEN EXTRACT(DAY FROM CAST(:end_dt AS timestamp) - last_activity_at) BETWEEN 15 AND 30
                    THEN '15-30 days'
                WHEN EXTRACT(DAY FROM CAST(:end_dt AS timestamp) - last_activity_at) > 30
                    THEN '30+ days'
                ELSE 'Unknown'
            END AS bucket,
            COUNT(*) AS count
        FROM users
        WHERE last_activity_at IS NOT NULL
          AND status NOT IN ('churned', 'cancelled')
        GROUP BY bucket
        ORDER BY MIN(EXTRACT(DAY FROM CAST(:end_dt AS timestamp) - last_activity_at))
    """), params).fetchall()

    bucket_order = ['1-7 days', '8-14 days', '15-30 days', '30+ days']
    bucket_map_d = {row.bucket: row.count for row in buckets_rows}
    inactivity_buckets = [
        {"bucket": b, "count": bucket_map_d.get(b, 0)}
        for b in bucket_order
    ]

    return {
        "filters_applied": {
            "start_date": start_dt.isoformat(),
            "end_date":   end_dt.isoformat(),
            "service_id": service_id,
        },
        "kpis": {
            "dau_today":         dau,
            "wau_current_week":  kpis.wau_current_week  or 0,
            "mau_current_month": mau,
            "stickiness_pct":    stickiness,
            "inactive_count":    inactive.inactive_count or 0,
            "avg_lifetime_days": float(lifetime.avg_lifetime_days or 0),
        },
        "dau_trend":        dau_trend,
        "activity_heatmap": activity_heatmap,
        "user_growth":      user_growth,
        "by_service": [
            {
                "service_name":      row.service_name,
                "active_users":      row.active_users      or 0,
                "trial_users":       row.trial_users       or 0,
                "inactive_7d":       row.inactive_7d       or 0,
                "inactive_30d":      row.inactive_30d      or 0,
                "avg_lifetime_days": float(row.avg_lifetime_days or 0),
                "stickiness_pct":    float(row.stickiness_pct    or 0),
            }
            for row in by_service_rows
        ],
        "inactivity_buckets": inactivity_buckets,
    }
