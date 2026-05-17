"""Report history model.
Tracks all generated reports with status, file metadata and AI usage.
"""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql import func

from app.core.database import Base


class ReportHistory(Base):
    __tablename__ = "report_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # Report configuration
    report_type = Column(String(50), nullable=False)
    # Values: executive | churn | ai_segmentation | full
    period_start = Column(String(20), nullable=True)
    period_end = Column(String(20), nullable=True)
    services_included = Column(JSON, default=list, nullable=True)
    sections_included = Column(JSON, default=list, nullable=True)
    distribution_format = Column(String(20), default="pdf", nullable=False)
    # Values: pdf | xls

    # AI options
    include_ai_insights = Column(Boolean, default=True)
    include_recommendations = Column(Boolean, default=True)

    # Generation progress
    status = Column(String(20), default="pending", nullable=False)
    # Values: pending | generating | success | failed
    current_step = Column(String(200), nullable=True)
    current_step_num = Column(Integer, default=0)
    total_steps = Column(Integer, default=5)
    progress_pct = Column(Integer, default=0)

    # Output metadata
    file_path = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=True)
    file_size_kb = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)
    ai_insights_used = Column(Integer, default=0)
    generation_time_sec = Column(Integer, nullable=True)

    # Error tracking
    error_msg = Column(Text, nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(String(100), nullable=True)

