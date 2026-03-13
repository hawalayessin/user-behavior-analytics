from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, date, timedelta, time
from typing import Optional
import uuid

from app.core.database import get_db

router = APIRouter(prefix="/analytics", tags=["User Activity"])


@router.get("/user-activity")
def get_user_activity(
    db:         Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date:   Optional[date] = Query(default=None),
    service_id: Optional[str]  = Query(default=None),
):
    # ── Même logique de dates que overview ───────────────────
    end_dt   = end_date   or date.today()
    start_dt = start_date or (end_dt - timedelta(days=30))

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
    }

    # ── Filtres — même pattern que overview ──────────────────
    # user_activities sans alias  → service_id direct
    sf_ua = "AND service_id = CAST(:service_id AS uuid)"        if valid_service_id else ""
    # subscriptions sans alias    → service_id direct
    sf_sub = "AND service_id = CAST(:service_id AS uuid)"       if valid_service_id else ""
    # subscriptions s + services srv → srv.id
    sf_srv = "AND srv.id = CAST(:service_id AS uuid)"           if valid_service_id else ""
    # inactive — subquery explicite
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
            )                                                    AS dau_today,
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime
                      BETWEEN :end_dt - INTERVAL '7 days' AND :end_dt + INTERVAL '1 day'
            )                                                    AS wau_current_week,
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime
                      BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
            )                                                    AS mau_current_month,
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime
                      BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
            )                                                    AS period_active_users
        FROM user_activities
        WHERE activity_datetime
              BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
        {sf_ua}
    """), params).fetchone()

    dau        = kpis.dau_today         or 0
    mau        = kpis.mau_current_month or 0
    stickiness = round((dau / mau * 100), 1) if mau > 0 else 0.0

    # ── 2. Inactive users ─────────────────────────────────────
    inactive = db.execute(text(f"""
        SELECT COUNT(DISTINCT u.id) AS inactive_count
        FROM users u
        LEFT JOIN user_activities ua
            ON  ua.user_id = u.id
            AND ua.activity_datetime >= :end_dt - INTERVAL '7 days'
        WHERE ua.user_id IS NULL
          AND u.status = 'inactive'
        {sf_inactive}
    """), params).fetchone()

    # ── 3. Average lifetime ───────────────────────────────────
    lifetime = db.execute(text(f"""
        SELECT ROUND(AVG(
            EXTRACT(DAY FROM
                COALESCE(subscription_end_date, NOW()) - subscription_start_date
            )
        ), 0) AS avg_lifetime_days
        FROM subscriptions
        WHERE subscription_start_date
              BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
          AND status IN ('active', 'cancelled', 'expired')
        {sf_sub}
    """), params).fetchone()

    # ── 4. DAU trend ──────────────────────────────────────────
    dau_rows = db.execute(text(f"""
        SELECT
            DATE(activity_datetime) AS date,
            COUNT(DISTINCT user_id) AS dau
        FROM user_activities
        WHERE activity_datetime
              BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
        {sf_ua}
        GROUP BY DATE(activity_datetime)
        ORDER BY date ASC
    """), params).fetchall()

    dau_map   = {str(row.date): row.dau for row in dau_rows}
    all_dates = [
        start_dt + timedelta(days=i)
        for i in range((end_dt - start_dt).days + 1)
    ]

    dau_trend = []
    for d in all_dates:
        ds       = str(d)
        wau      = sum(dau_map.get(str(d - timedelta(days=j)), 0) for j in range(7))
        mau_roll = sum(dau_map.get(str(d - timedelta(days=j)), 0) for j in range(30))
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
        WHERE activity_datetime
              BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
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

    heatmap_dict = {(day, h): 0 for day in days_fr for h in range(24)}
    for row in heatmap_rows:
        day_fr = day_map.get(row.day.strip(), row.day.strip())
        heatmap_dict[(day_fr, row.hour)] = row.count

    activity_heatmap = [
        {"day": day, "hour": h, "count": heatmap_dict[(day, h)]}
        for day in days_fr
        for h in range(24)
    ]

    # ── 6. By service ─────────────────────────────────────────
    by_service_rows = db.execute(text(f"""
        SELECT
            srv.name                                              AS service_name,
            COUNT(*) FILTER (WHERE s.status = 'active')           AS active_users,
            COUNT(*) FILTER (WHERE s.status = 'trial')            AS trial_users,
            COUNT(*) FILTER (
                WHERE u.last_activity_at < :end_dt - INTERVAL '7 days'
                OR u.last_activity_at IS NULL
            )                                                     AS inactive_7d,
            COUNT(*) FILTER (
                WHERE u.last_activity_at < :end_dt - INTERVAL '30 days'
                OR u.last_activity_at IS NULL
            )                                                     AS inactive_30d,
            ROUND(AVG(
                EXTRACT(DAY FROM
                    COALESCE(s.subscription_end_date, NOW())
                    - s.subscription_start_date)
            ), 0)                                                 AS avg_lifetime_days,
            ROUND(
                COUNT(DISTINCT ua_today.user_id) * 100.0
                / NULLIF(COUNT(DISTINCT s.user_id), 0)
            , 1)                                                  AS stickiness_pct
        FROM subscriptions s
        JOIN services srv ON srv.id = s.service_id
        JOIN users u ON u.id = s.user_id
        LEFT JOIN user_activities ua_today
            ON  ua_today.user_id = s.user_id
            AND DATE(ua_today.activity_datetime) = :end_dt
        WHERE s.subscription_start_date
              BETWEEN :start_dt AND :end_dt + INTERVAL '1 day'
        {sf_srv}
        GROUP BY srv.id, srv.name
        ORDER BY active_users DESC
    """), params).fetchall()

    # ── 7. Inactivity buckets ─────────────────────────────────
    buckets_rows = db.execute(text("""
        SELECT
            CASE
                WHEN EXTRACT(DAY FROM NOW() - last_activity_at) BETWEEN 1 AND 7
                    THEN '1-7 jours'
                WHEN EXTRACT(DAY FROM NOW() - last_activity_at) BETWEEN 8 AND 14
                    THEN '8-14 jours'
                WHEN EXTRACT(DAY FROM NOW() - last_activity_at) BETWEEN 15 AND 30
                    THEN '15-30 jours'
                WHEN EXTRACT(DAY FROM NOW() - last_activity_at) > 30
                    THEN '+30 jours'
                ELSE 'Inconnu'
            END AS bucket,
            COUNT(*) AS count
        FROM users
        WHERE last_activity_at IS NOT NULL
          AND status = 'inactive'
        GROUP BY bucket
        ORDER BY MIN(EXTRACT(DAY FROM NOW() - last_activity_at))
    """), params).fetchall()

    bucket_order = ['1-7 jours', '8-14 jours', '15-30 jours', '+30 jours']
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