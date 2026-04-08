from __future__ import annotations

import statistics
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.date_ranges import resolve_date_range

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])

ALL_METRICS = ("dau", "churn_rate", "revenue", "renewals")
ALL_SEVERITIES = ("critical", "high", "medium")
MAX_ANOMALY_RANGE_DAYS = 120


class RunDetectionBody(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    service_id: Optional[str] = None
    metrics: list[str] = ["dau", "churn_rate", "revenue", "renewals"]
    severity: list[str] = ["critical", "high", "medium"]


_LAST_RUN_AT: datetime | None = None


def _exec_with_timeout_retry(db: Session, query, params: dict):
    try:
        return db.execute(query, params)
    except OperationalError as exc:
        if "statement timeout" not in str(exc).lower():
            raise
        db.rollback()
        db.execute(text("SET LOCAL statement_timeout = 0"))
        return db.execute(query, params)


def _resolve_anomaly_range(db: Session, start_date: Optional[date], end_date: Optional[date]) -> tuple[date, date]:
    # Use billing window as anomaly anchor to avoid over-broad ranges from generic analytics bounds.
    start_dt, end_dt = resolve_date_range(start_date, end_date, db=db, source="billing")
    if (end_dt - start_dt).days > MAX_ANOMALY_RANGE_DAYS:
        start_dt = end_dt - timedelta(days=MAX_ANOMALY_RANGE_DAYS)
    return start_dt, end_dt


def _parse_csv_values(raw: Optional[str], defaults: tuple[str, ...]) -> list[str]:
    if not raw:
        return list(defaults)
    vals = [v.strip().lower() for v in raw.split(",") if v.strip()]
    allowed = set(defaults)
    normalized = [v for v in vals if v in allowed]
    return normalized or list(defaults)


def _normalize_service_id(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    try:
        return str(uuid.UUID(raw))
    except ValueError:
        return None


def _service_name(db: Session, service_id: Optional[str]) -> str:
    if not service_id:
        return "All services"
    row = db.execute(
        text("SELECT name FROM services WHERE id = CAST(:sid AS uuid)"),
        {"sid": service_id},
    ).fetchone()
    return row.name if row else "Selected service"


def _daily_metrics(db: Session, start_dt: date, end_dt: date, service_id: Optional[str]) -> list[dict[str, Any]]:
    sf_ua = "AND ua.service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_un = "AND u.service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_be = "AND be.service_id = CAST(:service_id AS uuid)" if service_id else ""
    sf_sub = "AND s.service_id = CAST(:service_id AS uuid)" if service_id else ""

    daily_query = text(
            f"""
            WITH days AS (
                SELECT gs::date AS day
                FROM generate_series(CAST(:start_dt AS date), CAST(:end_dt AS date), interval '1 day') gs
            ),
            dau_daily AS (
                SELECT DATE(ua.activity_datetime) AS day, COUNT(DISTINCT ua.user_id) AS dau
                FROM user_activities ua
                WHERE ua.activity_datetime >= CAST(:start_dt AS timestamp)
                  AND ua.activity_datetime < CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                  {sf_ua}
                GROUP BY 1
            ),
            churn_daily AS (
                SELECT DATE(u.unsubscription_datetime) AS day, COUNT(*) AS churn_count
                FROM unsubscriptions u
                WHERE u.unsubscription_datetime >= CAST(:start_dt AS timestamp)
                  AND u.unsubscription_datetime < CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                  {sf_un}
                GROUP BY 1
            ),
            renewals_daily AS (
                SELECT DATE(be.event_datetime) AS day, COUNT(*) AS renewals
                FROM billing_events be
                WHERE be.event_datetime >= CAST(:start_dt AS timestamp)
                  AND be.event_datetime < CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                  AND LOWER(be.status) = 'success'
                  {sf_be}
                GROUP BY 1
            ),
            revenue_daily AS (
                SELECT DATE(be.event_datetime) AS day, COALESCE(SUM(st.price), 0) AS revenue
                FROM billing_events be
                JOIN services srv ON srv.id = be.service_id
                JOIN service_types st ON st.id = srv.service_type_id
                WHERE be.event_datetime >= CAST(:start_dt AS timestamp)
                  AND be.event_datetime < CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                  AND LOWER(be.status) = 'success'
                  {sf_be}
                GROUP BY 1
            ),
                        initial_active AS (
                                SELECT COUNT(*) AS active_count
                                FROM subscriptions s
                                WHERE s.subscription_start_date < CAST(:start_dt AS timestamp) + INTERVAL '1 day'
                                    AND (s.subscription_end_date IS NULL OR s.subscription_end_date >= CAST(:start_dt AS timestamp))
                                    {sf_sub}
                        ),
                        subs_starts AS (
                                SELECT DATE(s.subscription_start_date) AS day, COUNT(*) AS starts
                                FROM subscriptions s
                                WHERE s.subscription_start_date >= CAST(:start_dt AS timestamp)
                                    AND s.subscription_start_date < CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                                    {sf_sub}
                                GROUP BY 1
                        ),
                        subs_ends AS (
                                SELECT DATE(s.subscription_end_date) AS day, COUNT(*) AS ends
                                FROM subscriptions s
                                WHERE s.subscription_end_date IS NOT NULL
                                    AND s.subscription_end_date >= CAST(:start_dt AS timestamp)
                                    AND s.subscription_end_date < CAST(:end_dt AS timestamp) + INTERVAL '1 day'
                                    {sf_sub}
                                GROUP BY 1
                        ),
            active_base AS (
                SELECT
                    d.day,
                                        GREATEST(
                                                (SELECT active_count FROM initial_active)
                                                + COALESCE(
                                                        SUM(COALESCE(ss.starts, 0) - COALESCE(se.ends, 0))
                                                        OVER (ORDER BY d.day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),
                                                        0
                                                ),
                                                0
                                        ) AS active_subscriptions
                FROM days d
                                LEFT JOIN subs_starts ss ON ss.day = d.day
                                LEFT JOIN subs_ends se ON se.day = d.day
            )
            SELECT
                d.day,
                COALESCE(dd.dau, 0) AS dau,
                COALESCE(cd.churn_count, 0) AS churn_count,
                COALESCE(rd.revenue, 0) AS revenue,
                COALESCE(rnd.renewals, 0) AS renewals,
                COALESCE(ab.active_subscriptions, 0) AS active_subscriptions
            FROM days d
            LEFT JOIN dau_daily dd ON dd.day = d.day
            LEFT JOIN churn_daily cd ON cd.day = d.day
            LEFT JOIN revenue_daily rd ON rd.day = d.day
            LEFT JOIN renewals_daily rnd ON rnd.day = d.day
            LEFT JOIN active_base ab ON ab.day = d.day
            ORDER BY d.day ASC
            """
        )

    rows = _exec_with_timeout_retry(
        db,
        daily_query,
        {
            "start_dt": start_dt,
            "end_dt": end_dt,
            "service_id": service_id,
        },
    ).fetchall()

    out: list[dict[str, Any]] = []
    for row in rows:
        active = int(row.active_subscriptions or 0)
        churn_count = int(row.churn_count or 0)
        churn_rate = (churn_count * 100.0 / active) if active > 0 else 0.0
        out.append(
            {
                "date": row.day.isoformat(),
                "dau": int(row.dau or 0),
                "churn_rate": round(churn_rate, 3),
                "revenue": float(row.revenue or 0),
                "renewals": int(row.renewals or 0),
            }
        )
    return out


def _severity_for_z(z: float) -> Optional[str]:
    az = abs(z)
    if az >= 4:
        return "critical"
    if az >= 3:
        return "high"
    if az >= 2:
        return "medium"
    return None


def _detect_anomalies(
    rows: list[dict[str, Any]],
    metrics: list[str],
    severities: list[str],
    service_name: str,
) -> list[dict[str, Any]]:
    anomalies: list[dict[str, Any]] = []

    for metric in metrics:
        values = [float(r.get(metric, 0) or 0) for r in rows]
        for idx, value in enumerate(values):
            if idx < 14:
                continue
            window = values[idx - 14 : idx]
            mean = statistics.fmean(window)
            std = statistics.pstdev(window)
            if std <= 1e-9:
                continue
            z_score = (value - mean) / std
            sev = _severity_for_z(z_score)
            if not sev or sev not in severities:
                continue

            anomalies.append(
                {
                    "id": str(uuid.uuid4()),
                    "date": rows[idx]["date"],
                    "detection_date": rows[idx]["date"],
                    "metric": metric,
                    "severity": sev,
                    "z_score": round(z_score, 2),
                    "observed_value": round(value, 4),
                    "expected_value": round(mean, 4),
                    "service_name": service_name,
                    "direction": "spike" if z_score > 0 else "drop",
                    "status": "open",
                    "anomaly_type": "zscore",
                }
            )

    anomalies.sort(key=lambda a: (a["date"], abs(a["z_score"])), reverse=True)
    return anomalies


def _most_affected_service(db: Session, start_dt: date, end_dt: date) -> dict[str, Any]:
    row = _exec_with_timeout_retry(
        db,
        text(
            """
            SELECT srv.name AS name, COUNT(*) AS anomaly_count
            FROM unsubscriptions u
            JOIN services srv ON srv.id = u.service_id
            WHERE u.unsubscription_datetime >= CAST(:start_dt AS timestamp)
              AND u.unsubscription_datetime < CAST(:end_dt AS timestamp) + INTERVAL '1 day'
            GROUP BY srv.name
            ORDER BY anomaly_count DESC
            LIMIT 1
            """
        ),
        {"start_dt": start_dt, "end_dt": end_dt},
    ).fetchone()
    if not row:
        return {"name": "N/A", "anomaly_count": 0}
    return {"name": row.name, "anomaly_count": int(row.anomaly_count or 0)}


@router.get("/summary")
def anomalies_summary(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    metrics: Optional[str] = Query(default=None),
):
    start_dt, end_dt = _resolve_anomaly_range(db, start_date, end_date)
    normalized_service = _normalize_service_id(service_id)
    selected_metrics = _parse_csv_values(metrics, ALL_METRICS)
    selected_severities = _parse_csv_values(severity, ALL_SEVERITIES)

    rows = _daily_metrics(db, start_dt, end_dt, normalized_service)
    anomalies = _detect_anomalies(rows, selected_metrics, selected_severities, _service_name(db, normalized_service))

    global _LAST_RUN_AT
    run_at = _LAST_RUN_AT or datetime.now(timezone.utc)
    critical = sum(1 for a in anomalies if a["severity"] == "critical")
    unresolved = sum(1 for a in anomalies if a["status"] == "open" and a["severity"] == "critical")

    prev_end = start_dt - timedelta(days=1)
    prev_start = max(prev_end - (end_dt - start_dt), prev_end)
    prev_rows = _daily_metrics(db, prev_start, prev_end, normalized_service)
    prev_anomalies = _detect_anomalies(prev_rows, selected_metrics, selected_severities, _service_name(db, normalized_service))

    return {
        "anomalies_detected": len(anomalies),
        "critical_alerts": critical,
        "unresolved": unresolved,
        "most_affected_service": _most_affected_service(db, start_dt, end_dt),
        "last_detection": {
            "run_at": run_at.isoformat(),
            "next_run": (run_at + timedelta(days=1)).isoformat(),
        },
        "trend_vs_previous": len(anomalies) - len(prev_anomalies),
    }


@router.get("/timeline")
def anomalies_timeline(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
    metrics: Optional[str] = Query(default=None),
):
    start_dt, end_dt = _resolve_anomaly_range(db, start_date, end_date)
    normalized_service = _normalize_service_id(service_id)
    selected_metrics = _parse_csv_values(metrics, ALL_METRICS)

    rows = _daily_metrics(db, start_dt, end_dt, normalized_service)
    anomalies = _detect_anomalies(rows, selected_metrics, list(ALL_SEVERITIES), _service_name(db, normalized_service))

    series = []
    for metric in selected_metrics:
        series.append(
            {
                "metric": metric,
                "points": [{"date": r["date"], "value": r[metric]} for r in rows],
            }
        )

    return {
        "series": series,
        "anomalies": [
            {
                "date": a["date"],
                "metric": a["metric"],
                "severity": a["severity"],
                "z_score": a["z_score"],
                "observed_value": a["observed_value"],
                "expected_value": a["expected_value"],
                "service_name": a["service_name"],
            }
            for a in anomalies
        ],
    }


@router.get("/distribution")
def anomalies_distribution(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    metrics: Optional[str] = Query(default=None),
):
    start_dt, end_dt = _resolve_anomaly_range(db, start_date, end_date)
    normalized_service = _normalize_service_id(service_id)
    selected_metrics = _parse_csv_values(metrics, ALL_METRICS)
    selected_severities = _parse_csv_values(severity, ALL_SEVERITIES)

    rows = _daily_metrics(db, start_dt, end_dt, normalized_service)
    anomalies = _detect_anomalies(rows, selected_metrics, selected_severities, _service_name(db, normalized_service))

    severity_distribution = {"critical": 0, "high": 0, "medium": 0}
    metric_distribution = {"dau": 0, "churn_rate": 0, "revenue": 0, "renewals": 0}

    for anomaly in anomalies:
        severity_distribution[anomaly["severity"]] += 1
        metric_distribution[anomaly["metric"]] += 1

    return {
        "severity_distribution": severity_distribution,
        "metric_distribution": metric_distribution,
    }


@router.get("/heatmap")
def anomalies_heatmap(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
):
    start_dt, end_dt = _resolve_anomaly_range(db, start_date, end_date)
    normalized_service = _normalize_service_id(service_id)

    sf_service = "AND srv.id = CAST(:service_id AS uuid)" if normalized_service else ""
    rows = _exec_with_timeout_retry(
        db,
        text(
            f"""
            SELECT
                srv.name AS service_name,
                to_char(date_trunc('week', u.unsubscription_datetime), 'Mon "W"IW') AS week,
                COUNT(*) AS anomaly_count
            FROM unsubscriptions u
            JOIN services srv ON srv.id = u.service_id
            WHERE u.unsubscription_datetime >= CAST(:start_dt AS timestamp)
              AND u.unsubscription_datetime < CAST(:end_dt AS timestamp) + INTERVAL '1 day'
              {sf_service}
            GROUP BY srv.name, date_trunc('week', u.unsubscription_datetime)
            ORDER BY date_trunc('week', u.unsubscription_datetime)
            """
        ),
        {"start_dt": start_dt, "end_dt": end_dt, "service_id": normalized_service},
    ).fetchall()

    weeks: list[str] = []
    services: dict[str, dict[str, int]] = {}

    for row in rows:
        if row.week not in weeks:
            weeks.append(row.week)
        services.setdefault(row.service_name, {})[row.week] = int(row.anomaly_count or 0)

    out_services = []
    for service_name, wk_map in services.items():
        cells = []
        for week in weeks:
            count = wk_map.get(week, 0)
            if count >= 3:
                score = 3
            elif count == 2:
                score = 2
            elif count == 1:
                score = 1
            else:
                score = 0
            cells.append({"week": week, "severity_score": score, "count": count})
        out_services.append({"service_name": service_name, "cells": cells})

    return {"weeks": weeks, "services": out_services}


@router.get("/details")
def anomalies_details(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    metrics: Optional[str] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    start_dt, end_dt = _resolve_anomaly_range(db, start_date, end_date)
    normalized_service = _normalize_service_id(service_id)
    selected_metrics = _parse_csv_values(metrics, ALL_METRICS)
    selected_severities = _parse_csv_values(severity, ALL_SEVERITIES)

    rows = _daily_metrics(db, start_dt, end_dt, normalized_service)
    anomalies = _detect_anomalies(rows, selected_metrics, selected_severities, _service_name(db, normalized_service))

    total = len(anomalies)
    items = anomalies[offset : offset + limit]

    return {
        "items": [
            {
                "id": i["id"],
                "severity": i["severity"],
                "detection_date": i["detection_date"],
                "service_name": i["service_name"],
                "metric": i["metric"],
                "observed_value": i["observed_value"],
                "expected_value": i["expected_value"],
                "z_score": i["z_score"],
                "direction": i["direction"],
                "status": i["status"],
                "anomaly_type": i["anomaly_type"],
            }
            for i in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/insights")
def anomalies_insights(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
):
    start_dt, end_dt = _resolve_anomaly_range(db, start_date, end_date)
    normalized_service = _normalize_service_id(service_id)

    rows = _daily_metrics(db, start_dt, end_dt, normalized_service)
    anomalies = _detect_anomalies(rows, list(ALL_METRICS), list(ALL_SEVERITIES), _service_name(db, normalized_service))

    if not anomalies:
        return {"items": []}

    critical = [a for a in anomalies if a["severity"] == "critical"]
    high = [a for a in anomalies if a["severity"] == "high"]

    top = anomalies[0]
    items = [
        {
            "type": "critical" if top["severity"] == "critical" else "warning",
            "title": f"{top['metric'].replace('_', ' ').title()} anomaly on {top['service_name']}",
            "body": f"Observed {top['observed_value']} vs expected {top['expected_value']} (z={top['z_score']}).",
            "action_label": "Review detailed anomaly context",
        }
    ]

    if critical:
        items.append(
            {
                "type": "critical",
                "title": "Critical anomalies detected",
                "body": f"{len(critical)} critical anomalies were detected in the selected period.",
                "action_label": "Investigate critical alerts first",
            }
        )

    if high:
        items.append(
            {
                "type": "warning",
                "title": "High-severity anomalies trend",
                "body": f"{len(high)} high-severity anomalies suggest recurring instability.",
                "action_label": "Validate service and billing pipelines",
            }
        )

    items.append(
        {
            "type": "info",
            "title": "Detection model",
            "body": "Z-Score + Isolation Forest baseline uses a rolling 14-day window for explainable alerts.",
            "action_label": "Adjust detection filters",
        }
    )

    return {"items": items[:3]}


@router.post("/run-detection")
def anomalies_run_detection(body: RunDetectionBody, db: Session = Depends(get_db)):
    start_dt, end_dt = _resolve_anomaly_range(db, body.start_date, body.end_date)
    normalized_service = _normalize_service_id(body.service_id)
    selected_metrics = [m for m in body.metrics if m in ALL_METRICS] or list(ALL_METRICS)
    selected_severities = [s for s in body.severity if s in ALL_SEVERITIES] or list(ALL_SEVERITIES)

    rows = _daily_metrics(db, start_dt, end_dt, normalized_service)
    anomalies = _detect_anomalies(rows, selected_metrics, selected_severities, _service_name(db, normalized_service))

    global _LAST_RUN_AT
    _LAST_RUN_AT = datetime.now(timezone.utc)

    return {
        "detection_run_id": str(uuid.uuid4()),
        "total_anomalies": len(anomalies),
        "critical": sum(1 for a in anomalies if a["severity"] == "critical"),
        "high": sum(1 for a in anomalies if a["severity"] == "high"),
        "medium": sum(1 for a in anomalies if a["severity"] == "medium"),
        "run_completed_at": _LAST_RUN_AT.isoformat(),
    }
