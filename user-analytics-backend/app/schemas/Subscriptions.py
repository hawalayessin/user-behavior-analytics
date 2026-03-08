from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class SubscriptionBase(BaseModel):
    user_id: UUID
    service_id: UUID
    campaign_id: UUID | None = None
    subscription_start_date: datetime
    subscription_end_date: datetime | None = None
    status: str = Field(..., max_length=20)


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    subscription_end_date: datetime | None = None
    status: str | None = Field(None, max_length=20)


class SubscriptionRead(SubscriptionBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}