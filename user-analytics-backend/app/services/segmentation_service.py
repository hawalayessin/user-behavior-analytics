"""Segmentation service layer with bounded payloads and real model training."""

from __future__ import annotations

import random
import time
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories import segmentation_repo
from app.utils.temporal import get_data_bounds
from ml_models.segmentation_trainer import run_segmentation_training


_DASHBOARD_CACHE_TTL_SECONDS = 30
_MAX_CLUSTER_POINTS = 600

_kpis_cache: dict[tuple[str, str, str], tuple[float, dict]] = {}
_clusters_cache: dict[tuple[str, str, str], tuple[float, dict]] = {}
_profiles_cache: dict[tuple[str, str, str], tuple[float, dict]] = {}


def _to_window(
    db: Session,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
) -> tuple[datetime, datetime]:
    if start_date and end_date:
        return start_date, end_date
    # Default "All time" for segmentation should cover the full DB range.
    return get_data_bounds(db, source="subscription")


def _cache_key(
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    service_id: Optional[str],
) -> tuple[str, str, str]:
    return (
        start_date.isoformat() if start_date else "",
        end_date.isoformat() if end_date else "",
        service_id or "",
    )


def _sample_cluster_points(segments: list[dict], max_points: int = _MAX_CLUSTER_POINTS) -> list[dict]:
    if len(segments) <= max_points:
        return segments

    by_segment: dict[str, list[dict]] = {}
    for row in segments:
        segment = str(row.get("segment") or "Unknown")
        by_segment.setdefault(segment, []).append(row)

    sampled: list[dict] = []
    total = len(segments)
    for rows in by_segment.values():
        quota = max(1, int(round((len(rows) / total) * max_points)))
        if len(rows) <= quota:
            sampled.extend(rows)
        else:
            sampled.extend(random.sample(rows, quota))

    if len(sampled) > max_points:
        sampled = random.sample(sampled, max_points)

    return sampled


def _distribution_from_segments(segments: list[dict]) -> list[dict]:
    ordered = ["Regular Loyals", "Power Users", "Occasional Users", "Trial Only"]
    total = len(segments)
    counts: dict[str, int] = {name: 0 for name in ordered}

    for row in segments:
        segment = str(row.get("segment") or "")
        counts[segment] = counts.get(segment, 0) + 1

    if total == 0:
        return [{"name": name, "percentage": 0.0, "count": 0} for name in ordered]

    return [
        {
            "name": name,
            "percentage": round((counts.get(name, 0) / total) * 100, 1),
            "count": counts.get(name, 0),
        }
        for name in ordered
    ]


def get_segmentation_kpis(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    service_id: Optional[str] = None,
) -> dict:
    start_date, end_date = _to_window(db, start_date, end_date)
    key = _cache_key(start_date, end_date, service_id)

    now = time.monotonic()
    cached = _kpis_cache.get(key)
    if cached and now - cached[0] < _DASHBOARD_CACHE_TTL_SECONDS:
        return cached[1]

    data = segmentation_repo.get_segment_kpis(db, start_date, end_date, service_id)
    _kpis_cache[key] = (now, data)
    return data


def get_segmentation_clusters(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    service_id: Optional[str] = None,
) -> dict:
    start_date, end_date = _to_window(db, start_date, end_date)
    key = _cache_key(start_date, end_date, service_id)

    now = time.monotonic()
    cached = _clusters_cache.get(key)
    if cached and now - cached[0] < _DASHBOARD_CACHE_TTL_SECONDS:
        return cached[1]

    segments = segmentation_repo.get_user_segments(db, start_date, end_date, service_id)
    sampled_segments = _sample_cluster_points(segments)
    distribution_payload = segmentation_repo.get_segment_distribution(db, start_date, end_date, service_id)

    clusters = [
        {
            "x": float(row.get("x") or 0.0),
            "y": float(row.get("y") or 0.0),
            "segment": str(row.get("segment") or "Trial Only"),
        }
        for row in sampled_segments
    ]

    payload = {
        "clusters": clusters,
        "distribution": distribution_payload.get("distribution", _distribution_from_segments(segments)),
    }
    _clusters_cache[key] = (now, payload)
    return payload


def get_segmentation_profiles(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    service_id: Optional[str] = None,
) -> dict:
    start_date, end_date = _to_window(db, start_date, end_date)
    key = _cache_key(start_date, end_date, service_id)

    now = time.monotonic()
    cached = _profiles_cache.get(key)
    if cached and now - cached[0] < _DASHBOARD_CACHE_TTL_SECONDS:
        return cached[1]

    data = segmentation_repo.get_segment_profiles(db, start_date, end_date, service_id)
    _profiles_cache[key] = (now, data)
    return data


def train_segmentation_model(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    service_id: Optional[str] = None,
) -> dict:
    """Train segmentation model using launcher in ml_models."""
    logs: list[dict] = []

    def log_step(message: str, **extra: object) -> None:
        payload = {"ts": datetime.utcnow().isoformat(), "message": message}
        payload.update(extra)
        logs.append(payload)

    t_global = time.monotonic()
    _kpis_cache.clear()
    _clusters_cache.clear()
    _profiles_cache.clear()

    result = run_segmentation_training(
        db,
        start_date=start_date,
        end_date=end_date,
        service_id=service_id,
        progress_callback=log_step,
    )

    total_sec = round(time.monotonic() - t_global, 2)
    log_step("Training completed", total_elapsed_sec=total_sec)
    meta = result.get("meta") or {}
    return {
        "status": result.get("status", "error"),
        "message": result.get("message", "Segmentation training finished"),
        "logs": logs,
        "summary": {
            "users": meta.get("users"),
            "window_start": meta.get("window_start"),
            "window_end": meta.get("window_end"),
            "total_elapsed_sec": total_sec,
        },
    }


def clear_caches() -> None:
    _kpis_cache.clear()
    _clusters_cache.clear()
    _profiles_cache.clear()
