from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, timedelta
from typing import Optional
import uuid

from app.core.database import get_db
from app.core.date_ranges import resolve_date_range
from app.core.cache import build_cache_key, cache_or_compute
from app.core.config import settings
from app.utils.temporal import get_data_anchor
from app.services.business_rules import build_trial_exception_summary

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
    start_dt, end_dt = resolve_date_range(start_date, end_date, db=db, source="subscription")

    cache_key = build_cache_key(
        "trial_kpis",
        {
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "service_id": service_id or "all",
        },
    )

    return cache_or_compute(
        cache_key,
        settings.TRIAL_KPIS_CACHE_TTL_SECONDS,
        compute_function=lambda: _compute_trial_kpis(
            db=db,
            start_dt=start_dt,
            end_dt=end_dt,
            service_id=service_id,
        ),
    )


def _compute_trial_kpis(
    db: Session,
    start_dt: date,
    end_dt: date,
    service_id: Optional[str],
):
    anchor_dt = get_data_anchor(db, source="subscription")

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
        "anchor_dt":  anchor_dt,
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

    # ── 2. Conversion & status breakdown ───────────────────────
    conversion_data = db.execute(text(f"""
        SELECT
            COUNT(*) FILTER (WHERE status IN ('trial', 'pending', 'active', 'cancelled', 'expired')) AS total_all,
                        COUNT(*) FILTER (WHERE status = 'active')       AS active_subs,
                        COUNT(*) FILTER (WHERE status IN ('cancelled', 'expired')) AS dropped_subs,
            COUNT(*) FILTER (WHERE status IN ('trial', 'pending')) AS trial_subs
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
                            COALESCE(subscription_end_date, CAST(:anchor_dt AS timestamp)) - subscription_start_date
                        )
                    )
                )::numeric,
                1
            ) AS avg_days
        FROM subscriptions
        WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
          AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                    AND subscription_start_date <= CAST(:anchor_dt AS timestamp)
        {sf}
    """), params).scalar() or 0.0

    # ── 4. Day 3 Drop-off Rate ─────────────────────────────────
    # ✅ GREATEST(0, ...) évite les négatifs dans le calcul
    dropoff_data = db.execute(text(f"""
        SELECT
            COUNT(*) FILTER (
                WHERE status IN ('cancelled', 'expired')
                  AND GREATEST(0, EXTRACT(DAY FROM
                                                COALESCE(subscription_end_date, CAST(:anchor_dt AS timestamp)) - subscription_start_date
                      )) <= 3
            ) AS dropoff_by_day3,
            COUNT(*) AS total_count
        FROM subscriptions
        WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
          AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                    AND subscription_start_date <= CAST(:anchor_dt AS timestamp)
        {sf}
    """), params).fetchone()

    dropoff_count  = dropoff_data.dropoff_by_day3 or 0
    total_count    = dropoff_data.total_count      or 0
    dropoff_j3     = round((dropoff_count / total_count * 100), 1) if total_count > 0 else 0.0

    # ── 5. Trial-only users (never converted to active) ────────
    trial_only = db.execute(text(f"""
        WITH trial_users AS (
            SELECT DISTINCT user_id
            FROM subscriptions
            WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
              AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
              {sf}
        ),
        has_active AS (
            SELECT DISTINCT user_id
            FROM subscriptions
            WHERE status = 'active'
              {sf}
        )
        SELECT
          COUNT(*) AS trial_only_users,
          COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM trial_users), 0) AS trial_only_rate
        FROM trial_users tu
        LEFT JOIN has_active ha ON ha.user_id = tu.user_id
        WHERE ha.user_id IS NULL
    """), params).fetchone()

    trial_only_users = int(trial_only.trial_only_users or 0)
    trial_only_rate = float(trial_only.trial_only_rate or 0.0)

    # ── 6. Business exceptions (promotion / trial extension) ──────────
    exceptions_row = db.execute(text(f"""
        SELECT
            COUNT(*) FILTER (
                WHERE c.campaign_type = 'promotion'
            ) AS promotion_trials,
            COUNT(*) FILTER (
                WHERE (
                    EXTRACT(DAY FROM COALESCE(sub.subscription_end_date, CAST(:anchor_dt AS timestamp)) - sub.subscription_start_date)
                    > COALESCE(st.trial_duration_days, 0)
                )
            ) AS trial_extensions
        FROM subscriptions sub
        JOIN services sv ON sv.id = sub.service_id
        JOIN service_types st ON st.id = sv.service_type_id
        LEFT JOIN campaigns c ON c.id = sub.campaign_id
        WHERE sub.subscription_start_date >= CAST(:start_dt AS timestamp)
          AND sub.subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
          AND sub.subscription_start_date <= CAST(:anchor_dt AS timestamp)
        {"AND sub.service_id = CAST(:service_id AS uuid)" if valid_service_id else ""}
    """), params).fetchone()

    exception_summary = build_trial_exception_summary(
        total_trials=int(total_trials),
        promotion_trials=int(exceptions_row.promotion_trials or 0),
        trial_extensions=int(exceptions_row.trial_extensions or 0),
    )

    return {
        "total_trials":      int(total_trials),
        "conversion_rate":   float(conversion_rate),
        "avg_duration":      float(avg_duration),
        "dropoff_j3":        float(dropoff_j3),
        "trial_only_users":  trial_only_users,
        "trial_only_rate":   trial_only_rate,
        "active_trials":     int(conversion_data.trial_subs or 0),
        "converted_trials":  int(conversion_data.active_subs or 0),
        "cancelled_trials":  int(conversion_data.dropped_subs or 0),
        "dropped_trials":    int(conversion_data.dropped_subs or 0),
        "business_exception_rules": exception_summary,
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
    start_dt, end_dt = resolve_date_range(start_date, end_date, db=db, source="subscription")

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
    start_dt, end_dt = resolve_date_range(start_date, end_date, db=db, source="subscription")

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
    start_dt, end_dt = resolve_date_range(start_date, end_date, db=db, source="subscription")
    anchor_dt = get_data_anchor(db, source="subscription")

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
        "anchor_dt":  anchor_dt,
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
                        COALESCE(sub.subscription_end_date, CAST(:anchor_dt AS timestamp)) - sub.subscription_start_date
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
                    AND sub.subscription_start_date <= CAST(:anchor_dt AS timestamp)
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
                    AND sub.subscription_start_date <= CAST(:anchor_dt AS timestamp)
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
    start_dt, end_dt = resolve_date_range(start_date, end_date, db=db, source="subscription")
    anchor_dt = get_data_anchor(db, source="subscription")

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
        "anchor_dt":  anchor_dt,
    }

    sf = "AND service_id = CAST(:service_id AS uuid)" if valid_service_id else ""

    row = db.execute(text(f"""
        WITH base AS (
            SELECT
                GREATEST(
                    0,
                                        EXTRACT(DAY FROM COALESCE(subscription_end_date, CAST(:anchor_dt AS timestamp)) - subscription_start_date)
                )::int AS duration_days
            FROM subscriptions
            WHERE subscription_start_date >= CAST(:start_dt AS timestamp)
              AND subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                            AND subscription_start_date <= CAST(:anchor_dt AS timestamp)
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
# GET /analytics/trial/dropoff-causes — causal explanation for 4.2
# ══════════════════════════════════════════════════════════════════
@router.get("/trial/dropoff-causes")
def get_trial_dropoff_causes(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date:   Optional[date] = Query(default=None),
    service_id: Optional[str]  = Query(default=None),
):
    start_dt, end_dt = resolve_date_range(start_date, end_date, db=db, source="subscription")

    cache_key = build_cache_key(
        "trial_dropoff_causes",
        {
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "service_id": service_id or "all",
            "v": "v1",
        },
    )

    return cache_or_compute(
        cache_key,
        settings.TRIAL_KPIS_CACHE_TTL_SECONDS,
        compute_function=lambda: _compute_trial_dropoff_causes(
            db=db,
            start_dt=start_dt,
            end_dt=end_dt,
            service_id=service_id,
        ),
    )


def _compute_trial_dropoff_causes(
    db: Session,
    start_dt: date,
    end_dt: date,
    service_id: Optional[str],
):
    anchor_dt = get_data_anchor(db, source="subscription")

    valid_service_id = None
    if service_id:
        try:
            valid_service_id = str(uuid.UUID(service_id))
        except ValueError:
            valid_service_id = None

    params = {
        "start_dt": start_dt,
        "end_dt": end_dt,
        "service_id": valid_service_id,
        "anchor_dt": anchor_dt,
    }

    sf = "AND s.service_id = CAST(:service_id AS uuid)" if valid_service_id else ""

    summary = db.execute(text(f"""
        WITH base AS (
            SELECT
                s.id AS subscription_id,
                COALESCE(
                    u.days_since_subscription,
                    GREATEST(
                        0,
                        EXTRACT(DAY FROM (
                            COALESCE(u.unsubscription_datetime, s.subscription_end_date, CAST(:anchor_dt AS timestamp))
                            - s.subscription_start_date
                        ))
                    )::int
                ) AS dropoff_days,
                UPPER(COALESCE(u.churn_type, '')) AS churn_type,
                NULLIF(TRIM(COALESCE(u.churn_reason, '')), '') AS churn_reason
            FROM subscriptions s
            LEFT JOIN unsubscriptions u ON u.subscription_id = s.id
            WHERE s.subscription_start_date >= CAST(:start_dt AS timestamp)
              AND s.subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
              AND s.subscription_start_date <= CAST(:anchor_dt AS timestamp)
              AND s.status IN ('cancelled', 'expired')
              {sf}
        )
        SELECT
            COUNT(*) AS total_dropoffs,
            COUNT(*) FILTER (WHERE dropoff_days <= 3) AS early_dropoffs_3d,
            COUNT(*) FILTER (WHERE churn_type = 'TECHNICAL') AS technical_dropoffs,
            COUNT(*) FILTER (WHERE churn_type = 'VOLUNTARY') AS voluntary_dropoffs
        FROM base
    """), params).fetchone()

    total_dropoffs = int(summary.total_dropoffs or 0)
    early_dropoffs_3d = int(summary.early_dropoffs_3d or 0)
    technical_dropoffs = int(summary.technical_dropoffs or 0)
    voluntary_dropoffs = int(summary.voluntary_dropoffs or 0)

    cause_rows = db.execute(text(f"""
        WITH base AS (
            SELECT
                COALESCE(
                    u.days_since_subscription,
                    GREATEST(
                        0,
                        EXTRACT(DAY FROM (
                            COALESCE(u.unsubscription_datetime, s.subscription_end_date, CAST(:anchor_dt AS timestamp))
                            - s.subscription_start_date
                        ))
                    )::int
                ) AS dropoff_days,
                UPPER(COALESCE(u.churn_type, '')) AS churn_type
            FROM subscriptions s
            LEFT JOIN unsubscriptions u ON u.subscription_id = s.id
            WHERE s.subscription_start_date >= CAST(:start_dt AS timestamp)
              AND s.subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
              AND s.subscription_start_date <= CAST(:anchor_dt AS timestamp)
              AND s.status IN ('cancelled', 'expired')
              {sf}
        )
        SELECT
            cause,
            COUNT(*) AS cnt
        FROM (
            SELECT
                CASE
                    WHEN churn_type = 'TECHNICAL' THEN 'Technical / billing friction'
                    WHEN churn_type = 'VOLUNTARY' THEN 'Voluntary opt-out'
                    WHEN dropoff_days <= 1 THEN 'No immediate value (D0-D1)'
                    WHEN dropoff_days <= 3 THEN 'Weak early engagement (D2-D3)'
                    ELSE 'Other / unclassified'
                END AS cause
            FROM base
        ) mapped
        GROUP BY cause
        ORDER BY cnt DESC
    """), params).fetchall()

    reason_rows = db.execute(text(f"""
        WITH base AS (
            SELECT
                NULLIF(TRIM(COALESCE(u.churn_reason, '')), '') AS churn_reason,
                UPPER(COALESCE(u.churn_type, '')) AS churn_type
            FROM subscriptions s
            LEFT JOIN unsubscriptions u ON u.subscription_id = s.id
            WHERE s.subscription_start_date >= CAST(:start_dt AS timestamp)
              AND s.subscription_start_date <= CAST(:end_dt AS timestamp) + INTERVAL '1 day'
              AND s.subscription_start_date <= CAST(:anchor_dt AS timestamp)
              AND s.status IN ('cancelled', 'expired')
              {sf}
        )
        SELECT
            COALESCE(
                churn_reason,
                CASE
                    WHEN churn_type = 'TECHNICAL' THEN 'Technical issue (unspecified)'
                    WHEN churn_type = 'VOLUNTARY' THEN 'User choice (unspecified)'
                    ELSE 'Reason not captured'
                END
            ) AS reason,
            COUNT(*) AS cnt
        FROM base
        GROUP BY reason
        ORDER BY cnt DESC
        LIMIT 5
    """), params).fetchall()

    cause_breakdown = []
    for row in cause_rows:
        pct = round((int(row.cnt or 0) * 100.0 / total_dropoffs), 1) if total_dropoffs > 0 else 0.0
        priority = "high" if pct >= 35 else "medium" if pct >= 15 else "low"
        cause_breakdown.append(
            {
                "cause": row.cause,
                "count": int(row.cnt or 0),
                "pct": pct,
                "priority": priority,
            }
        )

    top_reasons = []
    for row in reason_rows:
        pct = round((int(row.cnt or 0) * 100.0 / total_dropoffs), 1) if total_dropoffs > 0 else 0.0
        top_reasons.append(
            {
                "reason": row.reason,
                "count": int(row.cnt or 0),
                "pct": pct,
            }
        )

    early_dropoff_rate_pct = round((early_dropoffs_3d * 100.0 / total_dropoffs), 1) if total_dropoffs > 0 else 0.0
    technical_share_pct = round((technical_dropoffs * 100.0 / total_dropoffs), 1) if total_dropoffs > 0 else 0.0
    voluntary_share_pct = round((voluntary_dropoffs * 100.0 / total_dropoffs), 1) if total_dropoffs > 0 else 0.0

    notes = [
        f"{early_dropoff_rate_pct}% of drop-offs happen in the first 3 days.",
        f"Technical/billing friction represents {technical_share_pct}% of total drop-offs.",
        f"Voluntary opt-out represents {voluntary_share_pct}% of total drop-offs.",
    ]

    if cause_breakdown:
        top_cause = cause_breakdown[0]
        notes.append(
            f"Top driver: {top_cause['cause']} ({top_cause['pct']}% / {top_cause['count']} users)."
        )

    return {
        "summary": {
            "total_dropoffs": total_dropoffs,
            "early_dropoffs_3d": early_dropoffs_3d,
            "early_dropoff_rate_pct": early_dropoff_rate_pct,
            "technical_dropoffs": technical_dropoffs,
            "technical_share_pct": technical_share_pct,
            "voluntary_dropoffs": voluntary_dropoffs,
            "voluntary_share_pct": voluntary_share_pct,
        },
        "cause_breakdown": cause_breakdown,
        "top_reasons": top_reasons,
        "management_notes": notes,
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
    start_dt, end_dt = resolve_date_range(start_date, end_date, db=db, source="churn")

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
