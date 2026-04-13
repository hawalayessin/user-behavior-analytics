from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.utils.temporal import get_data_anchor


def get_nrr_payload(db: Session) -> dict[str, Any]:
    anchor_dt = get_data_anchor(db, source="billing")

    row = db.execute(
        text(
            """
            WITH params AS (
                SELECT
                    CAST(:anchor_dt AS timestamptz) AS anchor_dt,
                    date_trunc('month', CAST(:anchor_dt AS timestamptz)) AS month_start,
                    date_trunc('month', CAST(:anchor_dt AS timestamptz)) - INTERVAL '1 month' AS prev_month_start
            ),
            revenue_start AS (
                SELECT COALESCE(SUM(st.price), 0)::float AS value
                FROM billing_events be
                JOIN services srv ON srv.id = be.service_id
                JOIN service_types st ON st.id = srv.service_type_id
                CROSS JOIN params p
                WHERE LOWER(be.status) = 'success'
                  AND be.event_datetime >= p.prev_month_start
                  AND be.event_datetime < p.month_start
            ),
            revenue_renewed AS (
                SELECT COALESCE(SUM(st.price), 0)::float AS value
                FROM billing_events be
                JOIN services srv ON srv.id = be.service_id
                JOIN service_types st ON st.id = srv.service_type_id
                CROSS JOIN params p
                WHERE LOWER(be.status) = 'success'
                  AND be.event_datetime >= p.month_start
                  AND be.event_datetime < p.month_start + INTERVAL '1 month'
                  AND EXISTS (
                    SELECT 1
                    FROM billing_events be_prev
                    WHERE be_prev.user_id = be.user_id
                      AND be_prev.service_id = be.service_id
                      AND LOWER(be_prev.status) = 'success'
                      AND be_prev.event_datetime >= p.prev_month_start
                      AND be_prev.event_datetime < p.month_start
                  )
            ),
            revenue_churned AS (
                SELECT COALESCE(SUM(st.price), 0)::float AS value
                FROM billing_events be
                JOIN services srv ON srv.id = be.service_id
                JOIN service_types st ON st.id = srv.service_type_id
                CROSS JOIN params p
                WHERE LOWER(be.status) IN ('failed')
                  AND be.event_datetime >= p.month_start
                  AND be.event_datetime < p.month_start + INTERVAL '1 month'
            )
            SELECT
                rs.value AS revenue_start,
                rr.value AS revenue_renewed,
                rc.value AS revenue_churned,
                to_char((SELECT month_start FROM params), 'FMMonth YYYY') AS period_label
            FROM revenue_start rs
            CROSS JOIN revenue_renewed rr
            CROSS JOIN revenue_churned rc
            """
        ),
        {"anchor_dt": anchor_dt},
    ).fetchone()

    revenue_start = float(row.revenue_start or 0.0) if row else 0.0
    revenue_renewed = float(row.revenue_renewed or 0.0) if row else 0.0
    revenue_churned = float(row.revenue_churned or 0.0) if row else 0.0
    revenue_expansion = 0.0  # Upsell/upgrade non disponible dans le schema actuel.

    nrr_percent = 0.0
    if revenue_start > 0:
        nrr_percent = round(((revenue_renewed + revenue_expansion - revenue_churned) / revenue_start) * 100.0, 2)

    return {
        "nrr_percent": nrr_percent,
        "revenue_start": round(revenue_start, 2),
        "revenue_renewed": round(revenue_renewed, 2),
        "revenue_churned": round(revenue_churned, 2),
        "revenue_expansion": revenue_expansion,
        "period_label": (row.period_label.strip() if row and row.period_label else "N/A"),
        "calculated_at": datetime.now(timezone.utc).isoformat(),
    }
