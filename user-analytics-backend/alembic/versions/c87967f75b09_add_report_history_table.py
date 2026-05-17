"""add_report_history_table

Revision ID: c87967f75b09
Revises: 6c49d082ab7f
Create Date: 2026-05-16 10:42:37.891959

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c87967f75b09"
down_revision: Union[str, Sequence[str], None] = "6c49d082ab7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "report_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("report_type", sa.String(length=50), nullable=False),
        sa.Column("period_start", sa.String(length=20), nullable=True),
        sa.Column("period_end", sa.String(length=20), nullable=True),
        sa.Column("services_included", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("sections_included", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("distribution_format", sa.String(length=20), nullable=False),
        sa.Column("include_ai_insights", sa.Boolean(), nullable=True),
        sa.Column("include_recommendations", sa.Boolean(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("current_step", sa.String(length=200), nullable=True),
        sa.Column("current_step_num", sa.Integer(), nullable=True),
        sa.Column("total_steps", sa.Integer(), nullable=True),
        sa.Column("progress_pct", sa.Integer(), nullable=True),
        sa.Column("file_path", sa.Text(), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("file_size_kb", sa.Integer(), nullable=True),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("ai_insights_used", sa.Integer(), nullable=True),
        sa.Column("generation_time_sec", sa.Integer(), nullable=True),
        sa.Column("error_msg", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("report_history")
