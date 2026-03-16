import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class ImportLog(Base):
    __tablename__ = "import_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    admin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("platform_users.id", ondelete="SET NULL"),
        nullable=True,
    )

    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)  # csv | sql
    target_table: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mode: Mapped[str | None] = mapped_column(String(20), nullable=True)  # append | replace

    rows_inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success | partial | failed
    error_details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_import_logs_imported_at", "imported_at"),
        Index("ix_import_logs_admin_id", "admin_id"),
    )

