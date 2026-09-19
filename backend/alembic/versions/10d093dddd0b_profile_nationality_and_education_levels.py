"""profile nationality and education levels

Revision ID: 10d093dddd0b
Revises: 5c7fe4974834
Create Date: 2026-09-18 13:08:04.641765

Matching compares a profile against an opportunity's eligible countries and education
levels, so both sides need comparable values: nationality as an ISO code, and education
level from a fixed list instead of free text. Free-text levels stored so far ("University
student") can't be mapped reliably and only exist in dev data, so they're cleared, not
guessed. The level list is copied here, not imported, so this revision never changes.

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '10d093dddd0b'
down_revision: Union[str, Sequence[str], None] = '5c7fe4974834'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LEVELS = "('secondary', 'undergraduate', 'graduate', 'postgraduate')"


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("profiles", sa.Column("nationality", sa.Text(), nullable=True))
    op.create_check_constraint(
        "profiles_nationality_check", "profiles", "nationality ~ '^[A-Z]{2}$'"
    )
    op.execute(f"update profiles set education_level = null where education_level not in {LEVELS}")
    op.create_check_constraint(
        "profiles_education_level_check", "profiles", f"education_level in {LEVELS}"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("profiles_education_level_check", "profiles", type_="check")
    op.drop_constraint("profiles_nationality_check", "profiles", type_="check")
    op.drop_column("profiles", "nationality")
