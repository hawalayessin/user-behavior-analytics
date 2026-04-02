"""Segmentation repository built with SQL-first aggregations."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.utils.temporal import get_data_bounds


_SEGMENT_ORDER = ["Power Users", "Regular Loyals", "Occasional Users", "Trial Only"]
_SUCCESS_STATUS_SQL = "UPPER(TRIM(COALESCE(be.status, ''))) = 'SUCCESS'"


def _normalize_range(
    db: Session,
    start_date: date | datetime | None,
    end_date: date | datetime | None,
) -> tuple[datetime, datetime]:
    """Normalize requested range to billing data bounds."""
    data_start, data_end = get_data_bounds(db, source="billing")

    start = start_date or data_start
    end = end_date or data_end

    if isinstance(start, date) and not isinstance(start, datetime):
        start = datetime.combine(start, time.min)
    if isinstance(end, date) and not isinstance(end, datetime):
        end = datetime.combine(end, time.max)

    if start < data_start:
        start = data_start
    if end > data_end:
        end = data_end
    if start > end:
        start, end = end, start

    return start, end


def _service_filter(service_id: str | None, alias: str = "s") -> str:
    if not service_id:
        return ""
    return f"AND {alias}.service_id = CAST(:service_id AS uuid)"


def get_user_segments(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
    service_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return a bounded set of segmented users for scatter plotting."""
    start, end = _normalize_range(db, start_date, end_date)
    service_filter = _service_filter(service_id)

    rows = db.execute(
        text(
            f"""
            WITH user_stats AS (
                SELECT
                    s.user_id,
                    COUNT(be.id) FILTER (WHERE {_SUCCESS_STATUS_SQL}) AS billing_count,
                    COALESCE(
                        SUM(COALESCE(st.price, 0)) FILTER (WHERE {_SUCCESS_STATUS_SQL}),
                        0
                    ) AS revenue,
                    COUNT(DISTINCT DATE(be.event_datetime)) AS active_days,
                    COUNT(DISTINCT s.id) AS sub_count
                FROM subscriptions s
                JOIN billing_events be ON be.subscription_id = s.id
                JOIN services sv ON sv.id = s.service_id
                JOIN service_types st ON st.id = sv.service_type_id
                WHERE be.event_datetime BETWEEN :start AND :end
                  {service_filter}
                GROUP BY s.user_id
            ),
            percentiles AS (
                SELECT
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY billing_count) AS p25_billing,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY billing_count) AS p75_billing,
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY revenue) AS p25_revenue,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY revenue) AS p75_revenue
                FROM user_stats
                WHERE billing_count > 0
            ),
            segmented AS (
                SELECT
                    us.user_id,
                    us.billing_count,
                    us.revenue,
                    us.active_days,
                    CASE
                        WHEN COALESCE(p.p75_billing, 0) > 0
                        THEN LEAST(us.billing_count::float / p.p75_billing, 1.0)
                        ELSE 0
                    END AS x,
                    CASE
                        WHEN COALESCE(p.p75_revenue, 0) > 0
                        THEN LEAST(us.revenue::float / p.p75_revenue, 1.0)
                        ELSE 0
                    END AS y,
                    CASE
                        WHEN us.billing_count >= COALESCE(p.p75_billing, us.billing_count + 1)
                         AND us.revenue >= COALESCE(p.p75_revenue, us.revenue + 1)
                            THEN 'Power Users'
                        WHEN us.billing_count >= COALESCE(p.p25_billing, us.billing_count + 1)
                         AND us.revenue >= COALESCE(p.p25_revenue, us.revenue + 1)
                            THEN 'Regular Loyals'
                        WHEN us.billing_count > 0
                            THEN 'Occasional Users'
                        ELSE 'Trial Only'
                    END AS segment
                FROM user_stats us
                CROSS JOIN percentiles p
            )
            SELECT
                user_id::text AS user_id,
                x,
                y,
                segment,
                active_days,
                revenue
            FROM segmented
            ORDER BY revenue DESC
            LIMIT 50000
            """
        ),
        {
            "start": start,
            "end": end,
            "service_id": service_id,
        },
    ).fetchall()

    return [dict(row._mapping) for row in rows]


def get_segment_distribution(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
    service_id: str | None = None,
) -> dict[str, Any]:
    """Get full-segment distribution from SQL aggregation."""
    start, end = _normalize_range(db, start_date, end_date)
    service_filter = _service_filter(service_id)

    rows = db.execute(
        text(
            f"""
            WITH user_stats AS (
                SELECT
                    s.user_id,
                    COUNT(be.id) FILTER (WHERE {_SUCCESS_STATUS_SQL}) AS billing_count,
                    COALESCE(
                        SUM(COALESCE(st.price, 0)) FILTER (WHERE {_SUCCESS_STATUS_SQL}),
                        0
                    ) AS revenue
                FROM subscriptions s
                JOIN billing_events be ON be.subscription_id = s.id
                JOIN services sv ON sv.id = s.service_id
                JOIN service_types st ON st.id = sv.service_type_id
                WHERE be.event_datetime BETWEEN :start AND :end
                  {service_filter}
                GROUP BY s.user_id
            ),
            pct AS (
                SELECT
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY billing_count) AS p25_b,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY billing_count) AS p75_b,
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY revenue) AS p25_r,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY revenue) AS p75_r
                FROM user_stats
                WHERE billing_count > 0
            ),
            segmented AS (
                SELECT
                    CASE
                        WHEN us.billing_count >= COALESCE(pct.p75_b, us.billing_count + 1)
                         AND us.revenue >= COALESCE(pct.p75_r, us.revenue + 1)
                            THEN 'Power Users'
                        WHEN us.billing_count >= COALESCE(pct.p25_b, us.billing_count + 1)
                         AND us.revenue >= COALESCE(pct.p25_r, us.revenue + 1)
                            THEN 'Regular Loyals'
                        WHEN us.billing_count > 0
                            THEN 'Occasional Users'
                        ELSE 'Trial Only'
                    END AS segment
                FROM user_stats us
                CROSS JOIN pct
            ),
            stats AS (
                SELECT segment, COUNT(*) AS cnt
                FROM segmented
                GROUP BY segment
            ),
            totals AS (
                SELECT COALESCE(SUM(cnt), 0) AS total
                FROM stats
            )
            SELECT
                s.segment,
                s.cnt,
                CASE
                    WHEN t.total > 0 THEN ROUND((s.cnt * 100.0 / t.total)::numeric, 1)
                    ELSE 0
                END AS percentage
            FROM stats s
            CROSS JOIN totals t
            """
        ),
        {
            "start": start,
            "end": end,
            "service_id": service_id,
        },
    ).fetchall()

    rows_by_segment = {str(r._mapping["segment"]): r._mapping for r in rows}
    distribution: list[dict[str, Any]] = []
    total_users = 0

    for segment in _SEGMENT_ORDER:
        row = rows_by_segment.get(segment)
        count = int(row["cnt"]) if row else 0
        total_users += count
        distribution.append(
            {
                "name": segment,
                "percentage": float(row["percentage"]) if row else 0.0,
                "count": count,
            }
        )

    return {
        "distribution": distribution,
        "total_users": total_users,
    }


def get_segment_kpis(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
    service_id: str | None = None,
) -> dict[str, Any]:
    """Return dashboard KPIs in one SQL request."""
    start, end = _normalize_range(db, start_date, end_date)
    service_filter = _service_filter(service_id)

    row = db.execute(
        text(
            f"""
            WITH user_stats AS (
                SELECT
                    s.user_id,
                    COUNT(be.id) FILTER (WHERE {_SUCCESS_STATUS_SQL}) AS billing_count,
                    COALESCE(
                        SUM(COALESCE(st.price, 0)) FILTER (WHERE {_SUCCESS_STATUS_SQL}),
                        0
                    ) AS revenue
                FROM subscriptions s
                JOIN billing_events be ON be.subscription_id = s.id
                JOIN services sv ON sv.id = s.service_id
                JOIN service_types st ON st.id = sv.service_type_id
                WHERE be.event_datetime BETWEEN :start AND :end
                  {service_filter}
                GROUP BY s.user_id
            ),
            pct AS (
                SELECT
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY billing_count) AS p25_b,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY billing_count) AS p75_b,
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY revenue) AS p25_r,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY revenue) AS p75_r,
                    AVG(revenue) AS avg_revenue
                FROM user_stats
                WHERE billing_count > 0
            ),
            segmented AS (
                SELECT
                    us.user_id,
                    CASE
                        WHEN us.billing_count >= COALESCE(pct.p75_b, us.billing_count + 1)
                         AND us.revenue >= COALESCE(pct.p75_r, us.revenue + 1)
                            THEN 'Power Users'
                        WHEN us.billing_count >= COALESCE(pct.p25_b, us.billing_count + 1)
                         AND us.revenue >= COALESCE(pct.p25_r, us.revenue + 1)
                            THEN 'Regular Loyals'
                        WHEN us.billing_count > 0
                            THEN 'Occasional Users'
                        ELSE 'Trial Only'
                    END AS segment,
                    us.revenue
                FROM user_stats us
                CROSS JOIN pct
            ),
            stats AS (
                SELECT
                    segment,
                    COUNT(*) AS cnt,
                    AVG(revenue) AS avg_rev
                FROM segmented
                GROUP BY segment
            ),
            totals AS (
                SELECT COALESCE(SUM(cnt), 0) AS total
                FROM stats
            ),
            churn_stats AS (
                SELECT
                    seg.segment,
                    (
                        COUNT(DISTINCT sub.id) FILTER (WHERE sub.status IN ('cancelled', 'expired'))::float
                        / NULLIF(COUNT(DISTINCT sub.id), 0)
                    ) * 100 AS churn_pct
                FROM segmented seg
                JOIN subscriptions sub ON sub.user_id = seg.user_id
                GROUP BY seg.segment
            )
            SELECT
                (SELECT segment FROM stats ORDER BY cnt DESC LIMIT 1) AS dominant_segment,
                (
                    SELECT
                        CASE WHEN totals.total > 0 THEN cnt * 100.0 / totals.total ELSE 0 END
                    FROM stats, totals
                    ORDER BY cnt DESC
                    LIMIT 1
                ) AS dominant_pct,
                (SELECT segment FROM stats ORDER BY avg_rev DESC LIMIT 1) AS high_value_segment,
                (SELECT avg_rev FROM stats ORDER BY avg_rev DESC LIMIT 1) AS high_value_arpu,
                (SELECT avg_revenue FROM pct) AS overall_avg_arpu,
                (SELECT segment FROM churn_stats ORDER BY churn_pct DESC NULLS LAST LIMIT 1) AS risk_segment,
                (SELECT churn_pct FROM churn_stats ORDER BY churn_pct DESC NULLS LAST LIMIT 1) AS risk_churn_rate
            """
        ),
        {
            "start": start,
            "end": end,
            "service_id": service_id,
        },
    ).fetchone()

    if not row:
        return {
            "total_segments": 4,
            "dominant_segment": "N/A",
            "dominant_pct": 0.0,
            "high_value_segment": "N/A",
            "arpu_premium": 0.0,
            "risk_segment": "N/A",
            "risk_churn_rate": 0.0,
        }

    data = row._mapping
    avg_arpu = float(data["overall_avg_arpu"] or 0.0)
    high_value_arpu = float(data["high_value_arpu"] or 0.0)
    if avg_arpu <= 0:
        arpu_premium = 0.0
    else:
        arpu_premium = round((high_value_arpu / avg_arpu - 1.0) * 100.0, 1)

    return {
        "total_segments": 4,
        "dominant_segment": str(data["dominant_segment"] or "N/A"),
        "dominant_pct": round(float(data["dominant_pct"] or 0.0), 1),
        "high_value_segment": str(data["high_value_segment"] or "N/A"),
        "arpu_premium": arpu_premium,
        "risk_segment": str(data["risk_segment"] or "N/A"),
        "risk_churn_rate": -round(float(data["risk_churn_rate"] or 0.0), 1),
    }


def get_segment_profiles(
    db: Session,
    start_date: date | datetime | None = None,
    end_date: date | datetime | None = None,
    service_id: str | None = None,
) -> dict[str, Any]:
    """Return profiles with ARPU, usage duration and churn per segment."""
    start, end = _normalize_range(db, start_date, end_date)
    service_filter = _service_filter(service_id)

    rows = db.execute(
        text(
            f"""
            WITH user_stats AS (
                SELECT
                    s.user_id,
                    COUNT(be.id) FILTER (WHERE {_SUCCESS_STATUS_SQL}) AS billing_count,
                    COALESCE(
                        SUM(COALESCE(st.price, 0)) FILTER (WHERE {_SUCCESS_STATUS_SQL}),
                        0
                    ) AS revenue,
                    COUNT(DISTINCT DATE(be.event_datetime)) AS active_days
                FROM subscriptions s
                JOIN billing_events be ON be.subscription_id = s.id
                JOIN services sv ON sv.id = s.service_id
                JOIN service_types st ON st.id = sv.service_type_id
                WHERE be.event_datetime BETWEEN :start AND :end
                  {service_filter}
                GROUP BY s.user_id
            ),
            pct AS (
                SELECT
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY billing_count) AS p25_b,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY billing_count) AS p75_b,
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY revenue) AS p25_r,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY revenue) AS p75_r
                FROM user_stats
                WHERE billing_count > 0
            ),
            segmented AS (
                SELECT
                    us.user_id,
                    CASE
                        WHEN us.billing_count >= COALESCE(pct.p75_b, us.billing_count + 1)
                         AND us.revenue >= COALESCE(pct.p75_r, us.revenue + 1)
                            THEN 'Power Users'
                        WHEN us.billing_count >= COALESCE(pct.p25_b, us.billing_count + 1)
                         AND us.revenue >= COALESCE(pct.p25_r, us.revenue + 1)
                            THEN 'Regular Loyals'
                        WHEN us.billing_count > 0
                            THEN 'Occasional Users'
                        ELSE 'Trial Only'
                    END AS segment,
                    us.revenue,
                    us.active_days
                FROM user_stats us
                CROSS JOIN pct
            ),
            churn AS (
                SELECT
                    seg.segment,
                    (
                        COUNT(DISTINCT sub.id) FILTER (WHERE sub.status IN ('cancelled', 'expired'))::float
                        / NULLIF(COUNT(DISTINCT sub.id), 0)
                    ) * 100 AS churn_rate
                FROM segmented seg
                JOIN subscriptions sub ON sub.user_id = seg.user_id
                GROUP BY seg.segment
            ),
            profile_stats AS (
                SELECT
                    seg.segment,
                    AVG(seg.revenue) AS avg_arpu,
                    AVG(seg.active_days) AS avg_active_days,
                    COUNT(*) AS user_count
                FROM segmented seg
                GROUP BY seg.segment
            )
            SELECT
                ps.segment,
                ROUND(ps.avg_arpu::numeric, 2) AS arpu,
                ROUND(ps.avg_active_days::numeric, 1) AS avg_active_days,
                COALESCE(ROUND(c.churn_rate::numeric, 1), 0) AS churn_rate,
                ps.user_count
            FROM profile_stats ps
            LEFT JOIN churn c ON c.segment = ps.segment
            """
        ),
        {
            "start": start,
            "end": end,
            "service_id": service_id,
        },
    ).fetchall()

    rows_by_seg = {str(r._mapping["segment"]): r._mapping for r in rows}
    total_days = max((end - start).days, 1)

    profiles: list[dict[str, Any]] = []
    for segment in _SEGMENT_ORDER:
        row = rows_by_seg.get(segment)
        if row:
            avg_days = float(row["avg_active_days"] or 0.0)
            hours_day = (avg_days / total_days) * 24.0
            if hours_day >= 1:
                duration = f"{int(hours_day)}h / day"
            elif hours_day >= 0.1:
                duration = f"{hours_day:.1f}h / day"
            else:
                duration = "0h / day"

            profiles.append(
                {
                    "segment": segment,
                    "avg_duration": duration,
                    "arpu": float(row["arpu"] or 0.0),
                    "churn_rate": float(row["churn_rate"] or 0.0),
                }
            )
        else:
            profiles.append(
                {
                    "segment": segment,
                    "avg_duration": "0h / day",
                    "arpu": 0.0,
                    "churn_rate": 0.0,
                }
            )

    return {"profiles": profiles}
