import uuid
from datetime import date, datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class AnalystNote(Base):
    __tablename__ = "analyst_notes"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    analyst_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("platform_users.id", ondelete="CASCADE"), nullable=False
    )
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("services.id", ondelete="SET NULL"), nullable=True
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True
    )
    metric: Mapped[str | None] = mapped_column(String(50), nullable=True)
    period_start: Mapped[date | None] = mapped_column(nullable=True)
    period_end: Mapped[date | None] = mapped_column(nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_analyst_notes_analyst_id", "analyst_id"),
        Index("ix_analyst_notes_service_id", "service_id"),
        Index("ix_analyst_notes_campaign_id", "campaign_id"),
        Index("ix_analyst_notes_metric", "metric"),
        Index("ix_analyst_notes_period_start", "period_start"),
        Index("ix_analyst_notes_period_end", "period_end"),
        Index("ix_analyst_notes_created_at", "created_at"),
        {"comment": "Analyst contextual notes"},
    )

    def __repr__(self) -> str:
        return f"<AnalystNote(id={self.id}, analyst_id={self.analyst_id})>"
