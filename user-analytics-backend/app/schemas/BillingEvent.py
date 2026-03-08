from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class BillingEventBase(BaseModel):
    subscription_id: UUID
    user_id: UUID
    service_id: UUID
    event_datetime: datetime
    status: str = Field(..., max_length=20)
    failure_reason: str | None = Field(None, max_length=255)
    retry_count: int = Field(default=0, ge=0)
    is_first_charge: bool = False


class BillingEventCreate(BillingEventBase):
    pass


class BillingEventUpdate(BaseModel):
    status: str | None = Field(None, max_length=20)
    failure_reason: str | None = Field(None, max_length=255)
    retry_count: int | None = Field(None, ge=0)


class BillingEventRead(BillingEventBase):
    id: UUID

    model_config = {"from_attributes": True}