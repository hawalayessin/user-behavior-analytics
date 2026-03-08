import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Unsubscription(Base):
    """
    Unsubscription / churn events.
    was_in_trial can be calculated: days_since_subscription <= trial_duration_days.
    """

    __tablename__ = "unsubscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
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
    unsubscription_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    churn_type: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="VOLUNTARY, TECHNICAL",
    )
    churn_reason: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    days_since_subscription: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
        comment="Days between subscription_start_date and unsubscription_datetime",
    )
    last_billing_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("billing_events.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Relationships — lazy="select" : chargé UNIQUEMENT si accédé explicitement
    subscription: Mapped["Subscription"] = relationship(
        "Subscription", back_populates="unsubscription", lazy="select"
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="unsubscriptions", lazy="select"
    )
    service: Mapped["Service"] = relationship(
        "Service", back_populates="unsubscriptions", lazy="select"
    )
    last_billing_event: Mapped["BillingEvent | None"] = relationship(
        "BillingEvent", lazy="select"
    )

    __table_args__ = (
        Index("ix_unsubscriptions_user_id", "user_id"),
        Index("ix_unsubscriptions_service_id", "service_id"),
        Index("ix_unsubscriptions_churn_type", "churn_type"),
        Index("ix_unsubscriptions_datetime", "unsubscription_datetime"),
        {"comment": "Unsubscription / churn tracking"},
    )

    def __repr__(self) -> str:
        return f"<Unsubscription(id={self.id}, churn_type={self.churn_type})>"