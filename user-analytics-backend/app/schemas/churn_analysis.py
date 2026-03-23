from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


ChurnType = Literal["VOLUNTARY", "TECHNICAL"]


class ChurnKPIsResponse(BaseModel):
    global_churn_rate: float = Field(..., ge=0)
    avg_lifetime_days: float = Field(..., ge=0)
    first_bill_churn_rate: float = Field(..., ge=0)
    voluntary_pct: float = Field(..., ge=0, le=100)
    technical_pct: float = Field(..., ge=0, le=100)
    trial_churn_pct: float = Field(..., ge=0, le=100)
    paid_churn_pct: float = Field(..., ge=0, le=100)


class ChurnCurvePoint(BaseModel):
    month: str
    service_name: str
    churn_rate: float = Field(..., ge=0)
    retention_rate: float = Field(..., ge=0)
    new_subscriptions: int = Field(..., ge=0)


class TimeToChurnBucketRow(BaseModel):
    service_name: str
    churn_type: ChurnType
    bucket: str
    count: int = Field(..., ge=0)


class ChurnReasonRow(BaseModel):
    churn_type: ChurnType
    reason: str
    count: int = Field(..., ge=0)


class RiskSegmentRow(BaseModel):
    segment_id: str
    label: str
    description: str
    affected_users: int = Field(..., ge=0)
    top_services: list[str]

