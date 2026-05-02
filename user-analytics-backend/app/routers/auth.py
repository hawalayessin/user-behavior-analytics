from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
import secrets
import os
import shutil
from typing import Final

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.platform_user_invites import PlatformUserInvite
from app.models.platform_users import PlatformUser
from app.schemas.auth import (
    InviteUserRequest,
    LoginRequest,
    RegisterRequest,
    RegisterInviteRequest,
    ProfileUpdateRequest,
    TokenResponse,
    UserResponse,
    ForgotPasswordRequest,
    VerifyResetTokenRequest,
    ResetPasswordRequest,
    TokenValidationResponse,
    MessageResponse,
)
from app.utils.email import send_password_reset_email, send_invite_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ─── POST /auth/register ──────────────────────────────────
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Registration is invite-only. Please use the invitation link.",
    )


# ─── GET /auth/me ───────────────────────────────────────────
@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_profile(current_user: PlatformUser = Depends(get_current_user)):
    return current_user


# ─── PATCH /auth/profile ────────────────────────────────────
@router.patch(
    "/profile",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def update_profile(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(get_current_user),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name

    if payload.new_password:
        if not payload.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required to set a new password.",
            )
        if not verify_password(payload.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )
        current_user.password_hash = hash_password(payload.new_password)

    db.commit()
    db.refresh(current_user)
    return current_user


AVATAR_DIR: Final[str] = os.path.join(
    os.path.dirname(__file__), "..", "..", "uploads", "avatars"
)
ALLOWED_CONTENT_TYPES: Final[set[str]] = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
    "image/gif",
}
ALLOWED_EXTS: Final[set[str]] = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _resolve_avatar_extension(filename: str, content_type: str) -> str:
    ext = os.path.splitext(filename or "")[1].lower()
    if ext in ALLOWED_EXTS:
        return ext
    if content_type in ("image/jpeg", "image/jpg"):
        return ".jpg"
    if content_type == "image/png":
        return ".png"
    if content_type == "image/webp":
        return ".webp"
    if content_type == "image/gif":
        return ".gif"
    return ".png"


# ─── POST /auth/profile/avatar ─────────────────────────────
@router.post(
    "/profile/avatar",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Please upload an image.",
        )

    os.makedirs(AVATAR_DIR, exist_ok=True)
    ext = _resolve_avatar_extension(file.filename, file.content_type or "")
    filename = f"{current_user.id}{ext}"
    safe_name = os.path.basename(filename)
    file_path = os.path.join(AVATAR_DIR, safe_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    current_user.avatar_url = f"/static/avatars/{safe_name}"
    db.commit()
    db.refresh(current_user)
    return current_user


# ─── DELETE /auth/profile/avatar ───────────────────────────
@router.delete(
    "/profile/avatar",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def delete_avatar(
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(get_current_user),
):
    if current_user.avatar_url:
        filename = os.path.basename(current_user.avatar_url)
        file_path = os.path.join(AVATAR_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    current_user.avatar_url = None
    db.commit()
    db.refresh(current_user)
    return current_user


# ─── POST /auth/invite ─────────────────────────────────────
@router.post(
    "/invite",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def invite_user(
    payload: InviteUserRequest,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_admin),
):
    existing = db.query(PlatformUser).filter(PlatformUser.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà.",
        )

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    invite = (
        db.query(PlatformUserInvite)
        .filter(PlatformUserInvite.email == payload.email)
        .first()
    )

    if invite:
        invite.token = token
        invite.expires_at = expires_at
        invite.invited_by = current_user.id
        invite.used_at = None
        invite.role = "analyst"
    else:
        invite = PlatformUserInvite(
            email=payload.email,
            role="analyst",
            token=token,
            invited_by=current_user.id,
            expires_at=expires_at,
        )
        db.add(invite)

    db.commit()

    invite_link = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/register?token={token}"
    if not send_invite_email(payload.email, invite_link):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send invitation email.",
        )

    return MessageResponse(message="Invitation sent.")


# ─── POST /auth/register-invite ────────────────────────────
@router.post(
    "/register-invite",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_invite(payload: RegisterInviteRequest, db: Session = Depends(get_db)):
    invite = (
        db.query(PlatformUserInvite)
        .filter(
            PlatformUserInvite.token == payload.token,
            PlatformUserInvite.used_at.is_(None),
        )
        .first()
    )

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation invalide ou déjà utilisée.",
        )

    if datetime.now(timezone.utc) > invite.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation expirée.",
        )

    existing = db.query(PlatformUser).filter(PlatformUser.email == invite.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà.",
        )

    new_user = PlatformUser(
        email=invite.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=invite.role,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    invite.used_at = datetime.now(timezone.utc)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ─── POST /auth/login ─────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    # 1️⃣ Chercher user
    user = (
        db.query(PlatformUser)
        .filter(PlatformUser.email == payload.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2️⃣ Vérifier password
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3️⃣ Vérifier actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé.",
        )

    # 4️⃣ update last login
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    # 5️⃣ JWT
    token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        role=user.role,
        full_name=user.full_name,
    )


# ─── POST /auth/forgot-password ──────────────────────────────────
@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Generate a reset token and send it via email.
    Always returns success message even if email doesn't exist (security).
    """
    # Search for user by email
    user = db.query(PlatformUser).filter(PlatformUser.email == payload.email).first()

    if user:
        # Generate secure token
        reset_token = secrets.token_urlsafe(32)
        reset_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        # Store token in database
        user.reset_token = reset_token
        user.reset_token_expires_at = reset_expires_at
        db.commit()

        # Send email (non-blocking in production, but sync for now)
        send_password_reset_email(payload.email, reset_token)

    # Always return same message (don't reveal if email exists)
    return MessageResponse(message="Si cet email existe, un code a été envoyé.")


# ─── POST /auth/verify-reset-token ───────────────────────────────
@router.post(
    "/verify-reset-token",
    response_model=TokenValidationResponse,
    status_code=status.HTTP_200_OK,
)
def verify_reset_token(payload: VerifyResetTokenRequest, db: Session = Depends(get_db)):
    """
    Verify that a reset token is valid and not expired.
    """
    # Find user with this token
    user = (
        db.query(PlatformUser)
        .filter(PlatformUser.reset_token == payload.token)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code de réinitialisation invalide.",
        )

    # Check if token is expired
    if user.reset_token_expires_at is None or datetime.now(timezone.utc) > user.reset_token_expires_at:
        # Clear expired token
        user.reset_token = None
        user.reset_token_expires_at = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code de réinitialisation expiré.",
        )

    return TokenValidationResponse(valid=True)


# ─── POST /auth/reset-password ───────────────────────────────────
@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password using a valid reset token.
    """
    # Find user with this token
    user = (
        db.query(PlatformUser)
        .filter(PlatformUser.reset_token == payload.token)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code de réinitialisation invalide.",
        )

    # Check if token is expired
    if user.reset_token_expires_at is None or datetime.now(timezone.utc) > user.reset_token_expires_at:
        # Clear expired token
        user.reset_token = None
        user.reset_token_expires_at = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code de réinitialisation expiré.",
        )

    # Update password
    user.password_hash = hash_password(payload.new_password)
    user.reset_token = None  # Invalidate token after use
    user.reset_token_expires_at = None
    db.commit()

    return MessageResponse(message="Mot de passe modifié avec succès.")
