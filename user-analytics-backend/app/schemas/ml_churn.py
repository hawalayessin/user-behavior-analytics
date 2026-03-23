from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


RiskCategory = Literal["Low", "Medium", "High"]


class ChurnTrainMetricsResponse(BaseModel):
    trained_at: str
    roc_auc: Optional[float] = None
    accuracy: float = Field(..., ge=0, le=1)
    churn_rate: float = Field(..., ge=0, le=1)
    n_samples: int = Field(..., ge=0)
    n_positive: int = Field(..., ge=0)
    n_negative: int = Field(..., ge=0)
    report: dict[str, Any]
    coefficients: dict[str, float] = {}


class ChurnRiskDistributionItem(BaseModel):
    risk_category: RiskCategory
    count: int = Field(..., ge=0)


class ChurnTopUserItem(BaseModel):
    user_id: str
    phone_number: str
    service_name: str
    churn_risk: float = Field(..., ge=0, le=1)
    risk_category: RiskCategory
    predicted_churn: int = Field(..., ge=0, le=1)


class ChurnScoresResponse(BaseModel):
    generated_at: str
    threshold: float = Field(..., ge=0, le=1)
    distribution: list[ChurnRiskDistributionItem]
    top_users: list[ChurnTopUserItem]
    active_users_scored: int = Field(..., ge=0)

