from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AnalystNoteCreate(BaseModel):
    service_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    metric: Optional[str] = Field(default=None, max_length=50)
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    content: str = Field(min_length=10)


class AnalystNoteUpdate(BaseModel):
    service_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    metric: Optional[str] = Field(default=None, max_length=50)
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    content: Optional[str] = Field(default=None, min_length=10)


class AnalystNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    analyst_id: UUID
    analyst_name: Optional[str] = None
    service_id: Optional[UUID] = None
    service_name: Optional[str] = None
    campaign_id: Optional[UUID] = None
    campaign_name: Optional[str] = None
    metric: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    content: str
    created_at: datetime
    updated_at: datetime
