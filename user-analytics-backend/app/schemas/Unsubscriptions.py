from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class UnsubscriptionBase(BaseModel):
    subscription_id: UUID
    user_id: UUID
    service_id: UUID
    unsubscription_datetime: datetime
    churn_type: str = Field(..., max_length=20)
    churn_reason: str | None = Field(None, max_length=255)
    days_since_subscription: int | None = None
    last_billing_event_id: UUID | None = None


class UnsubscriptionCreate(UnsubscriptionBase):
    pass


class UnsubscriptionUpdate(BaseModel):
    churn_reason: str | None = Field(None, max_length=255)
    days_since_subscription: int | None = None


class UnsubscriptionRead(UnsubscriptionBase):
    id: UUID

    model_config = {"from_attributes": True}