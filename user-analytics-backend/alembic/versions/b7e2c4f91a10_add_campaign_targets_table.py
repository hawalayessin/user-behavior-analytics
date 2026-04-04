"""add campaign_targets table

Revision ID: b7e2c4f91a10
Revises: 4b9e2f7a1d3c
Create Date: 2026-04-04 12:05:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b7e2c4f91a10"
down_revision: Union[str, Sequence[str], None] = "4b9e2f7a1d3c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "campaign_targets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("segment", sa.String(length=100), nullable=True),
        sa.Column("region", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=True, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("campaign_id", "phone_number", name="uq_campaign_targets_campaign_phone"),
    )

    op.create_index("idx_ct_campaign", "campaign_targets", ["campaign_id"], unique=False)
    op.create_index("idx_ct_phone", "campaign_targets", ["phone_number"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_ct_phone", table_name="campaign_targets")
    op.drop_index("idx_ct_campaign", table_name="campaign_targets")
    op.drop_table("campaign_targets")
