from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class SmsEventBase(BaseModel):
    user_id: UUID
    campaign_id: UUID | None = None
    service_id: UUID | None = None
    event_datetime: datetime
    event_type: str = Field(..., max_length=30)
    message_content: str | None = None
    direction: str = Field(..., max_length=20)
    delivery_status: str | None = Field(None, max_length=50)


class SmsEventCreate(SmsEventBase):
    pass


class SmsEventUpdate(BaseModel):
    delivery_status: str | None = Field(None, max_length=50)


class SmsEventRead(SmsEventBase):
    id: UUID

    model_config = {"from_attributes": True}