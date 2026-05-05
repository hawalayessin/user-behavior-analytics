from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

import uuid

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.platform_users import PlatformUser

# FastAPI lit le token depuis le header : Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ─── Dépendance de base ───────────────────────────────────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> PlatformUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Décoder le JWT
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 2. Récupérer l'user en DB
    try:
        user_uuid = uuid.UUID(str(user_id))
    except (ValueError, TypeError):
        raise credentials_exception

    user = db.query(PlatformUser).filter(PlatformUser.id == user_uuid).first()
    if user is None:
        raise credentials_exception

    # 3. Vérifier que le compte est toujours actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is disabled.",
        )

    return user


# ─── Guard admin ──────────────────────────────────────────────────────────────
def require_admin(
    current_user: PlatformUser = Depends(get_current_user),
) -> PlatformUser:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only.",
        )
    return current_user