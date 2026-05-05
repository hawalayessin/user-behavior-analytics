import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """
    Core user table.
    phone_number is the main business identifier.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    phone_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active",
        comment="active, inactive (payed or not)"
    )
    last_activity_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    channel: Mapped[str | None] = mapped_column(
        String(20), nullable=True,
        comment="Activation channel from source (USSD/WEB)"
    )

    # ── Relationships — lazy="select" : chargé UNIQUEMENT si accédé explicitement
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription", back_populates="user", lazy="select"
    )
    billing_events: Mapped[list["BillingEvent"]] = relationship(
        "BillingEvent", back_populates="user", lazy="select"
    )
    unsubscriptions: Mapped[list["Unsubscription"]] = relationship(
        "Unsubscription", back_populates="user", lazy="select"
    )
    sms_events: Mapped[list["SmsEvent"]] = relationship(
        "SmsEvent", back_populates="user", lazy="select"
    )
    user_activities: Mapped[list["UserActivity"]] = relationship(
        "UserActivity", back_populates="user", lazy="select"
    )

    __table_args__ = (
        Index("ix_users_created_at", "created_at"),
        Index("ix_users_last_activity_at", "last_activity_at"),
        {"comment": "Core user table. phone_number is the main business identifier"},
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, phone={self.phone_number}, status={self.status})>"