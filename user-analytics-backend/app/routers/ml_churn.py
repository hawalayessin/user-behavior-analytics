from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from ml_models.churn_predictor import ChurnPredictor

from app.schemas.ml_churn import (
    ChurnScoresResponse,
    ChurnTrainMetricsResponse,
)


router = APIRouter(prefix="/ml/churn", tags=["AI Churn Prediction"])


@router.post("/train", response_model=ChurnTrainMetricsResponse)
def train_churn_model(
    db: Session = Depends(get_db),
    _: Any = Depends(require_admin),
):
    predictor = ChurnPredictor()
    try:
        metrics = predictor.train(db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    # If roc_auc couldn't be computed (single class), keep roc_auc=None
    return metrics


@router.get("/metrics")
def get_churn_model_metrics():
    predictor = ChurnPredictor()
    metrics = predictor.load_metrics()
    if metrics is None:
        raise HTTPException(status_code=404, detail="Churn model not trained yet.")
    return metrics


@router.get("/scores", response_model=ChurnScoresResponse)
def get_churn_scores(
    db: Session = Depends(get_db),
    top: int = Query(default=10, ge=1, le=200),
    threshold: float = Query(default=0.4, ge=0.0, le=1.0),
    store: bool = Query(default=False, description="Store predictions into SQL table churn_predictions."),
):
    predictor = ChurnPredictor()

    try:
        result = predictor.predict_active_subscriptions(
            db,
            threshold=threshold,
            store_predictions=store,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    df = result.df
    if df.empty:
        now = datetime.now(timezone.utc).isoformat()
        return ChurnScoresResponse(
            generated_at=now,
            threshold=threshold,
            distribution=[
                {"risk_category": "Low", "count": 0},
                {"risk_category": "Medium", "count": 0},
                {"risk_category": "High", "count": 0},
            ],
            top_users=[],
            active_users_scored=0,
        )

    # Convert to user-level: one row per user, with max churn risk across subscriptions.
    df_sorted = df.sort_values(["user_id", "churn_risk"], ascending=[True, False])
    df_user = df_sorted.groupby("user_id").head(1).copy()
    df_user["user_id"] = df_user["user_id"].astype(str)

    distribution_dict = df_user["risk_category"].value_counts().to_dict()
    distribution = [
        {"risk_category": "Low", "count": int(distribution_dict.get("Low", 0))},
        {"risk_category": "Medium", "count": int(distribution_dict.get("Medium", 0))},
        {"risk_category": "High", "count": int(distribution_dict.get("High", 0))},
    ]

    # "Top risky users" should honor the selected risk threshold.
    top_df = (
        df_user[df_user["churn_risk"] >= threshold]
        .sort_values("churn_risk", ascending=False)
        .head(top)
    )

    top_users = [
        {
            "user_id": row.user_id,
            "phone_number": row.phone_number,
            "service_name": row.service_name,
            "churn_risk": float(row.churn_risk),
            "risk_category": row.risk_category,
            "predicted_churn": int(row.predicted_churn),
        }
        for _, row in top_df.iterrows()
    ]

    return ChurnScoresResponse(
        generated_at=datetime.now(timezone.utc).isoformat(),
        threshold=threshold,
        distribution=distribution,
        top_users=top_users,
        active_users_scored=int(df_user["user_id"].nunique()),
    )

