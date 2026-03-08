import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Subscription(Base):

    __tablename__ = "subscriptions"

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
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True,
        comment="NULL = organic acquisition",
    )
    subscription_start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        comment="Single start date instead of trial_start/trial_end",
    )
    subscription_end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="NULL = still active",
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="trial, active, cancelled, expired",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # ── Relationships — lazy="select" : chargé UNIQUEMENT si accédé explicitement
    user: Mapped["User"] = relationship(
        "User", back_populates="subscriptions", lazy="select"
    )
    service: Mapped["Service"] = relationship(
        "Service", back_populates="subscriptions", lazy="select"
    )
    campaign: Mapped["Campaign | None"] = relationship(
        "Campaign", back_populates="subscriptions", lazy="select"
    )
    billing_events: Mapped[list["BillingEvent"]] = relationship(
        "BillingEvent", back_populates="subscription", lazy="select"
    )
    unsubscription: Mapped["Unsubscription | None"] = relationship(
        "Unsubscription", back_populates="subscription", uselist=False, lazy="select"
    )

    __table_args__ = (
        Index("ix_subscriptions_user_id", "user_id"),
        Index("ix_subscriptions_service_id", "service_id"),
        Index("ix_subscriptions_status", "status"),
        Index("ix_subscriptions_start_date", "subscription_start_date"),
        Index("ix_subscriptions_campaign_id", "campaign_id"),
        Index("idx_user_service", "user_id", "service_id"),
        {"comment": "User subscriptions to services"},
    )

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user={self.user_id}, status={self.status})>"