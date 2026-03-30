from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.date_ranges import DATA_START_DATE, resolve_date_range
from app.core.dependencies import get_current_user
from app.services.campaign_service import get_campaign_dashboard, get_campaign_list
from app.repositories.campaign_repo import CampaignRepository


router = APIRouter(prefix="/analytics/campaigns", tags=["Campaign Impact"])


# ============================================================================
# NEW Campaign Dashboard Endpoints (using service layer)
# ============================================================================


@router.get("/dashboard")
def get_campaign_impact_dashboard(
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
):
    """
    Get complete campaign impact dashboard
    Includes KPIs, type breakdown, monthly trend, top campaigns
    Supports optional date range and service filtering
    """
    filters = {
        "start_date": start_date,
        "end_date": end_date,
        "service_id": service_id,
    }
    payload = get_campaign_dashboard(db, filters=filters)
    return payload


@router.get("/list")
def get_campaigns_list(
    status: Optional[str] = Query(None, description="Filter by status: all|completed|sent|scheduled"),
    campaign_type: Optional[str] = Query(None, description="Filter by type: all|welcome|promotion|retention|reactivation"),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    """
    Get paginated campaign list with impact metrics
    Supports filtering by status and campaign_type
    """
    payload = get_campaign_list(
        db,
        status_filter=status,
        campaign_type_filter=campaign_type,
        start_date=start_date,
        end_date=end_date,
        service_id=service_id,
        page=page,
        limit=limit,
    )
    return payload


@router.get("/overview")
def get_campaigns_overview(
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    """
    Get high-level campaign metrics summary
    Returns total campaigns, conversions, targeted audience, etc.
    """
    overview = CampaignRepository.get_campaigns_overview(db)
    return overview


@router.get("/by-type")
def get_campaigns_by_type(
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    """
    Get campaign impact aggregated by campaign type
    Breakdown: welcome, promotion, retention, reactivation
    """
    data = CampaignRepository.get_impact_by_type(db)
    return {"by_type": data}


@router.get("/top")
def get_top_campaigns(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    """
    Get top campaigns by conversion rate
    """
    data = CampaignRepository.get_top_campaigns(db, limit=limit)
    return {"top_campaigns": data}


@router.get("/trend")
def get_campaigns_trend(
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    """
    Get monthly campaign trend
    Aggregated metrics by month and campaign type
    """
    data = CampaignRepository.get_campaigns_monthly_trend(db)
    return {"monthly_trend": data}


# ============================================================================
# EXISTING Campaign Endpoints (preserved for backward compatibility)
# ============================================================================


def _resolve_date_range(
    db: Session,
    *,
    start_date: Optional[date],
    end_date: Optional[date],
    service_id: Optional[str],
) -> tuple[date, date]:
    _ = db
    _ = service_id
    return resolve_date_range(start_date, end_date)


@router.get("/kpis")
def get_campaign_kpis(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=DATA_START_DATE),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
):
    start_dt, end_dt = _resolve_date_range(db, start_date=start_date, end_date=end_date, service_id=service_id)

    params = {"start_dt": start_dt, "end_dt": end_dt, "service_id": service_id}
    sf = "AND c.service_id = CAST(:service_id AS uuid)" if service_id else ""

    totals = db.execute(
        text(
            f"""
            WITH per_campaign AS (
                SELECT
                    c.id AS campaign_id,
                    c.name AS campaign_name,
                    c.target_size,
                    COUNT(s.id) AS total_subs
                FROM campaigns c
                LEFT JOIN subscriptions s ON (
                    s.campaign_id = c.id
                    OR (
                        s.service_id = c.service_id
                        AND s.subscription_start_date BETWEEN
                            c.send_datetime - INTERVAL '1 day'
                            AND c.send_datetime + INTERVAL '7 days'
                    )
                )
                WHERE DATE(c.send_datetime) >= :start_dt
                  AND DATE(c.send_datetime) <= :end_dt
                  {sf}
                GROUP BY c.id, c.name, c.target_size
            ),
            d7 AS (
                SELECT
                    AVG(co.retention_d7) AS avg_d7
                FROM campaigns c
                LEFT JOIN cohorts co
                  ON co.service_id = c.service_id
                 AND co.cohort_date = date_trunc('month', c.send_datetime)::date
                WHERE DATE(c.send_datetime) >= :start_dt
                  AND DATE(c.send_datetime) <= :end_dt
                  {sf}
            )
            SELECT
                (SELECT COUNT(DISTINCT campaign_id) FROM per_campaign) AS total_campaigns,
                (SELECT COALESCE(SUM(total_subs), 0) FROM per_campaign) AS total_subs_from_campaigns,
                (SELECT COALESCE(AVG((total_subs::numeric / NULLIF(target_size, 0)) * 100), 0) FROM per_campaign) AS avg_conversion_rate,
                (SELECT COALESCE(avg_d7, 0) FROM d7) AS avg_retention_d7
            """
        ),
        params,
    ).fetchone()

    top = db.execute(
        text(
            f"""
            SELECT
                c.name AS campaign_name,
                COUNT(s.id) AS total_subs
            FROM campaigns c
            LEFT JOIN subscriptions s ON (
                s.campaign_id = c.id
                OR (
                    s.service_id = c.service_id
                    AND s.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
                )
            )
            WHERE DATE(c.send_datetime) >= :start_dt
              AND DATE(c.send_datetime) <= :end_dt
              {sf}
            GROUP BY c.id, c.name
            ORDER BY total_subs DESC
            LIMIT 1
            """
        ),
        params,
    ).fetchone()

    return {
        "total_campaigns": int(totals.total_campaigns or 0),
        "total_subs_from_campaigns": int(totals.total_subs_from_campaigns or 0),
        "avg_conversion_rate": float(totals.avg_conversion_rate or 0),
        "avg_retention_d7": float(totals.avg_retention_d7 or 0),
        "top_campaign_name": (top.campaign_name if top else None),
        "top_campaign_subs": int(top.total_subs or 0) if top else 0,
    }


@router.get("/performance")
def get_campaign_performance(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=DATA_START_DATE),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
):
    start_dt, end_dt = _resolve_date_range(db, start_date=start_date, end_date=end_date, service_id=service_id)
    params = {"start_dt": start_dt, "end_dt": end_dt, "service_id": service_id}
    sf = "AND c.service_id = CAST(:service_id AS uuid)" if service_id else ""

    rows = db.execute(
        text(
            f"""
            SELECT
              c.id   AS campaign_id,
              c.name AS name,
              c.send_datetime,
              c.target_size,
              sv.name AS service_name,
              COUNT(s.id) AS total_subs,
              COUNT(s.id) FILTER (WHERE s.status = 'active') AS active_subs,
              ROUND(COUNT(s.id) FILTER (WHERE s.status = 'active')::numeric / NULLIF(c.target_size,0) * 100, 2) AS conv_rate,
              ROUND(AVG(co.retention_d7), 2) AS avg_d7
            FROM campaigns c
            LEFT JOIN subscriptions s ON (
                s.campaign_id = c.id
                OR (
                    s.service_id = c.service_id
                    AND s.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
                )
            )
            JOIN services sv ON sv.id = c.service_id
            LEFT JOIN cohorts co ON co.service_id = c.service_id
              AND co.cohort_date = date_trunc('month', c.send_datetime)::date
            WHERE DATE(c.send_datetime) >= :start_dt
              AND DATE(c.send_datetime) <= :end_dt
              {sf}
            GROUP BY c.id, c.name, c.send_datetime, c.target_size, sv.name
            ORDER BY conv_rate DESC NULLS LAST;
            """
        ),
        params,
    ).fetchall()

    return {
        "data": [
            {
                "campaign_id": str(r.campaign_id),
                "name": r.name,
                "send_date": r.send_datetime.isoformat() if r.send_datetime else None,
                "target_size": int(r.target_size or 0),
                "service_name": r.service_name,
                "total_subs": int(r.total_subs or 0),
                "active_subs": int(r.active_subs or 0),
                "conv_rate": float(r.conv_rate or 0),
                "avg_d7": float(r.avg_d7 or 0),
            }
            for r in rows
        ]
    }


@router.get("/comparison")
def get_campaign_comparison(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=DATA_START_DATE),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
):
    start_dt, end_dt = _resolve_date_range(db, start_date=start_date, end_date=end_date, service_id=service_id)
    params = {"start_dt": start_dt, "end_dt": end_dt, "service_id": service_id}
    sf = "AND c.service_id = CAST(:service_id AS uuid)" if service_id else ""

    rows = db.execute(
        text(
            f"""
            WITH per_campaign AS (
              SELECT
                c.id,
                c.service_id,
                COUNT(s.id) FILTER (WHERE s.status = 'active') AS active_subs,
                ROUND(COUNT(s.id) FILTER (WHERE s.status = 'active')::numeric / NULLIF(c.target_size,0) * 100, 2) AS conv_rate
              FROM campaigns c
              LEFT JOIN subscriptions s ON (
                s.campaign_id = c.id
                OR (
                    s.service_id = c.service_id
                    AND s.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
                )
              )
              WHERE DATE(c.send_datetime) >= :start_dt
                AND DATE(c.send_datetime) <= :end_dt
                {sf}
              GROUP BY c.id, c.service_id, c.target_size
            )
            SELECT
              sv.name AS service,
              COUNT(DISTINCT c.id) AS total_campaigns,
              COUNT(s.id) FILTER (WHERE s.status = 'active') AS total_subs,
              ROUND(AVG(pc.conv_rate), 2) AS avg_conversion,
              ROUND(AVG(co.retention_d7), 2) AS avg_d7
            FROM services sv
            JOIN campaigns c ON c.service_id = sv.id
            LEFT JOIN subscriptions s ON (
                s.campaign_id = c.id
                OR (
                    s.service_id = c.service_id
                    AND s.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
                )
            )
            LEFT JOIN per_campaign pc ON pc.id = c.id
            LEFT JOIN cohorts co ON co.service_id = c.service_id
              AND co.cohort_date = date_trunc('month', c.send_datetime)::date
            WHERE DATE(c.send_datetime) >= :start_dt
              AND DATE(c.send_datetime) <= :end_dt
              {sf}
            GROUP BY sv.name
            ORDER BY avg_conversion DESC NULLS LAST;
            """
        ),
        params,
    ).fetchall()

    return {
        "data": [
            {
                "service": r.service,
                "total_campaigns": int(r.total_campaigns or 0),
                "total_subs": int(r.total_subs or 0),
                "avg_conversion": float(r.avg_conversion or 0),
                "avg_d7": float(r.avg_d7 or 0),
            }
            for r in rows
        ]
    }


@router.get("/timeline")
def get_campaign_timeline(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=DATA_START_DATE),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
):
    start_dt, end_dt = resolve_date_range(start_date, end_date)

    params = {"start_dt": start_dt, "end_dt": end_dt, "service_id": service_id}
    sf = "AND s.service_id = CAST(:service_id AS uuid)" if service_id else ""

    rows = db.execute(
        text(
            f"""
            WITH months AS (
              SELECT generate_series(
                date_trunc('month', CAST(:start_dt AS timestamp))::date,
                date_trunc('month', CAST(:end_dt   AS timestamp))::date,
                interval '1 month'
              )::date AS month_start
            ),
            campaign_subs AS (
              SELECT
                date_trunc('month', s.subscription_start_date)::date AS month_start,
                COUNT(DISTINCT s.id) AS campaign_subs
              FROM subscriptions s
              WHERE s.subscription_start_date >= CAST(:start_dt AS timestamp)
                AND s.subscription_start_date <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                AND (
                  -- Primary: has campaign_id
                  s.campaign_id IS NOT NULL
                  OR
                  -- Fallback: matches date+service window of ANY campaign
                  EXISTS (
                    SELECT 1 FROM campaigns c
                    WHERE s.service_id = c.service_id
                      AND s.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
                  )
                )
                {sf}
              GROUP BY 1
            ),
            organic_subs AS (
              SELECT
                date_trunc('month', s.subscription_start_date)::date AS month_start,
                COUNT(DISTINCT s.id) AS organic_subs
              FROM subscriptions s
              WHERE s.subscription_start_date >= CAST(:start_dt AS timestamp)
                AND s.subscription_start_date <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                AND (
                  -- No direct campaign_id link AND
                  s.campaign_id IS NULL
                  AND
                  -- Does not match any campaign's date+service window
                  NOT EXISTS (
                    SELECT 1 FROM campaigns c
                    WHERE s.service_id = c.service_id
                      AND s.subscription_start_date BETWEEN
                        c.send_datetime - INTERVAL '1 day'
                        AND c.send_datetime + INTERVAL '7 days'
                  )
                )
                {sf}
              GROUP BY 1
            )
            SELECT
              to_char(m.month_start, 'YYYY-MM') AS month,
              COALESCE(c.campaign_subs, 0) AS campaign_subs,
              COALESCE(o.organic_subs, 0)  AS organic_subs
            FROM months m
            LEFT JOIN campaign_subs c ON c.month_start = m.month_start
            LEFT JOIN organic_subs  o ON o.month_start = m.month_start
            ORDER BY m.month_start ASC;
            """
        ),
        params,
    ).fetchall()

    return {
        "data": [
            {
                "month": r.month,
                "campaign_subs": int(r.campaign_subs or 0),
                "organic_subs": int(r.organic_subs or 0),
            }
            for r in rows
        ]
    }

