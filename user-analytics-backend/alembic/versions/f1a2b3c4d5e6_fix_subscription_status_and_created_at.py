"""fix subscription status and created_at

Revision ID: f1a2b3c4d5e6
Revises: b7e2c4f91a10
Create Date: 2026-04-06 10:40:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "b7e2c4f91a10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Repair historical subscriptions status + created_at mapping."""
    op.execute(
        """
        UPDATE subscriptions
        SET created_at = subscription_start_date
        WHERE DATE(created_at AT TIME ZONE 'UTC') = '2026-04-03'
          AND subscription_start_date IS NOT NULL
        """
    )

    op.execute(
        """
        UPDATE subscriptions
        SET status = 'billing_failed'
        WHERE status = 'expired'
        """
    )

    op.execute(
        """
        UPDATE subscriptions
        SET status = 'pending'
        WHERE status = 'inactive'
        """
    )


def downgrade() -> None:
    """Best-effort downgrade for renamed status values only."""
    op.execute(
        """
        UPDATE subscriptions
        SET status = 'expired'
        WHERE status = 'billing_failed'
        """
    )

    op.execute(
        """
        UPDATE subscriptions
        SET status = 'inactive'
        WHERE status = 'pending'
        """
    )
