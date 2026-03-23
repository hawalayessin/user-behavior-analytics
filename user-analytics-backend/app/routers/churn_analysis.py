from __future__ import annotations

from datetime import date, timedelta
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.platform_users import PlatformUser
from app.schemas.churn_analysis import (
    ChurnCurvePoint,
    ChurnKPIsResponse,
    ChurnReasonRow,
    RiskSegmentRow,
    TimeToChurnBucketRow,
)


router = APIRouter(prefix="/analytics/churn", tags=["Churn Analysis"])

ChurnTypeFilter = Literal["ALL", "VOLUNTARY", "TECHNICAL"]


def _resolve_date_range(
    db: Session,
    *,
    start_date: Optional[date],
    end_date: Optional[date],
    service_id: Optional[str],
) -> tuple[date, date]:
    if start_date is None and end_date is None:
        sf = "WHERE service_id = CAST(:service_id AS uuid)" if service_id else ""
        row = db.execute(
            text(
                f"""
                SELECT
                  MIN(DATE(unsubscription_datetime)) AS min_d,
                  MAX(DATE(unsubscription_datetime)) AS max_d
                FROM unsubscriptions
                {sf}
                """
            ),
            {"service_id": service_id},
        ).fetchone()
        end_dt = row.max_d or date.today()
        start_dt = row.min_d or (end_dt - timedelta(days=90))
        return start_dt, end_dt

    end_dt = end_date or date.today()
    start_dt = start_date or (end_dt - timedelta(days=90))
    return start_dt, end_dt


def _churn_facts_cte(service_filter_sql: str = "") -> str:
    return f"""
    WITH churn_facts AS (
      SELECT
        s.id AS subscription_id,
        s.user_id,
        s.service_id,
        sv.name AS service_name,
        st.billing_frequency_days,
        st.trial_duration_days,
        s.subscription_start_date,
        s.subscription_end_date,
        u.unsubscription_datetime,
        u.churn_type,
        u.churn_reason,
        u.days_since_subscription,
        be_first.event_datetime AS first_charge_date,
        EXTRACT(DAY FROM (u.unsubscription_datetime - s.subscription_start_date))::int AS days_to_churn,
        CASE
          WHEN u.unsubscription_datetime IS NULL THEN FALSE
          WHEN u.days_since_subscription <= st.trial_duration_days THEN TRUE
          ELSE FALSE
        END AS is_trial_churn,
        CASE
          WHEN u.unsubscription_datetime IS NOT NULL
               AND be_first.event_datetime IS NOT NULL
          THEN EXTRACT(DAY FROM (u.unsubscription_datetime - be_first.event_datetime))::int
          ELSE NULL
        END AS days_after_first_charge
      FROM subscriptions s
      JOIN services sv ON sv.id = s.service_id
      JOIN service_types st ON st.id = sv.service_type_id
      LEFT JOIN unsubscriptions u ON u.subscription_id = s.id
      LEFT JOIN LATERAL (
        SELECT be.event_datetime
        FROM billing_events be
        WHERE be.subscription_id = s.id
          AND be.is_first_charge = TRUE
          AND be.status = 'SUCCESS'
        ORDER BY be.event_datetime ASC
        LIMIT 1
      ) be_first ON TRUE
      {service_filter_sql}
    )
    """


@router.get("/kpis", response_model=ChurnKPIsResponse)
def get_churn_kpis(
    db: Session = Depends(get_db),
    _: PlatformUser = Depends(get_current_user),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
) -> ChurnKPIsResponse:
    start_dt, end_dt = _resolve_date_range(db, start_date=start_date, end_date=end_date, service_id=service_id)

    params = {"start_dt": start_dt, "end_dt": end_dt, "service_id": service_id}
    sf_sub = "AND s.service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_cte = f"WHERE s.service_id = CAST(:service_id AS uuid)" if service_id else ""

    row = db.execute(
        text(
            f"""
            {_churn_facts_cte(sf_cte)}
            , active_start AS (
              SELECT COUNT(DISTINCT s.id) AS active_at_start
              FROM subscriptions s
              WHERE s.subscription_start_date < CAST(:start_dt AS timestamp) + INTERVAL '1 day'
                AND (s.subscription_end_date IS NULL OR s.subscription_end_date >= CAST(:start_dt AS timestamp))
                {sf_sub}
            ),
            churned_in_period AS (
              SELECT *
              FROM churn_facts cf
              WHERE cf.unsubscription_datetime IS NOT NULL
                AND DATE(cf.unsubscription_datetime) >= :start_dt
                AND DATE(cf.unsubscription_datetime) <= :end_dt
            )
            SELECT
              (SELECT active_at_start FROM active_start) AS active_at_start,
              (SELECT COUNT(*) FROM churned_in_period) AS churned_count,
              (SELECT COALESCE(AVG(days_to_churn::numeric), 0) FROM churned_in_period) AS avg_lifetime_days,
              (SELECT COALESCE(100.0 * COUNT(*) FILTER (WHERE churn_type = 'VOLUNTARY') / NULLIF(COUNT(*), 0), 0) FROM churned_in_period) AS voluntary_pct,
              (SELECT COALESCE(100.0 * COUNT(*) FILTER (WHERE churn_type = 'TECHNICAL') / NULLIF(COUNT(*), 0), 0) FROM churned_in_period) AS technical_pct,
              (SELECT COALESCE(100.0 * COUNT(*) FILTER (WHERE is_trial_churn = TRUE) / NULLIF(COUNT(*), 0), 0) FROM churned_in_period) AS trial_churn_pct,
              (SELECT COALESCE(100.0 * COUNT(*) FILTER (WHERE is_trial_churn = FALSE) / NULLIF(COUNT(*), 0), 0) FROM churned_in_period) AS paid_churn_pct,
              (SELECT COALESCE(100.0 * COUNT(*) FILTER (WHERE days_after_first_charge BETWEEN 0 AND 7) / NULLIF(COUNT(*) FILTER (WHERE first_charge_date IS NOT NULL), 0), 0)
               FROM churned_in_period) AS first_bill_churn_rate
            """
        ),
        params,
    ).fetchone()

    active_at_start = int(row.active_at_start or 0)
    churned = int(row.churned_count or 0)
    global_churn_rate = (float(churned) / float(active_at_start) * 100.0) if active_at_start else 0.0

    return ChurnKPIsResponse(
        global_churn_rate=round(global_churn_rate, 2),
        avg_lifetime_days=float(row.avg_lifetime_days or 0),
        first_bill_churn_rate=float(row.first_bill_churn_rate or 0),
        voluntary_pct=float(row.voluntary_pct or 0),
        technical_pct=float(row.technical_pct or 0),
        trial_churn_pct=float(row.trial_churn_pct or 0),
        paid_churn_pct=float(row.paid_churn_pct or 0),
    )


@router.get("/curve", response_model=list[ChurnCurvePoint])
def get_churn_curve(
    db: Session = Depends(get_db),
    _: PlatformUser = Depends(get_current_user),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
) -> list[ChurnCurvePoint]:
    start_dt, end_dt = _resolve_date_range(db, start_date=start_date, end_date=end_date, service_id=service_id)

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
            services_scope AS (
              SELECT sv.id AS service_id, sv.name AS service_name
              FROM services sv
              WHERE sv.is_active = true
              {"AND sv.id = CAST(:service_id AS uuid)" if service_id else ""}
            ),
            active_start AS (
              SELECT
                m.month_start,
                s.service_id,
                COUNT(DISTINCT s.id) AS active_at_start
              FROM months m
              JOIN subscriptions s
                ON s.subscription_start_date < (m.month_start::timestamp + INTERVAL '1 day')
               AND (s.subscription_end_date IS NULL OR s.subscription_end_date >= m.month_start::timestamp)
              WHERE 1=1
                {sf}
              GROUP BY 1, 2
            ),
            churned AS (
              SELECT
                date_trunc('month', u.unsubscription_datetime)::date AS month_start,
                u.service_id,
                COUNT(DISTINCT u.subscription_id) AS churned_count
              FROM unsubscriptions u
              WHERE DATE(u.unsubscription_datetime) >= :start_dt
                AND DATE(u.unsubscription_datetime) <= :end_dt
                {"AND u.service_id = CAST(:service_id AS uuid)" if service_id else ""}
              GROUP BY 1, 2
            ),
            new_subs AS (
              SELECT
                date_trunc('month', s.subscription_start_date)::date AS month_start,
                s.service_id,
                COUNT(DISTINCT s.id) AS new_subscriptions
              FROM subscriptions s
              WHERE DATE(s.subscription_start_date) >= :start_dt
                AND DATE(s.subscription_start_date) <= :end_dt
                {sf}
              GROUP BY 1, 2
            )
            SELECT
              to_char(m.month_start, 'YYYY-MM') AS month,
              ss.service_name,
              COALESCE(c.churned_count, 0) AS churned_count,
              COALESCE(a.active_at_start, 0) AS active_at_start,
              COALESCE(n.new_subscriptions, 0) AS new_subscriptions
            FROM months m
            CROSS JOIN services_scope ss
            LEFT JOIN churned c ON c.month_start = m.month_start AND c.service_id = ss.service_id
            LEFT JOIN active_start a ON a.month_start = m.month_start AND a.service_id = ss.service_id
            LEFT JOIN new_subs n ON n.month_start = m.month_start AND n.service_id = ss.service_id
            ORDER BY m.month_start ASC, ss.service_name ASC;
            """
        ),
        params,
    ).fetchall()

    out: list[ChurnCurvePoint] = []
    for r in rows:
        active_at_start = int(r.active_at_start or 0)
        churned_count = int(r.churned_count or 0)
        churn_rate = (float(churned_count) / float(active_at_start) * 100.0) if active_at_start else 0.0
        # It is possible for churned_count > active_at_start (data delays / late unsubs / overlapping definitions).
        # Keep API stable for charts by bounding rates to [0, 100].
        churn_rate = max(0.0, min(100.0, churn_rate))
        churn_rate = round(churn_rate, 2)
        out.append(
            ChurnCurvePoint(
                month=r.month,
                service_name=r.service_name,
                churn_rate=churn_rate,
                retention_rate=round(max(0.0, 100.0 - churn_rate), 2),
                new_subscriptions=int(r.new_subscriptions or 0),
            )
        )
    return out


@router.get("/time-to-churn", response_model=list[TimeToChurnBucketRow])
def get_time_to_churn(
    db: Session = Depends(get_db),
    _: PlatformUser = Depends(get_current_user),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
    churn_type: ChurnTypeFilter = Query(default="ALL"),
) -> list[TimeToChurnBucketRow]:
    start_dt, end_dt = _resolve_date_range(db, start_date=start_date, end_date=end_date, service_id=service_id)

    params = {"start_dt": start_dt, "end_dt": end_dt, "service_id": service_id, "churn_type": churn_type}
    sf_cte = "WHERE s.service_id = CAST(:service_id AS uuid)" if service_id else ""
    tf = "AND cf.churn_type = :churn_type" if churn_type != "ALL" else ""

    rows = db.execute(
        text(
            f"""
            {_churn_facts_cte(sf_cte)}
            SELECT
              cf.service_name,
              cf.churn_type,
              CASE
                WHEN cf.days_to_churn BETWEEN 0 AND 3 THEN '0-3 days'
                WHEN cf.days_to_churn BETWEEN 4 AND 7 THEN '4-7 days'
                WHEN cf.days_to_churn BETWEEN 8 AND 30 THEN '8-30 days'
                WHEN cf.days_to_churn BETWEEN 31 AND 90 THEN '31-90 days'
                WHEN cf.days_to_churn >= 91 THEN '90+ days'
                ELSE 'Unknown'
              END AS bucket,
              COUNT(*) AS count
            FROM churn_facts cf
            WHERE cf.unsubscription_datetime IS NOT NULL
              AND DATE(cf.unsubscription_datetime) >= :start_dt
              AND DATE(cf.unsubscription_datetime) <= :end_dt
              {tf}
            GROUP BY 1, 2, 3
            ORDER BY cf.service_name ASC, cf.churn_type ASC, count DESC;
            """
        ),
        params,
    ).fetchall()

    return [
        TimeToChurnBucketRow(
            service_name=r.service_name,
            churn_type=r.churn_type,
            bucket=r.bucket,
            count=int(r.count or 0),
        )
        for r in rows
        if r.churn_type in ("VOLUNTARY", "TECHNICAL")
    ]


@router.get("/reasons", response_model=list[ChurnReasonRow])
def get_churn_reasons(
    db: Session = Depends(get_db),
    _: PlatformUser = Depends(get_current_user),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
    churn_type: ChurnTypeFilter = Query(default="ALL"),
) -> list[ChurnReasonRow]:
    start_dt, end_dt = _resolve_date_range(db, start_date=start_date, end_date=end_date, service_id=service_id)

    params = {"start_dt": start_dt, "end_dt": end_dt, "service_id": service_id, "churn_type": churn_type}
    sf = "AND u.service_id = CAST(:service_id AS uuid)" if service_id else ""
    tf = "AND u.churn_type = :churn_type" if churn_type != "ALL" else ""

    rows = db.execute(
        text(
            f"""
            SELECT
              u.churn_type,
              COALESCE(NULLIF(TRIM(u.churn_reason), ''), 'Unknown') AS reason,
              COUNT(*) AS count
            FROM unsubscriptions u
            WHERE DATE(u.unsubscription_datetime) >= :start_dt
              AND DATE(u.unsubscription_datetime) <= :end_dt
              {sf}
              {tf}
            GROUP BY 1, 2
            ORDER BY count DESC
            LIMIT 10;
            """
        ),
        params,
    ).fetchall()

    return [
        ChurnReasonRow(churn_type=r.churn_type, reason=r.reason, count=int(r.count or 0))
        for r in rows
        if r.churn_type in ("VOLUNTARY", "TECHNICAL")
    ]


@router.get("/risk-segments", response_model=list[RiskSegmentRow])
def get_risk_segments(
    db: Session = Depends(get_db),
    _: PlatformUser = Depends(get_current_user),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
) -> list[RiskSegmentRow]:
    start_dt, end_dt = _resolve_date_range(db, start_date=start_date, end_date=end_date, service_id=service_id)

    params = {"start_dt": start_dt, "end_dt": end_dt, "service_id": service_id}
    sf = "AND x.service_id = CAST(:service_id AS uuid)" if service_id else ""

    rows = db.execute(
        text(
            f"""
            {_churn_facts_cte("")}
            , activity_7d AS (
              SELECT
                ua.user_id,
                ua.service_id,
                COUNT(*) AS activity_count_7d
              FROM user_activities ua
              WHERE ua.activity_datetime >= CAST(:end_dt AS timestamp) - INTERVAL '7 days'
                AND ua.activity_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                {"AND ua.service_id = CAST(:service_id AS uuid)" if service_id else ""}
              GROUP BY 1, 2
            ),
            failed_billing_30d AS (
              SELECT
                be.user_id,
                be.service_id,
                COUNT(*) AS failed_billing_30d
              FROM billing_events be
              WHERE be.status = 'FAILED'
                AND be.event_datetime >= CAST(:end_dt AS timestamp) - INTERVAL '30 days'
                AND be.event_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                {"AND be.service_id = CAST(:service_id AS uuid)" if service_id else ""}
              GROUP BY 1, 2
            ),
            seg_a AS (
              SELECT
                'SEG_A' AS segment_id,
                'Low activity + failed billing' AS label,
                'Users with <2 activities in last 7 days and >=1 failed billing event (last 30 days).' AS description,
                COUNT(DISTINCT COALESCE(a.user_id, f.user_id)) AS affected_users,
                ARRAY_AGG(DISTINCT sv.name) FILTER (WHERE sv.name IS NOT NULL) AS services
              FROM activity_7d a
              FULL OUTER JOIN failed_billing_30d f
                ON f.user_id = a.user_id AND f.service_id = a.service_id
              LEFT JOIN services sv ON sv.id = COALESCE(a.service_id, f.service_id)
              WHERE COALESCE(a.activity_count_7d, 0) < 2
                AND COALESCE(f.failed_billing_30d, 0) >= 1
            ),
            seg_b AS (
              SELECT
                'SEG_B' AS segment_id,
                'Early churn on weekly services' AS label,
                'Churned in <7 days for weekly-billed services.' AS description,
                COUNT(DISTINCT cf.user_id) AS affected_users,
                ARRAY_AGG(DISTINCT cf.service_name) AS services
              FROM churn_facts cf
              WHERE cf.unsubscription_datetime IS NOT NULL
                AND DATE(cf.unsubscription_datetime) >= :start_dt
                AND DATE(cf.unsubscription_datetime) <= :end_dt
                AND cf.days_to_churn < 7
                AND cf.billing_frequency_days = 7
                {("AND cf.service_id = CAST(:service_id AS uuid)" if service_id else "")}
            ),
            seg_c AS (
              SELECT
                'SEG_C' AS segment_id,
                'High trial churn services' AS label,
                'Services where trial churn represents >30% of churn events in the selected period.' AS description,
                COALESCE(SUM(trial_churned), 0)::int AS affected_users,
                ARRAY_AGG(service_name) FILTER (WHERE trial_rate > 30) AS services
              FROM (
                SELECT
                  cf.service_name,
                  COUNT(*) FILTER (WHERE cf.is_trial_churn = TRUE) AS trial_churned,
                  COALESCE(100.0 * COUNT(*) FILTER (WHERE cf.is_trial_churn = TRUE) / NULLIF(COUNT(*), 0), 0) AS trial_rate
                FROM churn_facts cf
                WHERE cf.unsubscription_datetime IS NOT NULL
                  AND DATE(cf.unsubscription_datetime) >= :start_dt
                  AND DATE(cf.unsubscription_datetime) <= :end_dt
                  {("AND cf.service_id = CAST(:service_id AS uuid)" if service_id else "")}
                GROUP BY 1
              ) x
            ),
            seg_d AS (
              SELECT
                'SEG_D' AS segment_id,
                'High first-bill failure rate' AS label,
                'Services with elevated first charge failures (first billing event marked is_first_charge).' AS description,
                COALESCE(SUM(failed_first_charge_users), 0)::int AS affected_users,
                ARRAY_AGG(service_name) FILTER (WHERE fail_rate > 20) AS services
              FROM (
                SELECT
                  sv.name AS service_name,
                  COUNT(*) FILTER (WHERE be.is_first_charge = TRUE AND be.status = 'FAILED') AS failed_first_charges,
                  COUNT(*) FILTER (WHERE be.is_first_charge = TRUE) AS total_first_charges,
                  COUNT(DISTINCT be.user_id) FILTER (WHERE be.is_first_charge = TRUE AND be.status = 'FAILED') AS failed_first_charge_users,
                  COALESCE(
                    100.0 * COUNT(*) FILTER (WHERE be.is_first_charge = TRUE AND be.status = 'FAILED')
                    / NULLIF(COUNT(*) FILTER (WHERE be.is_first_charge = TRUE), 0),
                    0
                  ) AS fail_rate
                FROM billing_events be
                JOIN services sv ON sv.id = be.service_id
                WHERE be.event_datetime >= CAST(:start_dt AS timestamp)
                  AND be.event_datetime <  CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                  AND be.is_first_charge = TRUE
                  {("AND be.service_id = CAST(:service_id AS uuid)" if service_id else "")}
                GROUP BY 1
              ) x
            )
            SELECT * FROM seg_a
            UNION ALL SELECT * FROM seg_b
            UNION ALL SELECT * FROM seg_c
            UNION ALL SELECT * FROM seg_d;
            """
        ),
        params,
    ).fetchall()

    def _top_services(arr: object) -> list[str]:
        if not arr:
            return []
        try:
            # psycopg2 returns list for array_agg; other drivers may return string.
            if isinstance(arr, list):
                return [s for s in arr if s][:3]
        except Exception:
            pass
        return []

    out: list[RiskSegmentRow] = []
    for r in rows:
        out.append(
            RiskSegmentRow(
                segment_id=r.segment_id,
                label=r.label,
                description=r.description,
                affected_users=int(r.affected_users or 0),
                top_services=_top_services(getattr(r, "services", None)),
            )
        )
    return out

