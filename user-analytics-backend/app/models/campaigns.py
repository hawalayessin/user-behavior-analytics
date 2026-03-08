import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Text, Integer, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base



class Campaign(Base):
   

    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="SET NULL"),
        nullable=True,
        comment="NULL if multi-service campaign",
    )
    send_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    target_size: Mapped[int] = mapped_column(Integer, nullable=False)
    cost: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    campaign_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="acquisition, retention, reactivation, promotion",
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="draft, scheduled, sent, completed",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # ── Relationships ──
    service: Mapped["Service | None"] = relationship(
        "Service", back_populates="campaigns", lazy="joined"
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription", back_populates="campaign", lazy="selectin"
    )
    sms_events: Mapped[list["SmsEvent"]] = relationship(
        "SmsEvent", back_populates="campaign", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_campaigns_send_datetime", "send_datetime"),
        Index("ix_campaigns_status", "status"),
        Index("ix_campaigns_campaign_type", "campaign_type"),
        Index("ix_campaigns_service_id", "service_id"),
        {"comment": "SMS marketing campaigns"},
    )

    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, name={self.name}, status={self.status})>"