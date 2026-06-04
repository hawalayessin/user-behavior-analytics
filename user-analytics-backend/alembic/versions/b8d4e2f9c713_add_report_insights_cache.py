"""add report insights cache

Revision ID: b8d4e2f9c713
Revises: a7c9d2e4f601
Create Date: 2026-05-23
"""

from typing import Sequence, Union

from alembic import op


revision: str = "b8d4e2f9c713"
down_revision: Union[str, Sequence[str], None] = "a7c9d2e4f601"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS report_insights_cache (
            id SERIAL PRIMARY KEY,
            cache_key VARCHAR(32) UNIQUE NOT NULL,
            report_type VARCHAR(50),
            insights_json TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_report_insights_cache_key_created
        ON report_insights_cache (cache_key, created_at)
        """
    )


def downgrade() -> None:
    op.drop_index(
        "idx_report_insights_cache_key_created",
        table_name="report_insights_cache",
    )
    op.drop_table("report_insights_cache")
