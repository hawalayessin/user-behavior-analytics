"""add password reset fields

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-04-14 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('platform_users', sa.Column('reset_token', sa.String(255), nullable=True))
    op.add_column('platform_users', sa.Column('reset_token_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_platform_users_reset_token', 'platform_users', ['reset_token'])


def downgrade() -> None:
    op.drop_index('ix_platform_users_reset_token', table_name='platform_users')
    op.drop_column('platform_users', 'reset_token_expires_at')
    op.drop_column('platform_users', 'reset_token')
