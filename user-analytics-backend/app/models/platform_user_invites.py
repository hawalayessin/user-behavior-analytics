import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class PlatformUserInvite(Base):
    __tablename__ = "platform_user_invites"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="analyst")
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    invited_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("platform_users.id"), nullable=False
    )
    invited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_platform_user_invites_email", "email"),
        Index("ix_platform_user_invites_token", "token"),
        Index("ix_platform_user_invites_used_at", "used_at"),
        {"comment": "Pending platform user invites"},
    )

    def __repr__(self) -> str:
        return f"<PlatformUserInvite(id={self.id}, email={self.email}, role={self.role})>"
