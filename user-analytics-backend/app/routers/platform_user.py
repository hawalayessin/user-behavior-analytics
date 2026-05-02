from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.platform_users import PlatformUser
from app.schemas.platform_user_schemas import (
    PlatformUserCreate,
    PlatformUserListResponse,
    PlatformUserResponse,
    PlatformUserUpdate,
    UpdateRoleRequest,
    UpdateStatusRequest,
)
from app.services import platform_user_service as service

router = APIRouter()


# ── GET /platform-users ───────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=PlatformUserListResponse,
    status_code=status.HTTP_200_OK,
)
def list_platform_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=500),  # ← 100 → 500
    search: str | None = Query(default=None),
    role: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    _: PlatformUser = Depends(require_admin),
) -> PlatformUserListResponse:
    """List all platform users with optional filters and pagination."""
    return service.get_all_users(db, skip, limit, search, role, is_active)


# ── GET /platform-users/{user_id} ─────────────────────────────────────────────

@router.get(
    "/{user_id}",
    response_model=PlatformUserResponse,
    status_code=status.HTTP_200_OK,
)
def get_platform_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    _: PlatformUser = Depends(require_admin),
) -> PlatformUserResponse:
    """Get a single platform user by ID."""
    return service.get_user_by_id(db, user_id)


# ── POST /platform-users ──────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=PlatformUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_platform_user(
    data: PlatformUserCreate,
    db: Session = Depends(get_db),
    _: PlatformUser = Depends(require_admin),
) -> PlatformUserResponse:
    """Create a new platform user account."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Direct account creation is disabled. Use invitations instead.",
    )


# ── PUT /platform-users/{user_id} ─────────────────────────────────────────────

@router.put(
    "/{user_id}",
    response_model=PlatformUserResponse,
    status_code=status.HTTP_200_OK,
)
def update_platform_user(
    user_id: UUID,
    data: PlatformUserUpdate,
    db: Session = Depends(get_db),
    _: PlatformUser = Depends(require_admin),
) -> PlatformUserResponse:
    """Update name, email and/or role of a platform user."""
    return service.update_user(db, user_id, data)


# ── PATCH /platform-users/{user_id}/status ────────────────────────────────────

@router.patch(
    "/{user_id}/status",
    status_code=status.HTTP_200_OK,
)
def update_user_status(
    user_id: UUID,
    body: UpdateStatusRequest,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_admin),
) -> dict:
    """Toggle active/inactive status of a platform user."""
    user = service.update_user_status(db, user_id, body.is_active, current_user.id)
    return {"message": "User status updated", "is_active": user.is_active}


# ── PATCH /platform-users/{user_id}/role ──────────────────────────────────────

@router.patch(
    "/{user_id}/role",
    status_code=status.HTTP_200_OK,
)
def update_user_role(
    user_id: UUID,
    body: UpdateRoleRequest,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_admin),
) -> dict:
    """Change role of a platform user (admin ↔ analyst)."""
    user = service.update_user_role(db, user_id, body.role, current_user.id)
    return {"message": "Role updated", "role": user.role}


# ── DELETE /platform-users/{user_id} ──────────────────────────────────────────

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
)
def delete_platform_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_admin),
) -> dict:
    """Permanently delete a platform user."""
    service.delete_user(db, user_id, current_user.id)
    return {"message": "User deleted successfully"}