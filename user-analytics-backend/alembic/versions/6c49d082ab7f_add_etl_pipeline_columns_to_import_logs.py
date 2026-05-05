"""add_etl_pipeline_columns_to_import_logs

Revision ID: 6c49d082ab7f
Revises: feb49323daed
Create Date: 2026-05-04 11:19:17.399545
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6c49d082ab7f"
down_revision: Union[str, Sequence[str], None] = "feb49323daed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("import_logs", sa.Column("demo_users", sa.Integer(), nullable=True))
    op.add_column("import_logs", sa.Column("current_step", sa.String(length=100), nullable=True))
    op.add_column("import_logs", sa.Column("current_step_num", sa.Integer(), nullable=True))
    op.add_column("import_logs", sa.Column("total_steps", sa.Integer(), nullable=True))
    op.add_column("import_logs", sa.Column("progress_pct", sa.Integer(), nullable=True))
    op.add_column("import_logs", sa.Column("duration_sec", sa.Float(), nullable=True))
    op.add_column("import_logs", sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("import_logs", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))
    op.alter_column(
        "import_logs",
        "file_type",
        existing_type=sa.VARCHAR(length=10),
        type_=sa.String(length=20),
        existing_nullable=False,
    )
    op.create_index("ix_import_logs_started_at", "import_logs", ["started_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_import_logs_started_at", table_name="import_logs")
    op.alter_column(
        "import_logs",
        "file_type",
        existing_type=sa.String(length=20),
        type_=sa.VARCHAR(length=10),
        existing_nullable=False,
    )
    op.drop_column("import_logs", "completed_at")
    op.drop_column("import_logs", "started_at")
    op.drop_column("import_logs", "duration_sec")
    op.drop_column("import_logs", "progress_pct")
    op.drop_column("import_logs", "total_steps")
    op.drop_column("import_logs", "current_step_num")
    op.drop_column("import_logs", "current_step")
    op.drop_column("import_logs", "demo_users")
