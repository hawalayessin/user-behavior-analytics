"""merge heads

Revision ID: feb49323daed
Revises: b9c1d2e3f4a5, f4c2b0d1a7a9
Create Date: 2026-05-03 22:23:43.545707

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'feb49323daed'
down_revision: Union[str, Sequence[str], None] = ('b9c1d2e3f4a5', 'f4c2b0d1a7a9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
