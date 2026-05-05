from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from sklearn.preprocessing import RobustScaler


@dataclass
class SegmentationPreprocessor:
    feature_names: list[str]
    log_features: set[str]
    clip_low: dict[str, float]
    clip_high: dict[str, float]
    scaler: RobustScaler

    @classmethod
    def fit(
        cls,
        rows: Iterable[dict],
        feature_names: list[str],
        *,
        log_features: set[str] | None = None,
        low_q: float = 0.01,
        high_q: float = 0.99,
    ) -> tuple["SegmentationPreprocessor", np.ndarray]:
        log_features = log_features or set()
        x_raw = _rows_to_matrix(rows, feature_names)

        clip_low: dict[str, float] = {}
        clip_high: dict[str, float] = {}
        x_proc = np.array(x_raw, copy=True)
        for i, name in enumerate(feature_names):
            col = x_proc[:, i]
            lo = float(np.quantile(col, low_q))
            hi = float(np.quantile(col, high_q))
            if hi < lo:
                hi = lo
            clip_low[name] = lo
            clip_high[name] = hi
            x_proc[:, i] = np.clip(col, lo, hi)
            if name in log_features:
                x_proc[:, i] = np.log1p(np.clip(x_proc[:, i], a_min=0.0, a_max=None))

        scaler = RobustScaler()
        x_scaled = scaler.fit_transform(x_proc)
        return (
            cls(
                feature_names=feature_names,
                log_features=set(log_features),
                clip_low=clip_low,
                clip_high=clip_high,
                scaler=scaler,
            ),
            x_scaled,
        )

    def transform(self, rows: Iterable[dict]) -> np.ndarray:
        x_raw = _rows_to_matrix(rows, self.feature_names)
        x_proc = np.array(x_raw, copy=True)
        for i, name in enumerate(self.feature_names):
            lo = self.clip_low[name]
            hi = self.clip_high[name]
            x_proc[:, i] = np.clip(x_proc[:, i], lo, hi)
            if name in self.log_features:
                x_proc[:, i] = np.log1p(np.clip(x_proc[:, i], a_min=0.0, a_max=None))
        return self.scaler.transform(x_proc)


def _rows_to_matrix(rows: Iterable[dict], feature_names: list[str]) -> np.ndarray:
    data = []
    for row in rows:
        data.append([float(row.get(name) or 0.0) for name in feature_names])
    if not data:
        return np.zeros((0, len(feature_names)), dtype=float)
    return np.array(data, dtype=float)
