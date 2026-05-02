"""add analyst notes table

Revision ID: f4c2b0d1a7a9
Revises: f3b2d7c9a1e0
Create Date: 2026-05-02 10:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f4c2b0d1a7a9"
down_revision: Union[str, None] = "f3b2d7c9a1e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "analyst_notes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("analyst_id", sa.UUID(), nullable=False),
        sa.Column("service_id", sa.UUID(), nullable=True),
        sa.Column("campaign_id", sa.UUID(), nullable=True),
        sa.Column("metric", sa.String(length=50), nullable=True),
        sa.Column("period_start", sa.Date(), nullable=True),
        sa.Column("period_end", sa.Date(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["analyst_id"], ["platform_users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analyst_notes_analyst_id", "analyst_notes", ["analyst_id"], unique=False)
    op.create_index("ix_analyst_notes_service_id", "analyst_notes", ["service_id"], unique=False)
    op.create_index("ix_analyst_notes_campaign_id", "analyst_notes", ["campaign_id"], unique=False)
    op.create_index("ix_analyst_notes_metric", "analyst_notes", ["metric"], unique=False)
    op.create_index("ix_analyst_notes_period_start", "analyst_notes", ["period_start"], unique=False)
    op.create_index("ix_analyst_notes_period_end", "analyst_notes", ["period_end"], unique=False)
    op.create_index("ix_analyst_notes_created_at", "analyst_notes", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_analyst_notes_created_at", table_name="analyst_notes")
    op.drop_index("ix_analyst_notes_period_end", table_name="analyst_notes")
    op.drop_index("ix_analyst_notes_period_start", table_name="analyst_notes")
    op.drop_index("ix_analyst_notes_metric", table_name="analyst_notes")
    op.drop_index("ix_analyst_notes_campaign_id", table_name="analyst_notes")
    op.drop_index("ix_analyst_notes_service_id", table_name="analyst_notes")
    op.drop_index("ix_analyst_notes_analyst_id", table_name="analyst_notes")
    op.drop_table("analyst_notes")
