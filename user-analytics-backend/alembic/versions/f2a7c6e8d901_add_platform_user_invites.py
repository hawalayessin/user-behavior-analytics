"""add platform user invites table

Revision ID: f2a7c6e8d901
Revises: c9d8e7f6a5b4
Create Date: 2026-04-30 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f2a7c6e8d901"
down_revision = "c9d8e7f6a5b4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "platform_user_invites",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="analyst"),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("invited_by", sa.UUID(), nullable=False),
        sa.Column("invited_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["invited_by"], ["platform_users.id"],),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("token"),
    )
    op.create_index(
        "ix_platform_user_invites_email",
        "platform_user_invites",
        ["email"],
        unique=False,
    )
    op.create_index(
        "ix_platform_user_invites_token",
        "platform_user_invites",
        ["token"],
        unique=False,
    )
    op.create_index(
        "ix_platform_user_invites_used_at",
        "platform_user_invites",
        ["used_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_platform_user_invites_used_at", table_name="platform_user_invites")
    op.drop_index("ix_platform_user_invites_token", table_name="platform_user_invites")
    op.drop_index("ix_platform_user_invites_email", table_name="platform_user_invites")
    op.drop_table("platform_user_invites")
