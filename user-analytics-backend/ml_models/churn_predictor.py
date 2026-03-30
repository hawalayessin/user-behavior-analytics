from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import joblib
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
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
    - Active scoring uses subscription_end_date IS NULL.
    """

    def __init__(
        self,
        *,
        model_path: str | None = None,
        metrics_path: str | None = None,
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

    # -----------------------------
    # SQL Feature Engineering
    # -----------------------------
    def _read_sql_to_df(self, db_session: Session, query: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
        from sqlalchemy import text
        return pd.read_sql(text(query), db_session.bind, params=params or {})

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
              WHEN s.subscription_end_date IS NOT NULL THEN 1
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
        where_clauses = ["s.subscription_end_date IS NULL", "s.status IN ('active', 'trial')"]
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
            "report": report,
            "coefficients": coeffs,
            "n_samples": int(len(df := pd.concat([X, y.rename("churned")], axis=1))),
            "n_positive": int(int(y.sum())),
            "n_negative": int(int((y == 0).sum())),
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

