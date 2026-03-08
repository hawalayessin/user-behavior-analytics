from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ───────────────── SUB SCHEMAS ─────────────────

class SubscriptionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_id: UUID
    status: str
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None


class UnsubscriptionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    churn_type: Optional[str] = None
    churn_reason: Optional[str] = None
    days_since_subscription: Optional[int] = None
    unsubscription_datetime: Optional[datetime] = None


# ───────────────── GET /users ─────────────────

class UserListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    phone: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    total_subscriptions: int = 0
    active_subscriptions: int = 0
    has_churned: bool = False


class UserListResponse(BaseModel):
    data: List[UserListItem]
    total: int
    page: int
    page_size: int


# ───────────────── GET /users/{id} ─────────────────

class UserDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    phone: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    subscriptions: List[SubscriptionItem] = []
    unsubscriptions: List[UnsubscriptionItem] = []


# ───────────────── STATS ─────────────────

class UserStatsResponse(BaseModel):
    total_users: int
    active_users: int
    churned_users: int
    new_users_last_30_days: int
    conversion_rate: float