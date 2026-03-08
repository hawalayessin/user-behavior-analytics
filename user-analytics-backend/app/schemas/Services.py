from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

from app.schemas.ServicesTypes import ServiceTypeRead


class ServiceBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None
    service_type_id: UUID
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = None
    service_type_id: UUID | None = None
    is_active: bool | None = None


class ServiceRead(ServiceBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ServiceReadWithType(ServiceRead):
    """Service avec les détails du service_type imbriqué."""
    service_type: ServiceTypeRead