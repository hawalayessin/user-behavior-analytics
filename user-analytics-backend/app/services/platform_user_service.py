from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.platform_users import PlatformUser
from app.schemas.platform_user_schemas import PlatformUserCreate, PlatformUserUpdate

# ── Constants ────────────────────────────────────────────────────────────────

VALID_ROLES = {"admin", "analyst", "viewer"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_or_404(db: Session, user_id: UUID) -> PlatformUser:
    """Fetch a PlatformUser by ID or raise 404."""
    user = db.query(PlatformUser).filter(PlatformUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def _guard_self(user_id: UUID, current_user_id: UUID, action: str) -> None:
    """Raise 403 if the admin tries to modify/delete themselves."""
    if user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Admin cannot {action} their own account",
        )


# ── Service functions ─────────────────────────────────────────────────────────

def get_all_users(
    db: Session,
    skip: int,
    limit: int,
    search: str | None,
    role: str | None,
    is_active: bool | None,
) -> dict:
    """Return paginated list of platform users with optional filters."""
    query = db.query(PlatformUser)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                PlatformUser.full_name.ilike(pattern),
                PlatformUser.email.ilike(pattern),
            )
        )
    if role:
        query = query.filter(PlatformUser.role == role)

    if is_active is not None:
        query = query.filter(PlatformUser.is_active == is_active)

    total = query.count()
    users = query.order_by(PlatformUser.created_at.desc()).offset(skip).limit(limit).all()

    return {"items": users, "total": total}


def get_user_by_id(db: Session, user_id: UUID) -> PlatformUser:
    """Return a single platform user or raise 404."""
    return _get_or_404(db, user_id)


def create_user(db: Session, data: PlatformUserCreate) -> PlatformUser:
    """Create a new platform user, raise 400 if email already registered."""
    existing = db.query(PlatformUser).filter(PlatformUser.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = PlatformUser(
        email=data.email,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
        role=data.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(
    db: Session,
    user_id: UUID,
    data: PlatformUserUpdate,
) -> PlatformUser:
    """Update name, email and/or role of a platform user."""
    user = _get_or_404(db, user_id)

    if data.email and data.email != user.email:
        conflict = (
            db.query(PlatformUser)
            .filter(PlatformUser.email == data.email, PlatformUser.id != user_id)
            .first()
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        user.email = data.email

    if data.full_name is not None:
        user.full_name = data.full_name

    if data.role is not None:
        user.role = data.role

    db.commit()
    db.refresh(user)
    return user


def update_user_status(
    db: Session,
    user_id: UUID,
    is_active: bool,
    current_user_id: UUID,
) -> PlatformUser:
    """Toggle active/inactive status — admin cannot deactivate themselves."""
    _guard_self(user_id, current_user_id, "deactivate")
    user = _get_or_404(db, user_id)
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def update_user_role(
    db: Session,
    user_id: UUID,
    role: str,
    current_user_id: UUID,
) -> PlatformUser:
    """Change user role — admin cannot change their own role."""
    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
        )
    _guard_self(user_id, current_user_id, "change the role of")
    user = _get_or_404(db, user_id)
    user.role = role
    db.commit()
    db.refresh(user)
    return user


def delete_user(
    db: Session,
    user_id: UUID,
    current_user_id: UUID,
) -> None:
    """Permanently delete a platform user — admin cannot delete themselves."""
    _guard_self(user_id, current_user_id, "delete")
    user = _get_or_404(db, user_id)
    db.delete(user)
    db.commit()
