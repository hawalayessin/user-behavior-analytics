from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any, Literal

import joblib
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, classification_report, roc_auc_score
from sklearn.model_selection import train_test_split


RiskCategory = Literal["Low", "Medium", "High"]


@dataclass(frozen=True)
class ChurnPredictionResult:
    df: pd.DataFrame
    distribution: dict[str, int]


class ChurnPredictor:
    """
    Logistic Regression based churn predictor.

    Notes:
    - Training dataset is built from subscriptions table (subscription-level granularity).
    - Active scoring is status-driven (active/trial).
      This avoids empty predictions when source end dates are inconsistent.
    """

    def __init__(
        self,
        *,
        model_path: str | None = None,
        metrics_path: str | None = None,
        query_timeout_ms: int | None = None,
        random_state: int = 42,
    ):
        self.feature_names = [
            "days_since_last_activity",
            "nb_activities_7d",
            "nb_activities_30d",
            "billing_failures_30d",
            "days_since_first_charge",
            "is_trial_churn",
            "avg_retention_d7",
            "service_billing_frequency",
            "days_to_first_unsub",
        ]

        models_dir = Path(__file__).resolve().parent
        self.model_path = Path(model_path or models_dir / "churn_model.joblib")
        self.metrics_path = Path(metrics_path or models_dir / "churn_metrics.joblib")

        self.model = LogisticRegression(
            class_weight="balanced",
            random_state=random_state,
            max_iter=2000,
        )
        # Training/scoring feature SQL can be expensive on large datasets.
        # Allow a higher per-request timeout than the DB default.
        self.query_timeout_ms = int(
            query_timeout_ms
            if query_timeout_ms is not None
            else os.getenv("CHURN_SQL_TIMEOUT_MS", "120000")
        )

    def _feature_profile_from_df(self, df: pd.DataFrame) -> dict[str, dict[str, float]]:
        profile: dict[str, dict[str, float]] = {}
        for feature in self.feature_names:
            if feature not in df.columns:
                continue
            s = pd.to_numeric(df[feature], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
            if s.empty:
                profile[feature] = {
                    "mean": 0.0,
                    "std": 0.0,
                    "p10": 0.0,
                    "p50": 0.0,
                    "p90": 0.0,
                }
                continue
            profile[feature] = {
                "mean": float(s.mean()),
                "std": float(s.std(ddof=0)),
                "p10": float(s.quantile(0.10)),
                "p50": float(s.quantile(0.50)),
                "p90": float(s.quantile(0.90)),
            }
        return profile

    def _calibration_summary(self, y_true: pd.Series, y_proba: np.ndarray, bins: int = 10) -> dict[str, Any]:
        if len(y_true) == 0:
            return {"brier_score": None, "ece": None, "bins": []}

        y_true_arr = np.asarray(y_true).astype(float)
        y_proba_arr = np.asarray(y_proba).astype(float)
        brier = float(brier_score_loss(y_true_arr, y_proba_arr))

        edges = np.linspace(0.0, 1.0, bins + 1)
        total = len(y_true_arr)
        weighted_abs_gap = 0.0
        rows: list[dict[str, Any]] = []

        for i in range(bins):
            lo = float(edges[i])
            hi = float(edges[i + 1])
            mask = (y_proba_arr >= lo) & (y_proba_arr < hi if i < bins - 1 else y_proba_arr <= hi)
            count = int(mask.sum())
            if count == 0:
                rows.append(
                    {
                        "bin": f"{lo:.1f}-{hi:.1f}",
                        "count": 0,
                        "avg_pred": None,
                        "empirical_rate": None,
                        "abs_gap": None,
                    }
                )
                continue

            avg_pred = float(y_proba_arr[mask].mean())
            empirical = float(y_true_arr[mask].mean())
            abs_gap = abs(avg_pred - empirical)
            weighted_abs_gap += abs_gap * (count / total)
            rows.append(
                {
                    "bin": f"{lo:.1f}-{hi:.1f}",
                    "count": count,
                    "avg_pred": round(avg_pred, 4),
                    "empirical_rate": round(empirical, 4),
                    "abs_gap": round(abs_gap, 4),
                }
            )

        return {
            "brier_score": round(brier, 4),
            "ece": round(float(weighted_abs_gap), 4),
            "bins": rows,
        }

    def _compute_feature_drift(
        self,
        train_profile: dict[str, dict[str, float]],
        current_profile: dict[str, dict[str, float]],
    ) -> dict[str, Any]:
        features: list[dict[str, Any]] = []
        high_count = 0
        medium_count = 0

        for feature in self.feature_names:
            t = train_profile.get(feature) or {}
            c = current_profile.get(feature) or {}
            train_mean = float(t.get("mean") or 0.0)
            train_std = float(t.get("std") or 0.0)
            current_mean = float(c.get("mean") or 0.0)

            scale = train_std if train_std > 1e-9 else max(abs(train_mean), 1.0)
            z_shift = abs(current_mean - train_mean) / scale if scale > 0 else 0.0

            severity = "low"
            if z_shift >= 1.5:
                severity = "high"
                high_count += 1
            elif z_shift >= 1.0:
                severity = "medium"
                medium_count += 1

            features.append(
                {
                    "feature": feature,
                    "train_mean": round(train_mean, 4),
                    "current_mean": round(current_mean, 4),
                    "z_shift": round(float(z_shift), 4),
                    "severity": severity,
                }
            )

        features.sort(key=lambda x: x["z_shift"], reverse=True)
        avg_shift = float(np.mean([f["z_shift"] for f in features])) if features else 0.0

        return {
            "average_z_shift": round(avg_shift, 4),
            "high_drift_features": high_count,
            "medium_drift_features": medium_count,
            "features": features,
        }

    # -----------------------------
    # SQL Feature Engineering
    # -----------------------------
    def _read_sql_to_df(self, db_session: Session, query: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
        from sqlalchemy import text

        conn = db_session.connection()
        conn.exec_driver_sql(f"SET statement_timeout = {self.query_timeout_ms}")
        try:
            return pd.read_sql(text(query), conn, params=params or {})
        finally:
            conn.exec_driver_sql("SET statement_timeout = DEFAULT")

    def _base_features_sql(self) -> str:
        """
        Build a subscription-level dataset with features + churned label.
        Granularity: (user_id, service_id, subscription_id)
        """

        # IMPORTANT: Use subscription_end_date as reference ("ref_time") for churned subscriptions
        # to prevent label leakage from future activity/billing.
        return f"""
        WITH base AS (
          SELECT
            s.id AS subscription_id,
            s.user_id,
            s.service_id,
            s.subscription_start_date,
            s.subscription_end_date,
            s.status,
            COALESCE(s.subscription_end_date, NOW()) AS ref_time,
            st.billing_frequency_days,
            st.trial_duration_days,
            COALESCE(co.retention_d7, 0)::float AS avg_retention_d7,
            u.unsubscription_datetime,
            u.churn_type,
            u.churn_reason,
            u.days_since_subscription,
            CASE
              WHEN LOWER(COALESCE(s.status, '')) IN ('cancelled', 'expired') THEN 1
              ELSE 0
            END AS churned
          FROM subscriptions s
          JOIN services sv ON sv.id = s.service_id
          JOIN service_types st ON st.id = sv.service_type_id
          LEFT JOIN cohorts co
            ON co.service_id = s.service_id
           AND co.cohort_date = date_trunc('month', s.subscription_start_date)::date
          LEFT JOIN unsubscriptions u ON u.subscription_id = s.id
          WHERE s.status IN ('trial', 'active', 'cancelled', 'expired')
        )
        SELECT
          b.user_id,
          b.service_id,
          b.subscription_id,
          -- days_since_last_activity
          COALESCE(
            EXTRACT(DAY FROM (b.ref_time - last_activity.last_activity_datetime))::int,
            999
          ) AS days_since_last_activity,
          COALESCE(act7.nb_activities_7d, 0)::int AS nb_activities_7d,
          COALESCE(act30.nb_activities_30d, 0)::int AS nb_activities_30d,
          COALESCE(bfail30.billing_failures_30d, 0)::int AS billing_failures_30d,
          COALESCE(
            EXTRACT(DAY FROM (b.ref_time - first_charge.first_charge_datetime))::int,
            999
          ) AS days_since_first_charge,
          -- is_trial_churn: churn during trial
          CASE
            WHEN b.unsubscription_datetime IS NOT NULL
             AND COALESCE(b.days_since_subscription, EXTRACT(DAY FROM (b.unsubscription_datetime - b.subscription_start_date))::int)
                 <= b.trial_duration_days
            THEN 1 ELSE 0
          END AS is_trial_churn,
          COALESCE(b.avg_retention_d7, 0)::float AS avg_retention_d7,
          b.billing_frequency_days::float AS service_billing_frequency,
          -- days_to_first_unsub: time-to-churn for churned users, else a large sentinel
          CASE
            WHEN b.unsubscription_datetime IS NOT NULL
            THEN COALESCE(b.days_since_subscription, EXTRACT(DAY FROM (b.unsubscription_datetime - b.subscription_start_date))::int)
            ELSE 999
          END AS days_to_first_unsub,
          COALESCE(b.churned, 0)::int AS churned
        FROM base b
        LEFT JOIN LATERAL (
          SELECT MAX(ua.activity_datetime) AS last_activity_datetime
          FROM user_activities ua
          WHERE ua.user_id = b.user_id
            AND ua.service_id = b.service_id
            AND ua.activity_datetime <= b.ref_time
        ) last_activity ON TRUE
        LEFT JOIN LATERAL (
          SELECT COUNT(*) AS nb_activities_7d
          FROM user_activities ua
          WHERE ua.user_id = b.user_id
            AND ua.service_id = b.service_id
            AND ua.activity_datetime >= b.ref_time - INTERVAL '7 days'
            AND ua.activity_datetime <= b.ref_time
        ) act7 ON TRUE
        LEFT JOIN LATERAL (
          SELECT COUNT(*) AS nb_activities_30d
          FROM user_activities ua
          WHERE ua.user_id = b.user_id
            AND ua.service_id = b.service_id
            AND ua.activity_datetime >= b.ref_time - INTERVAL '30 days'
            AND ua.activity_datetime <= b.ref_time
        ) act30 ON TRUE
        LEFT JOIN LATERAL (
          SELECT COUNT(*) AS billing_failures_30d
          FROM billing_events be
          WHERE be.subscription_id = b.subscription_id
            AND be.status = 'FAILED'
            AND be.event_datetime >= b.ref_time - INTERVAL '30 days'
            AND be.event_datetime <= b.ref_time
        ) bfail30 ON TRUE
        LEFT JOIN LATERAL (
          SELECT MIN(be.event_datetime) AS first_charge_datetime
          FROM billing_events be
          WHERE be.subscription_id = b.subscription_id
            AND be.is_first_charge = TRUE
            AND be.status = 'SUCCESS'
            AND be.event_datetime <= b.ref_time
        ) first_charge ON TRUE
        """

    def _active_scoring_features_sql(
        self,
        service_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> str:
        """
        Build subscription-level dataset for active scoring.
        Granularity: (subscription_id)
        Includes user phone + service name for UI top lists.
        """
        where_clauses = ["LOWER(COALESCE(s.status, '')) IN ('active', 'trial')"]
        params = {}
        if service_id:
            where_clauses.append("s.service_id = CAST(:service_id AS uuid)")
            params["service_id"] = service_id
        if start_date:
            where_clauses.append("s.subscription_start_date >= :start_date")
            params["start_date"] = start_date
        if end_date:
            where_clauses.append("s.subscription_start_date <= :end_date")
            params["end_date"] = end_date

        where_str = " AND ".join(where_clauses)

        return f"""
        WITH base AS (
          SELECT
            s.id AS subscription_id,
            s.user_id,
            s.service_id,
            s.subscription_start_date,
            s.subscription_end_date,
            s.status,
            COALESCE(s.subscription_end_date, NOW()) AS ref_time,
            st.billing_frequency_days,
            st.trial_duration_days,
            COALESCE(co.retention_d7, 0)::float AS avg_retention_d7,
            u.unsubscription_datetime,
            u.days_since_subscription,
            u.churn_type,
            u.churn_reason,
            us.phone_number,
            sv.name AS service_name
          FROM subscriptions s
          JOIN services sv ON sv.id = s.service_id
          JOIN service_types st ON st.id = sv.service_type_id
          JOIN users us ON us.id = s.user_id
          LEFT JOIN cohorts co
            ON co.service_id = s.service_id
           AND co.cohort_date = date_trunc('month', s.subscription_start_date)::date
          LEFT JOIN unsubscriptions u ON u.subscription_id = s.id
          WHERE {where_str}
        )
        SELECT
          b.user_id,
          b.service_id,
          b.subscription_id,
          b.phone_number,
          b.service_name,
          COALESCE(
            EXTRACT(DAY FROM (b.ref_time - last_activity.last_activity_datetime))::int,
            999
          ) AS days_since_last_activity,
          COALESCE(act7.nb_activities_7d, 0)::int AS nb_activities_7d,
          COALESCE(act30.nb_activities_30d, 0)::int AS nb_activities_30d,
          COALESCE(bfail30.billing_failures_30d, 0)::int AS billing_failures_30d,
          COALESCE(
            EXTRACT(DAY FROM (b.ref_time - first_charge.first_charge_datetime))::int,
            999
          ) AS days_since_first_charge,
          CASE
            WHEN b.unsubscription_datetime IS NOT NULL
             AND COALESCE(b.days_since_subscription, EXTRACT(DAY FROM (b.unsubscription_datetime - b.subscription_start_date))::int)
                 <= b.trial_duration_days
            THEN 1 ELSE 0
          END AS is_trial_churn,
          COALESCE(b.avg_retention_d7, 0)::float AS avg_retention_d7,
          b.billing_frequency_days::float AS service_billing_frequency
          ,
          CASE
            WHEN b.unsubscription_datetime IS NOT NULL
            THEN COALESCE(b.days_since_subscription, EXTRACT(DAY FROM (b.unsubscription_datetime - b.subscription_start_date))::int)
            ELSE 999
          END AS days_to_first_unsub
        FROM base b
        LEFT JOIN LATERAL (
          SELECT MAX(ua.activity_datetime) AS last_activity_datetime
          FROM user_activities ua
          WHERE ua.user_id = b.user_id
            AND ua.service_id = b.service_id
            AND ua.activity_datetime <= b.ref_time
        ) last_activity ON TRUE
        LEFT JOIN LATERAL (
          SELECT COUNT(*) AS nb_activities_7d
          FROM user_activities ua
          WHERE ua.user_id = b.user_id
            AND ua.service_id = b.service_id
            AND ua.activity_datetime >= b.ref_time - INTERVAL '7 days'
            AND ua.activity_datetime <= b.ref_time
        ) act7 ON TRUE
        LEFT JOIN LATERAL (
          SELECT COUNT(*) AS nb_activities_30d
          FROM user_activities ua
          WHERE ua.user_id = b.user_id
            AND ua.service_id = b.service_id
            AND ua.activity_datetime >= b.ref_time - INTERVAL '30 days'
            AND ua.activity_datetime <= b.ref_time
        ) act30 ON TRUE
        LEFT JOIN LATERAL (
          SELECT COUNT(*) AS billing_failures_30d
          FROM billing_events be
          WHERE be.subscription_id = b.subscription_id
            AND be.status = 'FAILED'
            AND be.event_datetime >= b.ref_time - INTERVAL '30 days'
            AND be.event_datetime <= b.ref_time
        ) bfail30 ON TRUE
        LEFT JOIN LATERAL (
          SELECT MIN(be.event_datetime) AS first_charge_datetime
          FROM billing_events be
          WHERE be.subscription_id = b.subscription_id
            AND be.is_first_charge = TRUE
            AND be.status = 'SUCCESS'
            AND be.event_datetime <= b.ref_time
        ) first_charge ON TRUE
        """, params

    # -----------------------------
    # Train / Predict
    # -----------------------------
    def generate_training_dataset(self, db_session: Session) -> tuple[pd.DataFrame, pd.Series]:
        df = self._read_sql_to_df(db_session, self._base_features_sql())
        if df.empty:
            raise ValueError("Not enough data to build training dataset.")

        # Safety: coerce and sanitize features.
        X = df[self.feature_names].copy()
        X = X.replace([np.inf, -np.inf], np.nan).fillna(0)

        y = df["churned"].astype(int)
        return X, y

    def train(self, db_session: Session) -> dict[str, Any]:
        X, y = self.generate_training_dataset(db_session)
        n_positive = int((y == 1).sum())
        n_negative = int((y == 0).sum())
        label_distribution = {"1": n_positive, "0": n_negative}

        if y.nunique() < 2:
            warning = (
                "Training skipped: dataset contains a single class only. "
                "Need both churned (1) and non-churned (0) samples to train LogisticRegression."
            )
            metrics = {
                "trained_at": pd.Timestamp.utcnow().isoformat(),
                "roc_auc": None,
                "churn_rate": float(y.mean()) if len(y) else 0.0,
                "accuracy": 1.0,
                "report": {
                    "warning": warning,
                    "class_distribution": {
                        "n_positive": n_positive,
                        "n_negative": n_negative,
                    },
                    "label_distribution": label_distribution,
                },
                "coefficients": {},
                "n_samples": int(len(y)),
                "n_positive": n_positive,
                "n_negative": n_negative,
                "warning": warning,
                "governance": {
                  "protocol": {
                    "version": "churn-governance-v1",
                    "evaluation_split": "stratified train_test_split(test_size=0.2, random_state=42)",
                    "default_decision_threshold": 0.4,
                    "recalibration_cadence_days": 30,
                  },
                  "calibration": {
                    "brier_score": None,
                    "ece": None,
                    "bins": [],
                  },
                  "feature_profile_train": self._feature_profile_from_df(X),
                },
            }
            self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(metrics, self.metrics_path)
            return metrics

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() > 1 else None
        )

        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)[:, 1]

        roc_auc = None
        if y_test.nunique() > 1:
            roc_auc = float(roc_auc_score(y_test, y_proba))

        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        churn_rate = float(y.mean()) if len(y) else 0.0

        coeffs = {}
        try:
            # LogisticRegression exposes coef_ directly.
            coeffs = dict(zip(self.feature_names, self.model.coef_[0].astype(float)))
        except Exception:
            coeffs = {}

        metrics = {
            "trained_at": pd.Timestamp.utcnow().isoformat(),
            "roc_auc": roc_auc,
            "churn_rate": churn_rate,
            "accuracy": float(report.get("accuracy", 0.0)),
          "report": {
            **report,
            "label_distribution": label_distribution,
          },
            "coefficients": coeffs,
            "n_samples": int(len(df := pd.concat([X, y.rename("churned")], axis=1))),
          "n_positive": n_positive,
          "n_negative": n_negative,
            "warning": None,
            "governance": {
              "protocol": {
                "version": "churn-governance-v1",
                "evaluation_split": "stratified train_test_split(test_size=0.2, random_state=42)",
                "default_decision_threshold": 0.4,
                "recalibration_cadence_days": 30,
              },
              "calibration": self._calibration_summary(y_test, y_proba),
              "feature_profile_train": self._feature_profile_from_df(X_train),
            },
        }

        # Persist model + metrics.
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(metrics, self.metrics_path)

        return metrics

    def load(self) -> bool:
        if not self.model_path.exists():
            return False
        self.model = joblib.load(self.model_path)
        return True

    def load_metrics(self) -> dict[str, Any] | None:
        if not self.metrics_path.exists():
            return None
        return joblib.load(self.metrics_path)

    def _risk_category(self, churn_risk: float) -> RiskCategory:
        # Probability bins.
        if churn_risk < 0.3:
            return "Low"
        if churn_risk < 0.6:
            return "Medium"
        return "High"

    def predict_active_subscriptions(
        self,
        db_session: Session,
        *,
        threshold: float = 0.4,
        store_predictions: bool = False,
        service_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> ChurnPredictionResult:
        if not self.load():
            raise FileNotFoundError("Model not trained yet. Call /ml/churn/train first.")

        query, params = self._active_scoring_features_sql(
            service_id=service_id, start_date=start_date, end_date=end_date
        )
        df = self._read_sql_to_df(db_session, query, params=params)
        if df.empty:
            return ChurnPredictionResult(df=pd.DataFrame(), distribution={"Low": 0, "Medium": 0, "High": 0})

        X = df[self.feature_names].copy()
        X = X.replace([np.inf, -np.inf], np.nan).fillna(0)

        churn_risk_scores = self.model.predict_proba(X)[:, 1]
        churn_risk_scores = np.clip(churn_risk_scores.astype(float), 0.0, 1.0)

        df = df.copy()
        df["churn_risk"] = churn_risk_scores
        df["predicted_churn"] = (df["churn_risk"] >= threshold).astype(int)
        df["risk_category"] = df["churn_risk"].apply(self._risk_category)

        distribution = (
            df["risk_category"]
            .value_counts()
            .to_dict()
        )
        for k in ("Low", "Medium", "High"):
            distribution.setdefault(k, 0)

        if store_predictions:
            # Store only for API debugging / jury export.
            df_store = df[
                [
                    "subscription_id",
                    "user_id",
                    "service_id",
                    "churn_risk",
                    "risk_category",
                    "predicted_churn",
                ]
            ].copy()
            # Make sure UUIDs don't break type inference in to_sql.
            for col in ["subscription_id", "user_id", "service_id"]:
                if col in df_store.columns:
                    df_store[col] = df_store[col].astype(str)

            df_store["threshold"] = float(threshold)
            df_store.to_sql("churn_predictions", db_session.bind, if_exists="replace", index=False)

        return ChurnPredictionResult(df=df, distribution=distribution)

    def governance_report(self, db_session: Session, *, recalibration_cadence_days: int = 30) -> dict[str, Any]:
        metrics = self.load_metrics()
        if metrics is None:
            raise FileNotFoundError("Model metrics not found. Train the model first.")

        gov = metrics.get("governance") or {}
        train_profile = gov.get("feature_profile_train") or {}
        calibration = gov.get("calibration") or {}
        protocol = gov.get("protocol") or {}

        if not self.load():
            raise FileNotFoundError("Model not trained yet. Call /ml/churn/train first.")

        current = self.predict_active_subscriptions(db_session, threshold=0.4, store_predictions=False)
        current_df = current.df
        current_profile = self._feature_profile_from_df(current_df) if not current_df.empty else {}

        drift = self._compute_feature_drift(train_profile, current_profile) if train_profile else {
            "average_z_shift": 0.0,
            "high_drift_features": 0,
            "medium_drift_features": 0,
            "features": [],
        }

        trained_at_raw = metrics.get("trained_at")
        trained_at = pd.to_datetime(trained_at_raw, utc=True) if trained_at_raw else pd.Timestamp.now(tz="UTC")
        now = pd.Timestamp.now(tz="UTC")
        days_since_training = int(max((now - trained_at).days, 0))

        cadence = int(protocol.get("recalibration_cadence_days") or recalibration_cadence_days)
        calibration_due = days_since_training >= cadence
        retrain_due = calibration_due or int(drift.get("high_drift_features") or 0) >= 2

        if retrain_due:
            status = "retrain_required"
        elif int(drift.get("medium_drift_features") or 0) >= 2:
            status = "watch"
        else:
            status = "stable"

        return {
            "status": status,
            "trained_at": trained_at.isoformat(),
            "evaluated_at": now.isoformat(),
            "days_since_training": days_since_training,
            "calibration_due": calibration_due,
            "retrain_due": retrain_due,
            "protocol": {
                "version": protocol.get("version") or "churn-governance-v1",
                "evaluation_split": protocol.get("evaluation_split") or "stratified train_test_split(test_size=0.2, random_state=42)",
                "default_decision_threshold": float(protocol.get("default_decision_threshold") or 0.4),
                "recalibration_cadence_days": cadence,
            },
            "calibration": {
                "brier_score": calibration.get("brier_score"),
                "ece": calibration.get("ece"),
                "bins": calibration.get("bins") or [],
            },
            "drift": drift,
            "scored_population": int(current_df["user_id"].nunique()) if not current_df.empty and "user_id" in current_df.columns else 0,
            "recommendations": [
                "Review high-drift features and upstream data contracts before retraining.",
                "Recalibrate threshold policy if ECE exceeds 0.08 or Brier score degrades over two cycles.",
                "Run monthly stable evaluation protocol and archive governance snapshots for auditability.",
            ],
        }

