"""add avatar url to platform users

Revision ID: f3b2d7c9a1e0
Revises: f2a7c6e8d901
Create Date: 2026-04-30 12:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f3b2d7c9a1e0"
down_revision: Union[str, None] = "f2a7c6e8d901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("platform_users", sa.Column("avatar_url", sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column("platform_users", "avatar_url")
