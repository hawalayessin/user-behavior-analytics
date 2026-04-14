from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import secrets

from app.core.database import get_db
from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.platform_users import PlatformUser
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    ForgotPasswordRequest,
    VerifyResetTokenRequest,
    ResetPasswordRequest,
    TokenValidationResponse,
    MessageResponse,
)
from app.utils.email import send_password_reset_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ─── POST /auth/register ──────────────────────────────────
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):

    # 1️⃣ Vérifier doublon email
    existing = (
        db.query(PlatformUser)
        .filter(PlatformUser.email == payload.email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà.",
        )

    # 2️⃣ Créer utilisateur
    new_user = PlatformUser(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

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
