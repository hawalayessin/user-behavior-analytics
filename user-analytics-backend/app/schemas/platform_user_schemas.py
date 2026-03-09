from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ══════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: UUID
    role: str
    exp: datetime


# ══════════════════════════════════════════════════════════════
# CRUD SCHEMAS
# ══════════════════════════════════════════════════════════════

class PlatformUserBase(BaseModel):
    email: EmailStr
    full_name: str | None = Field(None, min_length=2, max_length=100)
    role: Literal["admin", "analyst", "viewer"] = "analyst"
    is_active: bool = True


class PlatformUserCreate(PlatformUserBase):
    password: str = Field(..., min_length=8)


class PlatformUserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(None, min_length=2, max_length=100)
    role: Literal["admin", "analyst", "viewer"] | None = None
    is_active: bool | None = None


class PlatformUserRead(PlatformUserBase):
    id: UUID
    created_at: datetime
    last_login_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# Alias utilisé dans le router platform_users
PlatformUserResponse = PlatformUserRead


class PlatformUserListResponse(BaseModel):
    items: list[PlatformUserResponse]
    total: int


# ══════════════════════════════════════════════════════════════
# STATUS / ROLE PATCH
# ══════════════════════════════════════════════════════════════

class UpdateStatusRequest(BaseModel):
    is_active: bool


class UpdateRoleRequest(BaseModel):
    role: Literal["admin", "analyst", "viewer"]
