from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class ServiceTypeBase(BaseModel):
    name: str = Field(..., max_length=50)
    billing_frequency_days: int = Field(..., gt=0)
    price: Decimal = Field(..., max_digits=10, decimal_places=2)
    trial_duration_days: int = Field(default=3, ge=0)
    is_active: bool = True


class ServiceTypeCreate(ServiceTypeBase):
    pass


class ServiceTypeUpdate(BaseModel):
    name: str | None = Field(None, max_length=50)
    billing_frequency_days: int | None = Field(None, gt=0)
    price: Decimal | None = Field(None, max_digits=10, decimal_places=2)
    trial_duration_days: int | None = Field(None, ge=0)
    is_active: bool | None = None


class ServiceTypeRead(ServiceTypeBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}