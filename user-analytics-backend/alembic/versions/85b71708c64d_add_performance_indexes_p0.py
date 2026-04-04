"""add_performance_indexes_p0

Revision ID: 85b71708c64d
Revises: 6c076db13bed
Create Date: 2026-04-03 12:51:52.911756

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '85b71708c64d'
down_revision: Union[str, Sequence[str], None] = '6c076db13bed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # CONCURRENTLY ne peut pas tourner dans une transaction.
    # Alembic ouvre une transaction par defaut -> il faut la fermer.
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
        idx_subscriptions_status_service_end_partial
        ON subscriptions (service_id, subscription_end_date)
        WHERE status IN ('cancelled','expired')
        """
    )

    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
        idx_subscriptions_service_end
        ON subscriptions (service_id, subscription_end_date)
        """
    )

    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
        idx_subscriptions_service_start_user
        ON subscriptions (service_id, subscription_start_date, user_id)
        """
    )

    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
        idx_billing_events_sub_success_dt
        ON billing_events (subscription_id, event_datetime)
        WHERE status = 'success'
        """
    )

    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
        idx_billing_events_sub_failed_dt
        ON billing_events (subscription_id, event_datetime)
        WHERE status = 'failed'
        """
    )

    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
        idx_campaigns_service_send_datetime
        ON campaigns (service_id, send_datetime)
        """
    )

    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
        idx_users_status_last_activity
        ON users (status, last_activity_at)
        """
    )

    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
        idx_user_activities_service_user_dt
        ON user_activities (service_id, user_id, activity_datetime)
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS idx_subscriptions_status_service_end_partial")
    op.execute("DROP INDEX IF EXISTS idx_subscriptions_service_end")
    op.execute("DROP INDEX IF EXISTS idx_subscriptions_service_start_user")
    op.execute("DROP INDEX IF EXISTS idx_billing_events_sub_success_dt")
    op.execute("DROP INDEX IF EXISTS idx_billing_events_sub_failed_dt")
    op.execute("DROP INDEX IF EXISTS idx_campaigns_service_send_datetime")
    op.execute("DROP INDEX IF EXISTS idx_users_status_last_activity")
    op.execute("DROP INDEX IF EXISTS idx_user_activities_service_user_dt")
