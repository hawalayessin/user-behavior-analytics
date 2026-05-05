from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

import joblib
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from app.repositories import segmentation_repo
from app.utils.temporal import get_data_bounds


_MODEL_PATH = Path(__file__).resolve().parent / "segmentation_kmeans.joblib"


def _to_window(
    db: Session,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
) -> tuple[datetime, datetime]:
    if start_date and end_date:
        return start_date, end_date
    return get_data_bounds(db, source="subscription")


def run_segmentation_training(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    service_id: Optional[str] = None,
    progress_callback: Optional[Callable[..., None]] = None,
) -> dict:
    def log_step(message: str, **extra: object) -> None:
        if progress_callback:
            progress_callback(message, **extra)

    start_date, end_date = _to_window(db, start_date, end_date)
    log_step(
        "Training window resolved",
        window_start=start_date.isoformat(),
        window_end=end_date.isoformat(),
        service_id=service_id,
    )
    segments = segmentation_repo.get_user_segments(db, start_date, end_date, service_id)
    log_step("Feature extraction completed", users=len(segments))

    if len(segments) < 4:
        return {
            "status": "error",
            "message": f"Not enough data: {len(segments)} users",
        }

    feature_matrix = np.array(
        [[float(row.get("x") or 0.0), float(row.get("y") or 0.0)] for row in segments],
        dtype=float,
    )

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(feature_matrix)

    model = KMeans(n_clusters=4, random_state=42, n_init=10)
    labels = model.fit_predict(x_scaled)
    log_step("KMeans fit completed", n_clusters=4)

    cluster_revenue: dict[int, float] = {}
    cluster_count: dict[int, int] = {}
    for row, label in zip(segments, labels):
        cluster_revenue[label] = cluster_revenue.get(label, 0.0) + float(row.get("revenue") or 0.0)
        cluster_count[label] = cluster_count.get(label, 0) + 1

    mean_revenue = {
        cluster: (cluster_revenue[cluster] / max(cluster_count.get(cluster, 1), 1))
        for cluster in cluster_revenue
    }
    ordered_clusters = [c for c, _ in sorted(mean_revenue.items(), key=lambda item: item[1])]
    names_low_to_high = ["Trial Only", "Occasional Users", "Regular Loyals", "Power Users"]
    rank_map = {cluster: names_low_to_high[idx] for idx, cluster in enumerate(ordered_clusters)}

    _MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "scaler": scaler,
            "rank_map": rank_map,
            "trained_at": datetime.utcnow().isoformat(),
            "window": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "service_id": service_id,
            },
        },
        _MODEL_PATH,
    )
    log_step("Model artifact saved", path=str(_MODEL_PATH))

    return {
        "status": "success",
        "message": f"KMeans trained on {len(segments)} users",
        "meta": {
            "users": len(segments),
            "window_start": start_date.isoformat(),
            "window_end": end_date.isoformat(),
        },
    }
