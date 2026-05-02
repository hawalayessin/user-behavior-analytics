"""add url to services

Revision ID: c9d8e7f6a5b4
Revises: a1b2c3d4e5f6
Create Date: 2026-04-23 11:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c9d8e7f6a5b4"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("services", sa.Column("url", sa.String(length=255), nullable=True))

    # Backfill known service URLs for analytics DB.
    op.execute(
        """
        UPDATE services
        SET url = 'https://tawer.net/'
        WHERE LOWER(name) LIKE '%tawer%'
          AND (url IS NULL OR url = '')
        """
    )

    op.execute(
        """
        UPDATE services
        SET url = 'https://esports.tn/'
        WHERE LOWER(name) LIKE '%esports%'
                    AND (url IS NULL OR url = '')
        """
    )

    op.execute(
        """
        UPDATE services
        SET url = 'https://eljournal.tn/'
        WHERE LOWER(name) LIKE '%journal%'
                    AND (url IS NULL OR url = '')
        """
    )

    op.execute(
        """
        UPDATE services
        SET url = 'https://almou7a9e9.net/'
                WHERE (LOWER(name) LIKE '%mou7a9e9%'
                     OR LOWER(name) LIKE '%almou7a9e9%')
                    AND (url IS NULL OR url = '')
        """
    )

    op.execute(
        """
        UPDATE services
        SET url = 'https://www.ttoons.cloud/'
        WHERE LOWER(name) LIKE '%ttoons%'
                    AND (url IS NULL OR url = '')
        """
    )

    op.execute(
        """
        UPDATE services
        SET url = 'https://rafi9niplus.tn/'
        WHERE LOWER(name) LIKE '%rafi9niplus%'
                    AND (url IS NULL OR url = '')
        """
    )

    op.execute(
        """
        UPDATE services
        SET url = 'https://smarttoons.tn/'
        WHERE LOWER(name) LIKE '%smarttoons%'
                    AND (url IS NULL OR url = '')
        """
    )

    op.execute(
        """
        UPDATE services
        SET url = 'https://rafi9ni.tn/'
        WHERE LOWER(name) LIKE '%rafi9ni%'
          AND LOWER(name) NOT LIKE '%plus%'
                    AND (url IS NULL OR url = '')
        """
    )

    op.execute(
        """
        UPDATE services
        SET url = 'https://3ich-healthy.tn/'
                WHERE (LOWER(name) LIKE '%3ich%'
                     OR LOWER(name) LIKE '%healthy%')
                    AND (url IS NULL OR url = '')
        """
    )


def downgrade() -> None:
    op.drop_column("services", "url")
