from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


class CohortBase(BaseModel):
    cohort_date: date
    service_id: UUID
    total_users: int = Field(..., ge=0)
    retention_d7: Decimal | None = Field(None, max_digits=5, decimal_places=2)
    retention_d14: Decimal | None = Field(None, max_digits=5, decimal_places=2)
    retention_d30: Decimal | None = Field(None, max_digits=5, decimal_places=2)
    calculated_at: datetime


class CohortCreate(CohortBase):
    pass


class CohortUpdate(BaseModel):
    total_users: int | None = Field(None, ge=0)
    retention_d7: Decimal | None = Field(None, max_digits=5, decimal_places=2)
    retention_d14: Decimal | None = Field(None, max_digits=5, decimal_places=2)
    retention_d30: Decimal | None = Field(None, max_digits=5, decimal_places=2)
    calculated_at: datetime | None = None


class CohortRead(CohortBase):
    id: UUID

    model_config = {"from_attributes": True}