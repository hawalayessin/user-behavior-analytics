from __future__ import annotations

import json
import logging
import statistics
import threading
import uuid
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sklearn.ensemble import IsolationForest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.cache import build_cache_key, cache_get_json, cache_set_json, cache_or_compute, get_redis_client
from app.core.database import SessionLocal, get_db
from app.core.dependencies import require_admin
from app.core.date_ranges import resolve_date_range
from app.utils.temporal import get_data_bounds

try:
    from cachetools import TTLCache
except ModuleNotFoundError:
    TTLCache = None  # type: ignore[assignment]

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])
logger = logging.getLogger(__name__)

ALL_METRICS = ("dau", "churn_rate", "revenue", "renewals")
ALL_SEVERITIES = ("critical", "high", "medium")
MAX_ANOMALY_RANGE_DAYS = 120
ENABLE_CACHE = True
DAILY_METRICS_CACHE_TTL_SECONDS = 180
ANOMALIES_CACHE_TTL_SECONDS = 120
MOST_AFFECTED_CACHE_TTL_SECONDS = 120
# "intersection" = higher precision, fewer false positives (recommended for production)
# "union" = higher recall, catches more edge cases but more noise
DETECTION_COMBINATION_MODE = "intersection"
ANOMALIES_CACHE_VERSION = "2026-05-05-v2-redis-shared-cache"
_job_start_lock = threading.Lock()
_JOBS_DIR = Path(__file__).resolve().parents[2] / "ml_models" / "anomaly_detection_jobs"

_METRIC_SOURCE_MAP: dict[str, tuple[str, ...]] = {
    "dau": ("usage",),
    "churn_rate": ("churn",),
    "revenue": ("billing",),
    "renewals": ("billing",),
}


class RunDetectionBody(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    service_id: Optional[str] = None
    metrics: list[str] = ["dau", "churn_rate", "revenue", "renewals"]
    severity: list[str] = ["critical", "high", "medium"]


_DAILY_METRICS_CACHE: dict[tuple[str, str, Optional[str]], list[dict[str, Any]]] = {}
_DAILY_METRICS_CACHE_EXPIRES_AT: dict[tuple[str, str, Optional[str]], datetime] = {}
_ANOMALIES_CACHE: dict[tuple[str, str, Optional[str], tuple[str, ...], tuple[str, ...], str], list[dict[str, Any]]] = {}
_ANOMALIES_CACHE_EXPIRES_AT: dict[
    tuple[str, str, Optional[str], tuple[str, ...], tuple[str, ...], str], datetime
] = {}
_MOST_AFFECTED_CACHE: dict[tuple[str, str], dict[str, Any]] = {}
_MOST_AFFECTED_CACHE_EXPIRES_AT: dict[tuple[str, str], datetime] = {}
if TTLCache is not None:
    _DAILY_METRICS_CACHE = TTLCache(maxsize=256, ttl=DAILY_METRICS_CACHE_TTL_SECONDS)  # type: ignore[assignment]
    _ANOMALIES_CACHE = TTLCache(maxsize=256, ttl=ANOMALIES_CACHE_TTL_SECONDS)  # type: ignore[assignment]
    _MOST_AFFECTED_CACHE = TTLCache(maxsize=128, ttl=MOST_AFFECTED_CACHE_TTL_SECONDS)  # type: ignore[assignment]


def _exec_with_timeout_retry(db: Session, query, params: dict):
    try:
        return db.execute(query, params)
    except OperationalError as exc:
        if "statement timeout" not in str(exc).lower():
            raise
        db.rollback()
        db.execute(text("SET LOCAL statement_timeout = 0"))
        return db.execute(query, params)


def _resolve_anomaly_range(
    db: Session,
    start_date: Optional[date],
    end_date: Optional[date],
    metrics: Optional[list[str]] = None,
) -> tuple[date, date]:
    # Build a safe intersection window for selected metrics so each metric can have real signal.
    selected_metrics = [m for m in (metrics or list(ALL_METRICS)) if m in ALL_METRICS] or list(ALL_METRICS)
    selected_sources = sorted({src for m in selected_metrics for src in _METRIC_SOURCE_MAP.get(m, tuple())}) or ["billing"]

    bounds = [get_data_bounds(db, source=src) for src in selected_sources]
    intersection_start = max(b[0] for b in bounds).date()
    intersection_end = min(b[1] for b in bounds).date()

    if intersection_start > intersection_end:
        # Fallback to billing anchor if sources do not overlap.
        start_dt, end_dt = resolve_date_range(start_date, end_date, db=db, source="billing")
    else:
        if start_date or end_date:
            requested_start, requested_end = resolve_date_range(start_date, end_date, db=db, source="analytics")
            start_dt = max(requested_start, intersection_start)
            end_dt = min(requested_end, intersection_end)
        else:
            end_dt = intersection_end
            start_dt = max(intersection_start, end_dt - timedelta(days=MAX_ANOMALY_RANGE_DAYS))

        if start_dt > end_dt:
            start_dt = end_dt

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
        # Overflow is possible when multiple delayed cancellations are booked on a day while active base is low.
        churn_rate = (churn_count * 100.0 / active) if active > 0 else 0.0
        churn_rate_overflow = churn_rate > 100.0
        out.append(
            {
                "date": row.day.isoformat(),
                "dau": int(row.dau or 0),
                "churn_rate": round(churn_rate, 3),
                "churn_rate_overflow": churn_rate_overflow,
                "revenue": float(row.revenue or 0),
                "renewals": int(row.renewals or 0),
            }
        )
    return out


def _get_daily_metrics_cached(db: Session, start_dt: date, end_dt: date, service_id: Optional[str]) -> list[dict[str, Any]]:
    if not ENABLE_CACHE:
        return _daily_metrics(db, start_dt, end_dt, service_id)

    redis_key = build_cache_key(
        "anomalies:daily_metrics",
        {
            "v": ANOMALIES_CACHE_VERSION,
            "start_dt": start_dt.isoformat(),
            "end_dt": end_dt.isoformat(),
            "service_id": service_id or "all",
        },
    )
    return cache_or_compute(
        redis_key,
        DAILY_METRICS_CACHE_TTL_SECONDS,
        lambda: _daily_metrics(db, start_dt, end_dt, service_id),
    )


def _severity_for_z(z: float) -> Optional[str]:
    az = abs(z)
    if az >= 4:
        return "critical"
    if az >= 3:
        return "high"
    if az >= 2:
        return "medium"
    return None


def _rt_log(message: str, *args: Any) -> None:
    """Realtime terminal log (stdout flush) + logger fallback."""
    rendered = message % args if args else message
    ts = datetime.now(timezone.utc).isoformat()
    line = f"[anomalies][{ts}] {rendered}"
    print(line, flush=True)
    logger.info(rendered)


def _detect_anomalies_isolation_forest(values: list[float], contamination: float = 0.05) -> set[int]:
    if len(values) < 10:
        return set()
    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=200,
    )
    reshaped = [[v] for v in values]
    preds = model.fit_predict(reshaped)
    return {idx for idx, pred in enumerate(preds) if pred == -1}


def _detect_anomalies(
    rows: list[dict[str, Any]],
    metrics: list[str],
    severities: list[str],
    service_name: str,
    combination_mode: str = DETECTION_COMBINATION_MODE,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> list[dict[str, Any]]:
    """
    The first 14 data points are excluded from detection as they serve
    as the initial rolling baseline. This is a known warm-up limitation.
    """
    anomalies: list[dict[str, Any]] = []

    for metric in metrics:
        if progress_callback:
            progress_callback(f"processing metric={metric}")
        values = [float(r.get(metric, 0) or 0) for r in rows]
        iso_indices = _detect_anomalies_isolation_forest(values)
        for idx, value in enumerate(values):
            z_flag = False
            z_score = 0.0
            expected_value = value
            sev: Optional[str] = None

            if idx < 14:
                mean = value
                std = 0.0
            else:
                window = values[idx - 14 : idx]
                mean = statistics.fmean(window)
                std = statistics.pstdev(window)
            expected_value = mean
            if std > 1e-9:
                z_score = (value - mean) / std
                sev = _severity_for_z(z_score)
                z_flag = sev is not None

            iso_flag = idx in iso_indices
            if combination_mode == "intersection":
                is_anomaly = z_flag and iso_flag
            else:
                is_anomaly = z_flag or iso_flag
            if not is_anomaly:
                continue

            if sev is None:
                sev = "medium"
            if sev not in severities:
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
                    "expected_value": round(expected_value, 4),
                    "service_name": service_name,
                    "direction": "spike" if z_score > 0 else "drop",
                    "status": "open",
                    "anomaly_type": "zscore+isolation_forest",
                    "churn_rate_overflow": rows[idx].get("churn_rate_overflow", False),
                }
            )
        if progress_callback:
            progress_callback(f"metric done={metric}")

    anomalies.sort(key=lambda a: (a["date"], abs(a["z_score"])), reverse=True)
    return anomalies


def _get_anomalies_cached(
    rows: list[dict[str, Any]],
    start_dt: date,
    end_dt: date,
    service_id: Optional[str],
    metrics: list[str],
    severities: list[str],
    service_name: str,
    combination_mode: str = DETECTION_COMBINATION_MODE,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> list[dict[str, Any]]:
    if ENABLE_CACHE and progress_callback is None:
        redis_key = build_cache_key(
            "anomalies:detected",
            {
                "v": ANOMALIES_CACHE_VERSION,
                "start_dt": start_dt.isoformat(),
                "end_dt": end_dt.isoformat(),
                "service_id": service_id or "all",
                "metrics": metrics,
                "severities": severities,
                "combination_mode": combination_mode,
            },
        )
        return cache_or_compute(
            redis_key,
            ANOMALIES_CACHE_TTL_SECONDS,
            lambda: _detect_anomalies(
                rows,
                metrics,
                severities,
                service_name,
                combination_mode=combination_mode,
                progress_callback=None,
            ),
        )

    return _detect_anomalies(
        rows,
        metrics,
        severities,
        service_name,
        combination_mode=combination_mode,
        progress_callback=progress_callback,
    )


def _run_detection_core(
    db: Session,
    start_date: Optional[date],
    end_date: Optional[date],
    service_id: Optional[str],
    metrics: list[str],
    severity: list[str],
    progress_callback: Optional[Callable[[str], None]] = None,
) -> dict[str, Any]:
    normalized_service = _normalize_service_id(service_id)
    selected_metrics = [m for m in metrics if m in ALL_METRICS] or list(ALL_METRICS)
    selected_severities = [s for s in severity if s in ALL_SEVERITIES] or list(ALL_SEVERITIES)
    start_dt, end_dt = _resolve_anomaly_range(db, start_date, end_date, selected_metrics)
    if progress_callback:
        progress_callback(
            f"Resolved params service={normalized_service or 'all'} range={start_dt.isoformat()}..{end_dt.isoformat()}"
        )

    rows = _get_daily_metrics_cached(db, start_dt, end_dt, normalized_service)
    if progress_callback:
        progress_callback(f"Daily metrics loaded ({len(rows)} rows)")

    anomalies = _get_anomalies_cached(
        rows,
        start_dt,
        end_dt,
        normalized_service,
        selected_metrics,
        selected_severities,
        _service_name(db, normalized_service),
        progress_callback=progress_callback,
    )
    return {
        "total_anomalies": len(anomalies),
        "critical": sum(1 for a in anomalies if a["severity"] == "critical"),
        "high": sum(1 for a in anomalies if a["severity"] == "high"),
        "medium": sum(1 for a in anomalies if a["severity"] == "medium"),
    }


def _save_job(job: dict[str, Any]) -> None:
    cache_set_json(f"detection_job:{job['job_id']}", job, 3600)
    _JOBS_DIR.mkdir(parents=True, exist_ok=True)
    job_path = _JOBS_DIR / f"{job['job_id']}.json"
    job_path.write_text(json.dumps(job, ensure_ascii=True, default=str), encoding="utf-8")


def _load_job(job_id: str) -> dict[str, Any] | None:
    payload = cache_get_json(f"detection_job:{job_id}")
    if isinstance(payload, dict):
        return payload
    job_path = _JOBS_DIR / f"{job_id}.json"
    if job_path.exists():
        try:
            file_payload = json.loads(job_path.read_text(encoding="utf-8"))
            if isinstance(file_payload, dict):
                return file_payload
        except (OSError, json.JSONDecodeError):
            return None
    return None


def _append_job_log(job_id: str, message: str, **extra: Any) -> None:
    job = _load_job(job_id)
    if not job:
        return
    payload = {"ts": datetime.now(timezone.utc).isoformat(), "message": message, **extra}
    job.setdefault("logs", []).append(payload)
    if len(job["logs"]) > 300:
        job["logs"] = job["logs"][-300:]
    _save_job(job)


def _find_running_job() -> dict[str, Any] | None:
    client = get_redis_client()
    if client is None:
        return None
    try:
        for key in client.scan_iter(match="detection_job:*", count=100):
            payload = cache_get_json(str(key))
            if isinstance(payload, dict) and payload.get("status") == "running":
                # vérifier que le job n'est pas "zombie" (démarré il y a > 10 min)
                started = payload.get("started_at", "")
                if started:
                    age = datetime.now(timezone.utc) - datetime.fromisoformat(started)
                    if age.total_seconds() > 600:  # 10 min timeout
                        continue  # job zombie, ignorer
                return payload
    except Exception:
        return None
    return None


def _run_detection_job(job_id: str) -> None:
    db = SessionLocal()
    started_at = datetime.now(timezone.utc)
    try:
        job = _load_job(job_id)
        if not job:
            return
        body = job["request"]
        _append_job_log(job_id, "Anomaly detection job started")
        result = _run_detection_core(
            db,
            start_date=body["start_date"],
            end_date=body["end_date"],
            service_id=body["service_id"],
            metrics=body["metrics"],
            severity=body["severity"],
            progress_callback=lambda msg: _append_job_log(job_id, msg),
        )
        took_ms = int((datetime.now(timezone.utc) - started_at).total_seconds() * 1000)
        _append_job_log(job_id, f"Detection completed in {took_ms}ms")
        job = _load_job(job_id)
        if not job:
            return
        job["result"] = {
            "detection_run_id": job_id,
            **result,
            "run_completed_at": datetime.now(timezone.utc).isoformat(),
        }
        job["status"] = "success"
        job["completed_at"] = datetime.now(timezone.utc).isoformat()
        _save_job(job)
    except Exception as exc:
        _append_job_log(job_id, "Detection failed", error=str(exc))
        job = _load_job(job_id)
        if not job:
            return
        job["status"] = "failed"
        job["error"] = str(exc)
        job["completed_at"] = datetime.now(timezone.utc).isoformat()
        _save_job(job)
    finally:
        db.close()


def _most_affected_service(db: Session, start_dt: date, end_dt: date) -> dict[str, Any]:
    def _compute() -> dict[str, Any]:
        services = _exec_with_timeout_retry(
            db,
            text(
                """
                SELECT CAST(id AS text) AS id, name
                FROM services
                """
            ),
            {},
        ).fetchall()

        top_name = "N/A"
        top_count = 0
        for srv in services:
            rows = _get_daily_metrics_cached(db, start_dt, end_dt, srv.id)
            anomalies = _get_anomalies_cached(
                rows,
                start_dt,
                end_dt,
                srv.id,
                list(ALL_METRICS),
                list(ALL_SEVERITIES),
                srv.name,
            )
            if len(anomalies) > top_count:
                top_name = srv.name
                top_count = len(anomalies)
        return {"name": "N/A", "anomaly_count": 0} if top_count == 0 else {"name": top_name, "anomaly_count": top_count}

    if not ENABLE_CACHE:
        return _compute()

    redis_key = build_cache_key(
        "anomalies:most_affected_service",
        {
            "v": ANOMALIES_CACHE_VERSION,
            "start_dt": start_dt.isoformat(),
            "end_dt": end_dt.isoformat(),
        },
    )
    return cache_or_compute(redis_key, MOST_AFFECTED_CACHE_TTL_SECONDS, _compute)


@router.get("/summary")
def anomalies_summary(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    service_id: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    metrics: Optional[str] = Query(default=None),
):
    normalized_service = _normalize_service_id(service_id)
    selected_metrics = _parse_csv_values(metrics, ALL_METRICS)
    selected_severities = _parse_csv_values(severity, ALL_SEVERITIES)
    start_dt, end_dt = _resolve_anomaly_range(db, start_date, end_date, selected_metrics)

    rows = _get_daily_metrics_cached(db, start_dt, end_dt, normalized_service)
    anomalies = _get_anomalies_cached(
        rows,
        start_dt,
        end_dt,
        normalized_service,
        selected_metrics,
        selected_severities,
        _service_name(db, normalized_service),
    )

    run_at = datetime.now(timezone.utc)
    critical = sum(1 for a in anomalies if a["severity"] == "critical")
    unresolved = sum(1 for a in anomalies if a["status"] == "open" and a["severity"] == "critical")

    prev_end = start_dt - timedelta(days=1)
    prev_start = max(prev_end - (end_dt - start_dt), prev_end)
    prev_rows = _get_daily_metrics_cached(db, prev_start, prev_end, normalized_service)
    prev_anomalies = _get_anomalies_cached(
        prev_rows,
        prev_start,
        prev_end,
        normalized_service,
        selected_metrics,
        selected_severities,
        _service_name(db, normalized_service),
    )

    return {
        "anomalies_detected": len(anomalies),
        "critical_alerts": critical,
        "unresolved": unresolved,
        "most_affected_service": _most_affected_service(db, start_dt, end_dt),
        "last_detection": {
            "run_at": run_at.isoformat(),
            "next_run": (run_at + timedelta(days=1)).isoformat(),
        },
        "detection_config": {
            "warmup_days": 14,
            "combination_mode": DETECTION_COMBINATION_MODE,
            "window_size": 14,
            "algorithm": "zscore+isolation_forest",
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
    normalized_service = _normalize_service_id(service_id)
    selected_metrics = _parse_csv_values(metrics, ALL_METRICS)
    start_dt, end_dt = _resolve_anomaly_range(db, start_date, end_date, selected_metrics)

    rows = _get_daily_metrics_cached(db, start_dt, end_dt, normalized_service)
    anomalies = _get_anomalies_cached(
        rows,
        start_dt,
        end_dt,
        normalized_service,
        selected_metrics,
        list(ALL_SEVERITIES),
        _service_name(db, normalized_service),
    )

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
    normalized_service = _normalize_service_id(service_id)
    selected_metrics = _parse_csv_values(metrics, ALL_METRICS)
    selected_severities = _parse_csv_values(severity, ALL_SEVERITIES)
    start_dt, end_dt = _resolve_anomaly_range(db, start_date, end_date, selected_metrics)

    rows = _get_daily_metrics_cached(db, start_dt, end_dt, normalized_service)
    anomalies = _get_anomalies_cached(
        rows,
        start_dt,
        end_dt,
        normalized_service,
        selected_metrics,
        selected_severities,
        _service_name(db, normalized_service),
    )

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
    start_dt, end_dt = _resolve_anomaly_range(db, start_date, end_date, list(ALL_METRICS))
    normalized_service = _normalize_service_id(service_id)

    services = _exec_with_timeout_retry(
        db,
        text(
            """
            SELECT CAST(id AS text) AS id, name
            FROM services
            WHERE (:service_id IS NULL OR id = CAST(:service_id AS uuid))
            """
        ),
        {"service_id": normalized_service},
    ).fetchall()

    weeks_set: set[str] = set()
    services_map: dict[str, dict[str, dict[str, int]]] = {}

    for srv in services:
        rows = _get_daily_metrics_cached(db, start_dt, end_dt, srv.id)
        anomalies = _get_anomalies_cached(
            rows,
            start_dt,
            end_dt,
            srv.id,
            list(ALL_METRICS),
            list(ALL_SEVERITIES),
            srv.name,
        )
        week_map: dict[str, dict[str, int]] = defaultdict(lambda: {"count": 0, "severity_score": 0})
        for anomaly in anomalies:
            week_label = datetime.fromisoformat(anomaly["date"]).strftime("%b W%V")
            weeks_set.add(week_label)
            score = {"medium": 1, "high": 2, "critical": 3}.get(anomaly["severity"], 0)
            week_map[week_label]["count"] += 1
            week_map[week_label]["severity_score"] = max(week_map[week_label]["severity_score"], score)
        services_map[srv.name] = dict(week_map)

    weeks = sorted(weeks_set)

    out_services = []
    for service_name, wk_map in services_map.items():
        cells = []
        for week in weeks:
            week_data = wk_map.get(week, {"count": 0, "severity_score": 0})
            count = week_data["count"]
            score = week_data["severity_score"]
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
    normalized_service = _normalize_service_id(service_id)
    selected_metrics = _parse_csv_values(metrics, ALL_METRICS)
    selected_severities = _parse_csv_values(severity, ALL_SEVERITIES)
    start_dt, end_dt = _resolve_anomaly_range(db, start_date, end_date, selected_metrics)

    rows = _get_daily_metrics_cached(db, start_dt, end_dt, normalized_service)
    anomalies = _get_anomalies_cached(
        rows,
        start_dt,
        end_dt,
        normalized_service,
        selected_metrics,
        selected_severities,
        _service_name(db, normalized_service),
    )

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
                "churn_rate_overflow": i.get("churn_rate_overflow", False),
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
    start_dt, end_dt = _resolve_anomaly_range(db, start_date, end_date, list(ALL_METRICS))
    normalized_service = _normalize_service_id(service_id)

    rows = _get_daily_metrics_cached(db, start_dt, end_dt, normalized_service)
    anomalies = _get_anomalies_cached(
        rows,
        start_dt,
        end_dt,
        normalized_service,
        list(ALL_METRICS),
        list(ALL_SEVERITIES),
        _service_name(db, normalized_service),
    )

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
def anomalies_run_detection(
    body: RunDetectionBody,
    db: Session = Depends(get_db),
    _admin = Depends(require_admin),
):
    started_at = datetime.now(timezone.utc)
    request_id = str(uuid.uuid4())
    _rt_log(
        "run_detection.start request_id=%s service_id=%s metrics=%s severities=%s start_date=%s end_date=%s",
        request_id,
        body.service_id or "all",
        body.metrics,
        body.severity,
        body.start_date,
        body.end_date,
    )

    try:
        def _on_progress(step: str) -> None:
            _rt_log("run_detection.progress request_id=%s %s", request_id, step)

        result = _run_detection_core(
            db,
            start_date=body.start_date,
            end_date=body.end_date,
            service_id=body.service_id,
            metrics=body.metrics,
            severity=body.severity,
            progress_callback=_on_progress,
        )
        run_completed_at = datetime.now(timezone.utc)
        took_ms = int((run_completed_at - started_at).total_seconds() * 1000)
        _rt_log(
            "run_detection.done request_id=%s anomalies=%s critical=%s high=%s medium=%s took_ms=%s",
            request_id,
            result["total_anomalies"],
            result["critical"],
            result["high"],
            result["medium"],
            took_ms,
        )

        return {
            "detection_run_id": request_id,
            "total_anomalies": result["total_anomalies"],
            "critical": result["critical"],
            "high": result["high"],
            "medium": result["medium"],
            "run_completed_at": run_completed_at.isoformat(),
        }
    except Exception:
        failed_at = datetime.now(timezone.utc)
        took_ms = int((failed_at - started_at).total_seconds() * 1000)
        _rt_log("run_detection.failed request_id=%s took_ms=%s", request_id, took_ms)
        logger.exception("anomalies.run_detection.failed exception request_id=%s", request_id)
        raise


@router.post("/run-detection/start")
def anomalies_run_detection_start(
    body: RunDetectionBody,
    _admin = Depends(require_admin),
):
    with _job_start_lock:
        active = _find_running_job()
        if active:
            return {"job_id": active["job_id"], "status": "running", "message": "A detection job is already running."}

        job_id = str(uuid.uuid4())
        job = {
            "job_id": job_id,
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
            "logs": [{"ts": datetime.now(timezone.utc).isoformat(), "message": "Detection job queued"}],
            "result": None,
            "error": None,
            "request": {
                "start_date": body.start_date,
                "end_date": body.end_date,
                "service_id": body.service_id,
                "metrics": body.metrics,
                "severity": body.severity,
            },
        }
        _save_job(job)

        t = threading.Thread(target=_run_detection_job, args=(job_id,), daemon=True)
        t.start()
        return {"job_id": job_id, "status": "running"}


@router.get("/run-detection/{job_id}/status")
def anomalies_run_detection_status(job_id: str):
    job = _load_job(job_id)
    if not job:
        return {"status": "not_found", "message": "Detection job not found."}
    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "started_at": job["started_at"],
        "completed_at": job["completed_at"],
        "logs": job["logs"],
        "result": job["result"],
        "error": job["error"],
    }
