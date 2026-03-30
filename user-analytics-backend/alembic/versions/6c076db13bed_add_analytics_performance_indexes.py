"""add_analytics_performance_indexes

Revision ID: 6c076db13bed
Revises: 3939f80c5a66
Create Date: 2026-03-30 16:57:34.320909

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '6c076db13bed'
down_revision: Union[str, Sequence[str], None] = '3939f80c5a66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # NOTE:
    # Existing indexes already cover many single-column filters.
    # We add only missing/high-value indexes for analytics queries, and use
    # IF NOT EXISTS to keep migration idempotent across environments.

    # billing_events
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_billing_events_datetime_status "
        "ON billing_events (event_datetime, status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_billing_events_service_datetime "
        "ON billing_events (service_id, event_datetime)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_billing_events_user_datetime "
        "ON billing_events (user_id, event_datetime)"
    )

    # subscriptions
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_subscriptions_end_date "
        "ON subscriptions (subscription_end_date)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_subscriptions_status_end_date "
        "ON subscriptions (status, subscription_end_date)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_subscriptions_service_start_date "
        "ON subscriptions (service_id, subscription_start_date)"
    )

    # user_activities
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_user_activities_service_id "
        "ON user_activities (service_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_user_activities_datetime_type "
        "ON user_activities (activity_datetime, activity_type)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_user_activities_service_datetime "
        "ON user_activities (service_id, activity_datetime)"
    )

    # cohorts
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_cohorts_service_id "
        "ON cohorts (service_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_cohorts_service_cohort_date "
        "ON cohorts (service_id, cohort_date)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS idx_cohorts_service_cohort_date")
    op.execute("DROP INDEX IF EXISTS idx_cohorts_service_id")

    op.execute("DROP INDEX IF EXISTS idx_user_activities_service_datetime")
    op.execute("DROP INDEX IF EXISTS idx_user_activities_datetime_type")
    op.execute("DROP INDEX IF EXISTS idx_user_activities_service_id")

    op.execute("DROP INDEX IF EXISTS idx_subscriptions_service_start_date")
    op.execute("DROP INDEX IF EXISTS idx_subscriptions_status_end_date")
    op.execute("DROP INDEX IF EXISTS idx_subscriptions_end_date")

    op.execute("DROP INDEX IF EXISTS idx_billing_events_user_datetime")
    op.execute("DROP INDEX IF EXISTS idx_billing_events_service_datetime")
    op.execute("DROP INDEX IF EXISTS idx_billing_events_datetime_status")
