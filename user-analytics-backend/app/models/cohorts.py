import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, Integer, Numeric, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base



class Cohort(Base):
    """Pre-calculated retention metrics for performance."""

    __tablename__ = "cohorts"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    cohort_date: Mapped[date] = mapped_column(Date, nullable=False)
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
    )
    total_users: Mapped[int] = mapped_column(Integer, nullable=False)
    retention_d7: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    retention_d14: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    retention_d30: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # ── Relationships ──
    service: Mapped["Service"] = relationship(
        "Service", back_populates="cohorts", lazy="joined"
    )

    __table_args__ = (
        UniqueConstraint("cohort_date", "service_id", name="idx_cohort_unique"),
        Index("ix_cohorts_cohort_date", "cohort_date"),
        {"comment": "Pre-calculated retention metrics for performance"},
    )

    def __repr__(self) -> str:
        return f"<Cohort(id={self.id}, date={self.cohort_date}, users={self.total_users})>"