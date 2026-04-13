from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.nrr import NRRResponse
from app.utils.temporal import get_data_anchor

router = APIRouter()


@router.get("/nrr", response_model=NRRResponse)
def get_nrr_kpi(
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    # NRR = ((Revenue Start + Expansion - Churn) / Revenue Start) x 100
    # >100% = growth from existing users
    # =100% = perfectly retained
    # <100% = net revenue loss from existing users
    anchor_dt = get_data_anchor(db, source="billing")

    # Cohort NRR: base = users who paid in previous month.
    # Schema adaptation:
    # - charge_success -> LOWER(status) = 'success'
    # - event_date -> event_datetime
    # - amount -> service_types.price
    row = db.execute(
        text(
            """
            WITH prev_payer_services AS (
                SELECT DISTINCT be.user_id, be.service_id
                FROM billing_events be
                WHERE LOWER(be.status) = 'success'
                  AND DATE_TRUNC('month', be.event_datetime) =
                      DATE_TRUNC('month', CAST(:anchor_date AS timestamptz)) - INTERVAL '1 month'
            ),
            rev_start AS (
                SELECT COALESCE(SUM(st.price), 0)::float AS total
                FROM prev_payer_services pps
                JOIN services srv ON srv.id = pps.service_id
                JOIN service_types st ON st.id = srv.service_type_id
            ),
            rev_renewed AS (
                SELECT COALESCE(SUM(st.price), 0)::float AS total
                FROM prev_payer_services pps
                JOIN services srv ON srv.id = pps.service_id
                JOIN service_types st ON st.id = srv.service_type_id
                WHERE EXISTS (
                    SELECT 1
                    FROM billing_events be
                    WHERE be.user_id = pps.user_id
                      AND be.service_id = pps.service_id
                      AND LOWER(be.status) = 'success'
                      AND DATE_TRUNC('month', be.event_datetime) =
                          DATE_TRUNC('month', CAST(:anchor_date AS timestamptz))
                )
            )
            SELECT
                ROUND(((r.total / NULLIF(s.total, 0)) * 100.0)::numeric, 1) AS nrr_percent,
                s.total AS revenue_start,
                r.total AS revenue_renewed,
                GREATEST(s.total - r.total, 0)::float AS revenue_churned,
                to_char(DATE_TRUNC('month', CAST(:anchor_date AS timestamptz)), 'FMMonth YYYY') AS period_label
            FROM rev_start s, rev_renewed r
            """
        ),
        {"anchor_date": anchor_dt},
    ).fetchone()

    revenue_start = float(row.revenue_start or 0.0) if row else 0.0
    revenue_renewed = float(row.revenue_renewed or 0.0) if row else 0.0
    revenue_churned = float(row.revenue_churned or 0.0) if row else 0.0
    revenue_expansion = 0.0  # No upsell data available in current schema.
    nrr_percent = float(row.nrr_percent or 0.0) if row else 0.0

    return {
        "nrr_percent": nrr_percent,
        "revenue_start": round(revenue_start, 2),
        "revenue_renewed": round(revenue_renewed, 2),
        "revenue_churned": round(revenue_churned, 2),
        "revenue_expansion": revenue_expansion,
        "period_label": (row.period_label.strip() if row and row.period_label else "N/A"),
        "calculated_at": datetime.now(timezone.utc).isoformat(),
    }
