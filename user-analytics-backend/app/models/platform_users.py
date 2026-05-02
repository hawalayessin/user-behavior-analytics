import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base 


class PlatformUser(Base):
   

    __tablename__ = "platform_users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False,
        comment="Login email : manager@company.com",
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False,
        comment="bcrypt hash — jamais stocker en clair",
    )
    full_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String(512), nullable=True
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="analyst",
        comment="admin, analyst, viewer",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Dernière connexion au dashboard",
    )
    reset_token: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
        comment="Token de réinitialisation de mot de passe",
    )
    reset_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Expiration du token de réinitialisation",
    )

    __table_args__ = (
        Index("ix_platform_users_role", "role"),
        Index("ix_platform_users_is_active", "is_active"),
        {"comment": "Platform users for dashboard access"},
    )

    def __repr__(self) -> str:
        return f"<PlatformUser(id={self.id}, email={self.email}, role={self.role})>"