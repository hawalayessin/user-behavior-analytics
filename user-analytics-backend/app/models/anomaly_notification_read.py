import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class AnomalyNotificationRead(Base):
    __tablename__ = "anomaly_notification_reads"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("platform_users.id", ondelete="CASCADE"), nullable=False
    )
    anomaly_id: Mapped[str] = mapped_column(String(64), nullable=False)
    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "anomaly_id", name="uq_anomaly_notification_reads_user_anomaly"),
        Index("ix_anomaly_notification_reads_user_id", "user_id"),
        Index("ix_anomaly_notification_reads_anomaly_id", "anomaly_id"),
    )
