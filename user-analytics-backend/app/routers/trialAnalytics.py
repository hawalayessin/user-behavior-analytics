from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, timedelta
from typing import Optional
import uuid

from app.core.database import get_db

router = APIRouter(prefix="/analytics", tags=["Trial Analytics"])


# ══════════════════════════════════════════════════════════════════
# GET /analytics/trial/kpis
# ══════════════════════════════════════════════════════════════════
@router.get("/trial/kpis")
def get_trial_kpis(
    db:         Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date:   Optional[date] = Query(default=None),
    service_id: Optional[str]  = Query(default=None),
):
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

    sf = "AND service_id = CAST(:service_id AS uuid)" if valid_service_id else ""

    # ── 1. Total Trials Started ────────────────────────────────
    total_trials = db.execute(text(f"""
        SELECT COUNT(*) AS total
        FROM subscriptions
        WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
          AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
        {sf}
    """), params).scalar() or 0

    # ── 2. Conversion Rate (trial → active) ────────────────────
    conversion_data = db.execute(text(f"""
        SELECT
            COUNT(*)                                         AS total_all,
            COUNT(*) FILTER (WHERE status = 'active')       AS active_subs,
            COUNT(*) FILTER (WHERE status = 'cancelled')    AS cancelled_subs,
            COUNT(*) FILTER (WHERE status = 'trial')        AS trial_subs
        FROM subscriptions
        WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
          AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
        {sf}
    """), params).fetchone()

    total_all    = conversion_data.total_all    or 0
    active_count = conversion_data.active_subs  or 0
    conversion_rate = round((active_count / total_all * 100), 1) if total_all > 0 else 0.0

    # ── 3. Average Trial Duration ──────────────────────────────
    # ✅ GREATEST(0, ...) évite les valeurs négatives
    avg_duration = db.execute(text(f"""
        SELECT
            ROUND(
                AVG(
                    GREATEST(
                        0,
                        EXTRACT(DAY FROM
                            COALESCE(subscription_end_date, NOW()) - subscription_start_date
                        )
                    )
                )::numeric,
                1
            ) AS avg_days
        FROM subscriptions
        WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
          AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
          AND subscription_start_date <= NOW()
        {sf}
    """), params).scalar() or 0.0

    # ── 4. Day 3 Drop-off Rate ─────────────────────────────────
    # ✅ GREATEST(0, ...) évite les négatifs dans le calcul
    dropoff_data = db.execute(text(f"""
        SELECT
            COUNT(*) FILTER (
                WHERE status IN ('cancelled', 'expired')
                  AND GREATEST(0, EXTRACT(DAY FROM
                        COALESCE(subscription_end_date, NOW()) - subscription_start_date
                      )) <= 3
            ) AS dropoff_by_day3,
            COUNT(*) AS total_count
        FROM subscriptions
        WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
          AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
          AND subscription_start_date <= NOW()
        {sf}
    """), params).fetchone()

    dropoff_count  = dropoff_data.dropoff_by_day3 or 0
    total_count    = dropoff_data.total_count      or 0
    dropoff_j3     = round((dropoff_count / total_count * 100), 1) if total_count > 0 else 0.0

    return {
        "total_trials":    int(total_trials),
        "conversion_rate": float(conversion_rate),
        "avg_duration":    float(avg_duration),
        "dropoff_j3":      float(dropoff_j3),
    }


# ══════════════════════════════════════════════════════════════════
# GET /analytics/trial/timeline
# ══════════════════════════════════════════════════════════════════
@router.get("/trial/timeline")
def get_trial_timeline(
    db:         Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date:   Optional[date] = Query(default=None),
    service_id: Optional[str]  = Query(default=None),
):
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

    sf = "AND service_id = CAST(:service_id AS uuid)" if valid_service_id else ""

    timeline = db.execute(text(f"""
        SELECT
            DATE(subscription_start_date)                                    AS date,
            COUNT(*) FILTER (WHERE status = 'trial')                         AS trials_started,
            COUNT(*) FILTER (WHERE status = 'active')                        AS converted,
            COUNT(*) FILTER (WHERE status IN ('cancelled', 'expired'))       AS dropped
        FROM subscriptions
        WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
          AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
        {sf}
        GROUP BY DATE(subscription_start_date)
        ORDER BY date ASC
    """), params).fetchall()

    return {
        "data": [
            {
                "date":           str(row.date),
                "trials_started": row.trials_started or 0,
                "converted":      row.converted      or 0,
                "dropped":        row.dropped         or 0,
            }
            for row in timeline
        ]
    }


# ══════════════════════════════════════════════════════════════════
# GET /analytics/trial/by-service
# ══════════════════════════════════════════════════════════════════
@router.get("/trial/by-service")
def get_trial_by_service(
    db:         Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date:   Optional[date] = Query(default=None),
):
    end_dt   = end_date   or date.today()
    start_dt = start_date or (end_dt - timedelta(days=30))

    params = {
        "start_dt": start_dt,
        "end_dt":   end_dt,
    }

    by_service = db.execute(text("""
        SELECT
            s.name AS service_name,
            COUNT(*) FILTER (WHERE sub.status = 'trial')                         AS trials,
            COUNT(*) FILTER (WHERE sub.status = 'active')                        AS converted,
            COUNT(*) FILTER (WHERE sub.status IN ('cancelled', 'expired'))       AS dropped,
            ROUND(
                COUNT(*) FILTER (WHERE sub.status = 'active') * 100.0
                / NULLIF(COUNT(*), 0),
                1
            ) AS conversion_rate_pct
        FROM subscriptions sub
        JOIN services s ON s.id = sub.service_id
        WHERE sub.subscription_start_date >= CAST(:start_dt AS timestamp)
          AND sub.subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
        GROUP BY s.name
        ORDER BY trials DESC
    """), params).fetchall()

    return {
        "data": [
            {
                "service_name":    row.service_name,
                "trials":          row.trials     or 0,
                "converted":       row.converted  or 0,
                "dropped":         row.dropped    or 0,
                "conversion_rate": float(row.conversion_rate_pct or 0),
            }
            for row in by_service
        ]
    }


# ══════════════════════════════════════════════════════════════════
# GET /analytics/trial/users — Trial Users Table
# ══════════════════════════════════════════════════════════════════
@router.get("/trial/users")
def get_trial_users(
    db:         Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date:   Optional[date] = Query(default=None),
    service_id: Optional[str]  = Query(default=None),
    search:     Optional[str]  = Query(default=None),
    status:     Optional[str]  = Query(default=None),
    page:       int            = Query(default=1, ge=1),
    page_size:  int            = Query(default=8,  ge=1, le=200),
    export:     bool           = Query(default=False),
):
    end_dt   = end_date   or date.today()
    start_dt = start_date or (end_dt - timedelta(days=30))

    valid_service_id = None
    if service_id:
        try:
            valid_service_id = str(uuid.UUID(service_id))
        except ValueError:
            valid_service_id = None

    # ── Mapping statut frontend → DB ──────────────────────────
    # "trial"     → status = 'trial'
    # "converted" → status = 'active'
    # "dropped"   → status IN ('cancelled', 'expired')
    status_filter_sql = ""
    if status == "trial":
        status_filter_sql = "AND sub.status = 'trial'"
    elif status == "converted":
        status_filter_sql = "AND sub.status = 'active'"
    elif status == "dropped":
        status_filter_sql = "AND sub.status IN ('cancelled', 'expired')"

    search_sql     = "AND u.phone_number ILIKE :search" if search else ""
    service_sql    = "AND sub.service_id = CAST(:service_id AS uuid)" if valid_service_id else ""
    limit_clause   = "" if export else "LIMIT :limit OFFSET :offset"

    params = {
        "start_dt":   start_dt,
        "end_dt":     end_dt,
        "service_id": valid_service_id,
        "search":     f"%{search}%" if search else None,
    }

    if not export:
        params["limit"]  = page_size
        params["offset"] = (page - 1) * page_size

    rows = db.execute(text(f"""
        SELECT
            u.id,
            u.phone_number,
            s.name                                                AS service_name,
            sub.subscription_start_date                          AS trial_start,
            sub.subscription_end_date                            AS trial_end,
            sub.status,

            -- ✅ GREATEST(0, ...) évite les durées négatives
            GREATEST(0,
                ROUND(
                    EXTRACT(DAY FROM
                        COALESCE(sub.subscription_end_date, NOW()) - sub.subscription_start_date
                    )::numeric,
                1
                )
            )                                                     AS duration_days,

            -- Converti = status active
            CASE WHEN sub.status = 'active' THEN true ELSE false END AS converted

        FROM subscriptions sub
        JOIN users    u ON u.id  = sub.user_id
        JOIN services s ON s.id  = sub.service_id

        WHERE sub.subscription_start_date >= CAST(:start_dt AS timestamp)
          AND sub.subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
          AND sub.subscription_start_date <= NOW()
          {service_sql}
          {status_filter_sql}
          {search_sql}

        ORDER BY sub.subscription_start_date DESC
        {limit_clause}
    """), {k: v for k, v in params.items() if v is not None}).fetchall()

    # ── Count total ───────────────────────────────────────────
    count_params = {k: v for k, v in params.items() if k not in ("limit", "offset") and v is not None}
    total = db.execute(text(f"""
        SELECT COUNT(*) AS total
        FROM subscriptions sub
        JOIN users    u ON u.id = sub.user_id
        JOIN services s ON s.id = sub.service_id
        WHERE sub.subscription_start_date >= CAST(:start_dt AS timestamp)
          AND sub.subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
          AND sub.subscription_start_date <= NOW()
          {service_sql}
          {status_filter_sql}
          {search_sql}
    """), count_params).scalar() or 0

    return {
        "data": [
            {
                "id":           str(row.id),
                "phone_number": row.phone_number,
                "service_name": row.service_name,
                "trial_start":  row.trial_start.isoformat()  if row.trial_start  else None,
                "trial_end":    row.trial_end.isoformat()    if row.trial_end    else None,
                "status":       row.status,
                "duration_days": float(row.duration_days or 0),
                "converted":    bool(row.converted),
            }
            for row in rows
        ],
        "total":     total,
        "page":      page,
        "page_size": page_size,
    }


# ══════════════════════════════════════════════════════════════════
# GET /analytics/trial/dropoff-by-day — Day1/2/3 buckets
# ══════════════════════════════════════════════════════════════════
@router.get("/trial/dropoff-by-day")
def get_trial_dropoff_by_day(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date:   Optional[date] = Query(default=None),
    service_id: Optional[str]  = Query(default=None),
):
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

    sf = "AND service_id = CAST(:service_id AS uuid)" if valid_service_id else ""

    row = db.execute(text(f"""
        WITH base AS (
            SELECT
                GREATEST(
                    0,
                    EXTRACT(DAY FROM COALESCE(subscription_end_date, NOW()) - subscription_start_date)
                )::int AS duration_days
            FROM subscriptions
            WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
              AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
              AND subscription_start_date <= NOW()
              AND status IN ('cancelled', 'expired')
              AND subscription_end_date IS NOT NULL
            {sf}
        )
        SELECT
            COUNT(*) FILTER (WHERE duration_days <= 1)                      AS day1,
            COUNT(*) FILTER (WHERE duration_days > 1 AND duration_days <= 2) AS day2,
            COUNT(*) FILTER (WHERE duration_days > 2 AND duration_days <= 3) AS day3
        FROM base
    """), params).fetchone()

    return {
        "day1": int(row.day1 or 0),
        "day2": int(row.day2 or 0),
        "day3": int(row.day3 or 0),
    }


# ══════════════════════════════════════════════════════════════════
# GET /analytics/churn/breakdown — voluntary vs technical
# ══════════════════════════════════════════════════════════════════
@router.get("/churn/breakdown")
def get_churn_breakdown(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date:   Optional[date] = Query(default=None),
    service_id: Optional[str]  = Query(default=None),
):
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

    sf = "AND u.service_id = CAST(:service_id AS uuid)" if valid_service_id else ""

    churn = db.execute(text(f"""
        SELECT
            COUNT(*)                                                         AS total_unsubs,
            COUNT(*) FILTER (WHERE u.churn_type = 'VOLUNTARY')               AS voluntary,
            COUNT(*) FILTER (WHERE u.churn_type = 'TECHNICAL')               AS technical,
            ROUND(COUNT(*) FILTER (WHERE u.churn_type = 'VOLUNTARY') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                    AS voluntary_pct,
            ROUND(COUNT(*) FILTER (WHERE u.churn_type = 'TECHNICAL') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                    AS technical_pct
        FROM unsubscriptions u
        WHERE u.unsubscription_datetime >= CAST(:start_dt AS timestamp)
          AND u.unsubscription_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
        {sf}
    """), params).fetchone()

    return {
        "total": int(churn.total_unsubs or 0),
        "voluntary_pct": float(churn.voluntary_pct or 0),
        "technical_pct": float(churn.technical_pct or 0),
        "voluntary": int(churn.voluntary or 0),
        "technical": int(churn.technical or 0),
    }
