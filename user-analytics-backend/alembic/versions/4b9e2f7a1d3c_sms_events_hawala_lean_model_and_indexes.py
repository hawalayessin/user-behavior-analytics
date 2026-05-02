"""sms events prod_db lean model and indexes

Revision ID: 4b9e2f7a1d3c
Revises: c1f4a2d9e8b1
Create Date: 2026-04-04 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4b9e2f7a1d3c"
down_revision: Union[str, Sequence[str], None] = "c1f4a2d9e8b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("sms_events", "user_id", existing_type=sa.UUID(), nullable=True)

    op.execute("""
    UPDATE sms_events
    SET source_system = 'prod_db.message_events'
    WHERE source_system IS NULL
    """)

    op.execute("""
    UPDATE sms_events
    SET direction = 'OUTBOUND'
    WHERE direction IS NULL
    """)

    op.alter_column(
        "sms_events",
        "is_otp",
        existing_type=sa.Boolean(),
        server_default=sa.text("false"),
        existing_nullable=False,
    )
    op.alter_column(
        "sms_events",
        "is_activation",
        existing_type=sa.Boolean(),
        server_default=sa.text("false"),
        existing_nullable=False,
    )
    op.alter_column(
        "sms_events",
        "direction",
        existing_type=sa.String(length=20),
        server_default=sa.text("'OUTBOUND'"),
        existing_nullable=False,
    )
    op.alter_column(
        "sms_events",
        "source_system",
        existing_type=sa.String(length=50),
        nullable=False,
        server_default=sa.text("'prod_db.message_events'"),
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_sms_events_event_type_event_datetime
        ON sms_events (event_type, event_datetime DESC)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_sms_events_source_system
        ON sms_events (source_system)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_sms_events_metadata_gin
        ON sms_events USING GIN (metadata)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_sms_events_metadata_gin")
    op.execute("DROP INDEX IF EXISTS idx_sms_events_source_system")
    op.execute("DROP INDEX IF EXISTS idx_sms_events_event_type_event_datetime")

    op.alter_column(
        "sms_events",
        "source_system",
        existing_type=sa.String(length=50),
        nullable=True,
        server_default=None,
    )
    op.alter_column(
        "sms_events",
        "direction",
        existing_type=sa.String(length=20),
        server_default=None,
        existing_nullable=False,
    )
    op.alter_column(
        "sms_events",
        "is_activation",
        existing_type=sa.Boolean(),
        server_default=None,
        existing_nullable=False,
    )
    op.alter_column(
        "sms_events",
        "is_otp",
        existing_type=sa.Boolean(),
        server_default=None,
        existing_nullable=False,
    )

    op.alter_column("sms_events", "user_id", existing_type=sa.UUID(), nullable=False)

