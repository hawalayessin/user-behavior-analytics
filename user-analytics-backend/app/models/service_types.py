import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Integer, Numeric, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base



class ServiceType(Base):
  

    __tablename__ = "service_types"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False,
        comment="daily, weekly, monthly"
    )
    billing_frequency_days: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="1 for daily, 7 for weekly, 30 for monthly"
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False,
        comment="Price for this subscription type"
    )
    trial_duration_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3,
        comment="Free trial duration in days"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # ── Relationships ──
    services: Mapped[list["Service"]] = relationship(
        "Service", back_populates="service_type", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_service_types_is_active", "is_active"),
        {
            "comment": "Billing types with pricing - daily, weekly, monthly"
        },
    )

    def __repr__(self) -> str:
        return f"<ServiceType(id={self.id}, name={self.name}, price={self.price})>"