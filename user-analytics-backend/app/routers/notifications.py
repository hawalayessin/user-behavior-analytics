from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.anomaly_notification_read import AnomalyNotificationRead
from app.models.platform_users import PlatformUser
from ml_models.anomalies import (
    ALL_METRICS,
    _get_anomalies_cached,
    _get_daily_metrics_cached,
    _resolve_anomaly_range,
    _service_name,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

_NEGATIVE_SPIKE_METRICS = {"churn_rate"}
_READ_TABLE_CHECKED = False


def _ensure_read_table(db: Session) -> bool:
    global _READ_TABLE_CHECKED
    if _READ_TABLE_CHECKED:
        return True

    bind = db.get_bind()
    try:
        if not inspect(bind).has_table(AnomalyNotificationRead.__tablename__):
            AnomalyNotificationRead.__table__.create(bind=bind, checkfirst=True)
        _READ_TABLE_CHECKED = True
        return True
    except Exception:
        db.rollback()
        return False


def _stable_anomaly_id(anomaly: dict[str, Any]) -> str:
    raw = "|".join(
        [
            str(anomaly.get("service_name") or "all"),
            str(anomaly.get("metric") or ""),
            str(anomaly.get("detection_date") or anomaly.get("date") or ""),
            str(anomaly.get("z_score") or ""),
            str(anomaly.get("observed_value") or ""),
            str(anomaly.get("expected_value") or ""),
        ]
    )
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"digmaco-anomaly-notification:{raw}"))


def _business_direction(metric: str, z_score: float) -> str:
    is_spike = z_score >= 0
    if metric in _NEGATIVE_SPIKE_METRICS:
        return "negative" if is_spike else "positive"
    return "positive" if is_spike else "negative"


def _message(metric: str, direction: str, z_score: float) -> str:
    trend = "Hausse" if z_score >= 0 else "Baisse"
    metric_label = metric.replace("_", " ")
    if metric == "churn_rate" and direction == "negative":
        return "Hausse anormale du churn detectee"
    if metric == "dau" and direction == "negative":
        return "Baisse anormale de l'activite detectee"
    if metric == "revenue" and direction == "positive":
        return "Hausse anormale des revenus detectee"
    if metric == "renewals" and direction == "positive":
        return "Hausse anormale des renouvellements detectee"
    return f"{trend} anormale de {metric_label} detectee"


def _interpretation(notification: dict[str, Any]) -> str:
    metric = notification["metric_name"]
    direction = notification["direction"]
    severity = notification["severity"]
    current = notification["current_value"]
    expected = notification["expected_value"]

    if direction == "negative":
        return (
            f"Signal {severity.lower()} defavorable sur {metric}: la valeur observee "
            f"({current}) s'ecarte fortement de l'attendu ({expected}). Une verification "
            "des segments, services et evenements recents est recommandee."
        )
    return (
        f"Signal {severity.lower()} favorable sur {metric}: la valeur observee "
        f"({current}) depasse l'attendu ({expected}). Analysez les campagnes, canaux "
        "ou cohortes qui expliquent cette progression."
    )


def _serialize_notification(anomaly: dict[str, Any], read_ids: set[str]) -> dict[str, Any]:
    metric = str(anomaly["metric"])
    z_score = float(anomaly.get("z_score") or 0)
    anomaly_id = _stable_anomaly_id(anomaly)
    direction = _business_direction(metric, z_score)
    detected_at = anomaly.get("detection_date") or anomaly.get("date")
    payload = {
        "id": anomaly_id,
        "metric_name": metric,
        "severity": str(anomaly["severity"]).upper(),
        "direction": direction,
        "z_score": z_score,
        "current_value": float(anomaly.get("observed_value") or 0),
        "expected_value": float(anomaly.get("expected_value") or 0),
        "detected_at": detected_at,
        "message": _message(metric, direction, z_score),
        "read": anomaly_id in read_ids,
        "service_name": anomaly.get("service_name"),
    }
    payload["interpretation"] = _interpretation(payload)
    return payload


@router.get("/anomalies")
def anomaly_notifications(
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(get_current_user),
) -> list[dict[str, Any]]:
    start_dt, end_dt = _resolve_anomaly_range(db, None, None, list(ALL_METRICS))
    rows = _get_daily_metrics_cached(db, start_dt, end_dt, None)
    anomalies = _get_anomalies_cached(
        rows,
        start_dt,
        end_dt,
        None,
        list(ALL_METRICS),
        ["critical", "high"],
        _service_name(db, None),
    )
    recent = anomalies[:20]
    ids = [_stable_anomaly_id(item) for item in recent]
    reads = []
    if ids and _ensure_read_table(db):
        try:
            reads = (
                db.query(AnomalyNotificationRead.anomaly_id)
                .filter(
                    AnomalyNotificationRead.user_id == current_user.id,
                    AnomalyNotificationRead.anomaly_id.in_(ids),
                )
                .all()
            )
        except ProgrammingError:
            db.rollback()
    read_ids = {row.anomaly_id for row in reads}
    return [_serialize_notification(item, read_ids) for item in recent]


@router.patch("/anomalies/{anomaly_id}/read")
def mark_anomaly_notification_read(
    anomaly_id: str,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(get_current_user),
) -> dict[str, Any]:
    if not _ensure_read_table(db):
        return {"id": anomaly_id, "read": False, "read_at": None}

    existing = (
        db.query(AnomalyNotificationRead)
        .filter(
            AnomalyNotificationRead.user_id == current_user.id,
            AnomalyNotificationRead.anomaly_id == anomaly_id,
        )
        .first()
    )
    if existing:
        return {"id": anomaly_id, "read": True, "read_at": existing.read_at.isoformat()}

    read = AnomalyNotificationRead(
        user_id=current_user.id,
        anomaly_id=anomaly_id,
        read_at=datetime.now(timezone.utc),
    )
    db.add(read)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        read = (
            db.query(AnomalyNotificationRead)
            .filter(
                AnomalyNotificationRead.user_id == current_user.id,
                AnomalyNotificationRead.anomaly_id == anomaly_id,
            )
            .first()
        )
    except ProgrammingError:
        db.rollback()
        return {"id": anomaly_id, "read": False, "read_at": None}
    return {
        "id": anomaly_id,
        "read": True,
        "read_at": read.read_at.isoformat() if read else None,
    }
