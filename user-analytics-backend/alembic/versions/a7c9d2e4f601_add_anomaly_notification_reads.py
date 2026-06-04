"""add anomaly notification read state

Revision ID: a7c9d2e4f601
Revises: 9f4c2a1b7d10
Create Date: 2026-05-23
"""

from typing import Sequence, Union

from alembic import op


revision: str = "a7c9d2e4f601"
down_revision: Union[str, Sequence[str], None] = "9f4c2a1b7d10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS anomaly_notification_reads (
            id UUID NOT NULL,
            user_id UUID NOT NULL REFERENCES platform_users(id) ON DELETE CASCADE,
            anomaly_id VARCHAR(64) NOT NULL,
            read_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            PRIMARY KEY (id)
        )
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_anomaly_notification_reads_user_anomaly'
            ) THEN
                ALTER TABLE anomaly_notification_reads
                ADD CONSTRAINT uq_anomaly_notification_reads_user_anomaly
                UNIQUE (user_id, anomaly_id);
            END IF;
        END
        $$;
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_anomaly_notification_reads_user_id "
        "ON anomaly_notification_reads (user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_anomaly_notification_reads_anomaly_id "
        "ON anomaly_notification_reads (anomaly_id)"
    )


def downgrade() -> None:
    op.drop_index("ix_anomaly_notification_reads_anomaly_id", table_name="anomaly_notification_reads")
    op.drop_index("ix_anomaly_notification_reads_user_id", table_name="anomaly_notification_reads")
    op.drop_table("anomaly_notification_reads")
