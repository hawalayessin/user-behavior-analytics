import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base



class UserActivity(Base):
    """Activity logging for DAU/WAU/MAU."""

    __tablename__ = "user_activities"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
    )
    activity_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    activity_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="service_usage, sms_received, etc.",
    )
    session_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    # ── Relationships ──
    user: Mapped["User"] = relationship(
        "User", back_populates="user_activities", lazy="joined"
    )
    service: Mapped["Service"] = relationship(
        "Service", back_populates="user_activities", lazy="joined"
    )

    __table_args__ = (
        Index("idx_user_activity_time", "user_id", "activity_datetime"),
        Index("ix_user_activities_datetime", "activity_datetime"),
        Index("ix_user_activities_type", "activity_type"),
        {"comment": "Activity logging for DAU/WAU/MAU"},
    )

    def __repr__(self) -> str:
        return f"<UserActivity(id={self.id}, type={self.activity_type})>"