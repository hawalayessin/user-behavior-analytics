from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone

from app.core.database import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ══════════════════════════════════════════════════════════════
# GET /analytics/overview
# Vue globale Dashboard — équivalent Power BI Summary Page
# ══════════════════════════════════════════════════════════════

@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):

    # ── 1. USERS KPIs ─────────────────────────────────────────
    users = db.execute(text("""
        SELECT
            COUNT(*)                                                      AS total_users,
            COUNT(*) FILTER (WHERE status = 'active')                     AS active_users,
            COUNT(*) FILTER (WHERE status = 'inactive')                   AS inactive_users,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') AS new_last_30_days
        FROM users
    """)).fetchone()

    # ── 2. SUBSCRIPTIONS KPIs ─────────────────────────────────
    subs = db.execute(text("""
        SELECT
            COUNT(*)                                              AS total,
            COUNT(*) FILTER (WHERE status = 'active')            AS active,
            COUNT(*) FILTER (WHERE status = 'trial')             AS trial,
            COUNT(*) FILTER (WHERE status = 'expired')           AS expired,
            COUNT(*) FILTER (WHERE status = 'cancelled')         AS cancelled,
            -- Conversion rate : actifs / (actifs + expired + drop-off trial)
            ROUND(
                COUNT(*) FILTER (WHERE status = 'active') * 100.0
                / NULLIF(
                    COUNT(*) FILTER (WHERE status IN ('active', 'expired'))
                    + COUNT(*) FILTER (
                        WHERE status = 'cancelled'
                        AND (subscription_end_date - subscription_start_date)
                            <= INTERVAL '3 days'
                    ), 0
                ), 1
            )                                                     AS conversion_rate_pct
        FROM subscriptions
    """)).fetchone()

    # ── 3. CHURN KPIs ─────────────────────────────────────────
    churn = db.execute(text("""
        SELECT
            COUNT(*)                                                            AS total_unsubs,
            COUNT(*) FILTER (WHERE churn_type = 'VOLUNTARY')                   AS voluntary,
            COUNT(*) FILTER (WHERE churn_type = 'TECHNICAL')                   AS technical,
            ROUND(COUNT(*) FILTER (WHERE churn_type = 'VOLUNTARY') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                      AS voluntary_pct,
            ROUND(COUNT(*) FILTER (WHERE churn_type = 'TECHNICAL') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                      AS technical_pct,
            -- Drop-off trial J1/J2/J3
            COUNT(*) FILTER (WHERE days_since_subscription = 1)                AS dropoff_day1,
            COUNT(*) FILTER (WHERE days_since_subscription = 2)                AS dropoff_day2,
            COUNT(*) FILTER (WHERE days_since_subscription = 3)                AS dropoff_day3,
            -- Monthly churn rate
            ROUND(
                COUNT(*) FILTER (
                    WHERE unsubscription_datetime >= DATE_TRUNC('month', NOW())
                ) * 100.0
                / NULLIF((
                    SELECT COUNT(*) FROM subscriptions WHERE status = 'active'
                ), 0), 2
            )                                                                   AS churn_rate_month_pct
        FROM unsubscriptions
    """)).fetchone()

    # ── 4. REVENUE KPIs ───────────────────────────────────────
    revenue = db.execute(text("""
        SELECT
            -- Total revenue all time
            ROUND(SUM(st.price) FILTER (WHERE be.status = 'SUCCESS'), 2)       AS total_revenue,
            COUNT(*) FILTER (WHERE be.status = 'SUCCESS')                      AS success_events,
            COUNT(*) FILTER (WHERE be.status = 'FAILED')                       AS failed_events,
            ROUND(COUNT(*) FILTER (WHERE be.status = 'FAILED') * 100.0
                / NULLIF(COUNT(*), 0), 1)                                      AS failed_pct,
            -- MRR : revenue du mois en cours
            ROUND(SUM(st.price) FILTER (
                WHERE be.status = 'SUCCESS'
                AND be.event_datetime >= DATE_TRUNC('month', NOW())
            ), 2)                                                               AS mrr,
            -- ARPU mois en cours
            ROUND(
                SUM(st.price) FILTER (
                    WHERE be.status = 'SUCCESS'
                    AND be.event_datetime >= DATE_TRUNC('month', NOW())
                )
                / NULLIF(COUNT(DISTINCT be.user_id) FILTER (
                    WHERE be.status = 'SUCCESS'
                    AND be.event_datetime >= DATE_TRUNC('month', NOW())
                ), 0), 2
            )                                                                   AS arpu_current_month
        FROM billing_events be
        JOIN subscriptions  s   ON s.id   = be.subscription_id
        JOIN services       srv ON srv.id = s.service_id
        JOIN service_types  st  ON st.id  = srv.service_type_id
    """)).fetchone()

    # ── 5. ENGAGEMENT KPIs ────────────────────────────────────
    engagement = db.execute(text("""
        SELECT
            -- DAU today
            COUNT(DISTINCT user_id) FILTER (
                WHERE DATE(activity_datetime) = CURRENT_DATE
            )                                                   AS dau_today,
            -- MAU current month
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime >= DATE_TRUNC('month', NOW())
            )                                                   AS mau_current_month,
            -- WAU current week
            COUNT(DISTINCT user_id) FILTER (
                WHERE activity_datetime >= DATE_TRUNC('week', NOW())
            )                                                   AS wau_current_week
        FROM user_activities
    """)).fetchone()

    # Stickiness = DAU / MAU × 100
    dau   = engagement.dau_today        or 0
    mau   = engagement.mau_current_month or 0
    stickiness = round((dau / mau * 100), 1) if mau > 0 else 0.0

    # ── 6. TOP SERVICES ───────────────────────────────────────
    top_services = db.execute(text("""
        SELECT
            srv.name                                            AS service_name,
            COUNT(*) FILTER (WHERE s.status = 'active')        AS active_subs,
            COUNT(*) FILTER (WHERE s.status = 'cancelled')     AS churned_subs,
            ROUND(
                COUNT(*) FILTER (WHERE s.status = 'cancelled') * 100.0
                / NULLIF(COUNT(*), 0), 1
            )                                                   AS churn_rate_pct
        FROM subscriptions s
        JOIN services srv ON srv.id = s.service_id
        GROUP BY srv.name
        ORDER BY active_subs DESC
    """)).fetchall()

    # ── Build response ────────────────────────────────────────
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),

        "users": {
            "total":              users.total_users,
            "active":             users.active_users,
            "inactive":           users.inactive_users,
            "new_last_30_days":   users.new_last_30_days,
        },

        "subscriptions": {
            "total":              subs.total,
            "active":             subs.active,
            "trial":              subs.trial,
            "expired":            subs.expired,
            "cancelled":          subs.cancelled,
            "conversion_rate_pct": float(subs.conversion_rate_pct or 0),
        },

        "churn": {
            "total":              churn.total_unsubs,
            "voluntary":          churn.voluntary,
            "technical":          churn.technical,
            "voluntary_pct":      float(churn.voluntary_pct or 0),
            "technical_pct":      float(churn.technical_pct or 0),
            "churn_rate_month_pct": float(churn.churn_rate_month_pct or 0),
            "dropoff": {
                "day1":           churn.dropoff_day1,
                "day2":           churn.dropoff_day2,
                "day3":           churn.dropoff_day3,
            },
        },

        "revenue": {
            "total_revenue":      float(revenue.total_revenue    or 0),
            "mrr":                float(revenue.mrr              or 0),
            "arpu_current_month": float(revenue.arpu_current_month or 0),
            "billing_success":    revenue.success_events,
            "billing_failed":     revenue.failed_events,
            "failed_pct":         float(revenue.failed_pct       or 0),
        },

        "engagement": {
            "dau_today":          dau,
            "wau_current_week":   engagement.wau_current_week or 0,
            "mau_current_month":  mau,
            "stickiness_pct":     stickiness,
        },

        "top_services": [
            {
                "name":          row.service_name,
                "active_subs":   row.active_subs,
                "churned_subs":  row.churned_subs,
                "churn_rate_pct": float(row.churn_rate_pct or 0),
            }
            for row in top_services
        ],
    }
