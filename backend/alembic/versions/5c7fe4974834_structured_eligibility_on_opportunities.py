"""structured eligibility on opportunities

Revision ID: 5c7fe4974834
Revises: 072690cc6368
Create Date: 2026-09-18 12:37:49.942139

Hard eligibility (country, education level) and relevance data (fields, skills) as real
columns, so matching reads structured values instead of parsing eligibility_notes. Empty
arrays mean unrestricted / none listed, so existing rows stay visible to everyone until
the sheet fills them in.

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5c7fe4974834'
down_revision: Union[str, Sequence[str], None] = '072690cc6368'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COLUMNS = ("eligible_countries", "education_levels", "fields_of_study", "skills")


def upgrade() -> None:
    """Upgrade schema."""
    for column in COLUMNS:
        op.add_column(
            "opportunities",
            sa.Column(
                column,
                postgresql.ARRAY(sa.Text()),
                nullable=False,
                server_default=sa.text("'{}'"),
            ),
        )


def downgrade() -> None:
    """Downgrade schema."""
    for column in reversed(COLUMNS):
        op.drop_column("opportunities", column)
