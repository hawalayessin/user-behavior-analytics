import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base



class SmsEvent(Base):
    """SMS interaction logs."""

    __tablename__ = "sms_events"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True,
        comment="NULL = non-campaign SMS",
    )
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="SET NULL"),
        nullable=True,
    )
    event_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    event_type: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="DELIVERY_SUCCESS, DELIVERY_FAILURE",
    )
    message_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    direction: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="inbound, outbound - outbound price is 0.035 TND",
    )
    delivery_status: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )

    # ── Relationships ──
    user: Mapped["User"] = relationship(
        "User", back_populates="sms_events", lazy="joined"
    )
    campaign: Mapped["Campaign | None"] = relationship(
        "Campaign", back_populates="sms_events", lazy="joined"
    )
    service: Mapped["Service | None"] = relationship(
        "Service", back_populates="sms_events", lazy="joined"
    )

    __table_args__ = (
        Index("ix_sms_events_user_id", "user_id"),
        Index("ix_sms_events_campaign_id", "campaign_id"),
        Index("ix_sms_events_event_datetime", "event_datetime"),
        Index("ix_sms_events_event_type", "event_type"),
        Index("ix_sms_events_service_id", "service_id"),
        {"comment": "SMS interaction logs"},
    )

    def __repr__(self) -> str:
        return f"<SmsEvent(id={self.id}, type={self.event_type}, direction={self.direction})>"