from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class UserActivityBase(BaseModel):
    user_id: UUID
    service_id: UUID
    activity_datetime: datetime
    activity_type: str = Field(..., max_length=50)
    session_id: str | None = Field(None, max_length=100)


class UserActivityCreate(UserActivityBase):
    pass


class UserActivityRead(UserActivityBase):
    id: UUID

    model_config = {"from_attributes": True}