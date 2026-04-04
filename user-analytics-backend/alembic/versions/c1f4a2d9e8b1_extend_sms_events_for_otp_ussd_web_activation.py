"""extend sms_events for otp ussd web activation

Revision ID: c1f4a2d9e8b1
Revises: 85b71708c64d
Create Date: 2026-04-03 19:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c1f4a2d9e8b1"
down_revision: Union[str, Sequence[str], None] = "85b71708c64d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _resolve_sms_table_name(inspector: sa.Inspector) -> str:
    if inspector.has_table("sms_events"):
        return "sms_events"
    if inspector.has_table("smsevents"):
        return "smsevents"
    raise RuntimeError("Neither 'sms_events' nor 'smsevents' exists in current schema")


def _column_exists(inspector: sa.Inspector, table_name: str, col: str) -> bool:
    return any(c["name"] == col for c in inspector.get_columns(table_name))


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(ix.get("name") == index_name for ix in inspector.get_indexes(table_name))


def _add_col_if_missing(inspector: sa.Inspector, table_name: str, column: sa.Column) -> bool:
    if _column_exists(inspector, table_name, column.name):
        return False
    op.add_column(table_name, column)
    return True


def _create_index_if_missing(
    inspector: sa.Inspector,
    table_name: str,
    index_name: str,
    columns: list[str],
    *,
    postgresql_where: sa.ClauseElement | None = None,
) -> None:
    if _index_exists(inspector, table_name, index_name):
        return
    op.create_index(
        index_name,
        table_name,
        columns,
        unique=False,
        postgresql_where=postgresql_where,
    )


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = _resolve_sms_table_name(inspector)

    added_is_otp = _add_col_if_missing(
        inspector,
        table_name,
        sa.Column("is_otp", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    added_is_activation = _add_col_if_missing(
        inspector,
        table_name,
        sa.Column("is_activation", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )

    _add_col_if_missing(inspector, table_name, sa.Column("channel", sa.String(length=30), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("activation_channel", sa.String(length=30), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("source_system", sa.String(length=50), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("template_name", sa.String(length=100), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("template_code", sa.String(length=100), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("otp_code", sa.String(length=20), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("activation_status", sa.String(length=30), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("flow_name", sa.String(length=100), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("session_id", sa.String(length=100), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("external_ref", sa.String(length=100), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("phone_number", sa.String(length=30), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("shortcode", sa.String(length=30), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("ussd_code", sa.String(length=30), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("website_path", sa.String(length=255), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("landing_page", sa.String(length=255), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("event_result", sa.String(length=50), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("failure_reason", sa.Text(), nullable=True))
    _add_col_if_missing(inspector, table_name, sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # Drop temporary defaults to keep schema clean.
    if added_is_otp:
        op.alter_column(table_name, "is_otp", server_default=None)
    if added_is_activation:
        op.alter_column(table_name, "is_activation", server_default=None)

    # Simple indexes.
    _create_index_if_missing(inspector, table_name, "idx_sms_evt_event_datetime", ["event_datetime"])
    _create_index_if_missing(inspector, table_name, "idx_sms_evt_event_type", ["event_type"])
    _create_index_if_missing(inspector, table_name, "idx_sms_evt_channel", ["channel"])
    _create_index_if_missing(inspector, table_name, "idx_sms_evt_activation_channel", ["activation_channel"])
    _create_index_if_missing(inspector, table_name, "idx_sms_evt_is_otp", ["is_otp"])
    _create_index_if_missing(inspector, table_name, "idx_sms_evt_is_activation", ["is_activation"])
    _create_index_if_missing(inspector, table_name, "idx_sms_evt_service_id", ["service_id"])
    _create_index_if_missing(inspector, table_name, "idx_sms_evt_user_id", ["user_id"])
    _create_index_if_missing(inspector, table_name, "idx_sms_evt_delivery_status", ["delivery_status"])

    # Composite indexes.
    _create_index_if_missing(inspector, table_name, "idx_sms_evt_dt_channel", ["event_datetime", "channel"])
    _create_index_if_missing(inspector, table_name, "idx_sms_evt_service_dt", ["service_id", "event_datetime"])
    _create_index_if_missing(inspector, table_name, "idx_sms_evt_user_dt", ["user_id", "event_datetime"])
    _create_index_if_missing(inspector, table_name, "idx_sms_evt_activation_channel_dt", ["activation_channel", "event_datetime"])
    _create_index_if_missing(inspector, table_name, "idx_sms_evt_delivery_status_dt", ["delivery_status", "event_datetime"])

    # Partial indexes for hot dashboard filters.
    _create_index_if_missing(
        inspector,
        table_name,
        "idx_sms_evt_otp_partial",
        ["event_datetime"],
        postgresql_where=sa.text("is_otp = true"),
    )
    _create_index_if_missing(
        inspector,
        table_name,
        "idx_sms_evt_activation_partial",
        ["event_datetime"],
        postgresql_where=sa.text("is_activation = true"),
    )
    _create_index_if_missing(
        inspector,
        table_name,
        "idx_sms_evt_failed_delivery_partial",
        ["event_datetime"],
        postgresql_where=sa.text("delivery_status = 'FAILED'"),
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = _resolve_sms_table_name(inspector)

    indexes_to_drop = [
        "idx_sms_evt_failed_delivery_partial",
        "idx_sms_evt_activation_partial",
        "idx_sms_evt_otp_partial",
        "idx_sms_evt_delivery_status_dt",
        "idx_sms_evt_activation_channel_dt",
        "idx_sms_evt_user_dt",
        "idx_sms_evt_service_dt",
        "idx_sms_evt_dt_channel",
        "idx_sms_evt_delivery_status",
        "idx_sms_evt_user_id",
        "idx_sms_evt_service_id",
        "idx_sms_evt_is_activation",
        "idx_sms_evt_is_otp",
        "idx_sms_evt_activation_channel",
        "idx_sms_evt_channel",
        "idx_sms_evt_event_type",
        "idx_sms_evt_event_datetime",
    ]

    for idx in indexes_to_drop:
        if _index_exists(inspector, table_name, idx):
            op.drop_index(idx, table_name=table_name)

    columns_to_drop = [
        "metadata",
        "failure_reason",
        "event_result",
        "landing_page",
        "website_path",
        "ussd_code",
        "shortcode",
        "phone_number",
        "external_ref",
        "session_id",
        "flow_name",
        "activation_status",
        "is_activation",
        "is_otp",
        "otp_code",
        "template_code",
        "template_name",
        "source_system",
        "activation_channel",
        "channel",
    ]

    for col in columns_to_drop:
        if _column_exists(inspector, table_name, col):
            op.drop_column(table_name, col)
