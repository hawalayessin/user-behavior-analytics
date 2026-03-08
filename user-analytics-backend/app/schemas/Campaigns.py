from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class CampaignBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    service_id: UUID | None = None
    send_datetime: datetime
    target_size: int = Field(..., ge=0)
    cost: Decimal | None = Field(None, max_digits=10, decimal_places=2)
    campaign_type: str = Field(..., max_length=50)
    status: str = Field(..., max_length=20)


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    service_id: UUID | None = None
    send_datetime: datetime | None = None
    target_size: int | None = Field(None, ge=0)
    cost: Decimal | None = Field(None, max_digits=10, decimal_places=2)
    campaign_type: str | None = Field(None, max_length=50)
    status: str | None = Field(None, max_length=20)


class CampaignRead(CampaignBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}