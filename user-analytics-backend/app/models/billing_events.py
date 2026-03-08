import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base 



class BillingEvent(Base):
    """
    Billing events for subscriptions.
    Amount is calculated from service_types.price.
    """

    __tablename__ = "billing_events"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
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
    event_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="SUCCESS, FAILED",
    )
    failure_reason: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    retry_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    is_first_charge: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # ── Relationships ──
    subscription: Mapped["Subscription"] = relationship(
        "Subscription", back_populates="billing_events", lazy="joined"
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="billing_events", lazy="joined"
    )
    service: Mapped["Service"] = relationship(
        "Service", back_populates="billing_events", lazy="joined"
    )

    __table_args__ = (
        Index("ix_billing_events_subscription_id", "subscription_id"),
        Index("ix_billing_events_user_id", "user_id"),
        Index("ix_billing_events_event_datetime", "event_datetime"),
        Index("ix_billing_events_status", "status"),
        Index("ix_billing_events_is_first_charge", "is_first_charge"),
        Index("ix_billing_events_service_id", "service_id"),
        {
            "comment": "Billing events - amount derived from service_types.price"
        },
    )

    def __repr__(self) -> str:
        return f"<BillingEvent(id={self.id}, status={self.status})>"