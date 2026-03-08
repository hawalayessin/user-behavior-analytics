import uuid
from datetime import datetime

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base



class Service(Base):
 

    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False,
        comment="Horoscope, Météo, Actualités, etc."
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    service_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("service_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # ── Relationships ──
    service_type: Mapped["ServiceType"] = relationship(
        "ServiceType", back_populates="services", lazy="joined"
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription", back_populates="service", lazy="selectin"
    )
    campaigns: Mapped[list["Campaign"]] = relationship(
        "Campaign", back_populates="service", lazy="selectin"
    )
    billing_events: Mapped[list["BillingEvent"]] = relationship(
        "BillingEvent", back_populates="service", lazy="selectin"
    )
    unsubscriptions: Mapped[list["Unsubscription"]] = relationship(
        "Unsubscription", back_populates="service", lazy="selectin"
    )
    sms_events: Mapped[list["SmsEvent"]] = relationship(
        "SmsEvent", back_populates="service", lazy="selectin"
    )
    user_activities: Mapped[list["UserActivity"]] = relationship(
        "UserActivity", back_populates="service", lazy="selectin"
    )
    cohorts: Mapped[list["Cohort"]] = relationship(
        "Cohort", back_populates="service", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_services_name", "name"),
        Index("ix_services_service_type_id", "service_type_id"),
        Index("ix_services_is_active", "is_active"),
        {
            "comment": "Service catalog - price and billing are in service_types"
        },
    )

    def __repr__(self) -> str:
        return f"<Service(id={self.id}, name={self.name})>"