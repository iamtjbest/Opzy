"""unique skills and interests per profile

Revision ID: 072690cc6368
Revises: 2d6c5e3b3a6b
Create Date: 2026-09-18 09:18:01.359858

A profile's skill and interest lists are sets: the same skill or opportunity type twice
means nothing extra, and would double-count in matching. The API already dedupes before
writing; these constraints stop anything else (a bug, a manual insert) from sneaking
duplicates in. No existing rows are affected — the seed data has no profiles.

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '072690cc6368'
down_revision: Union[str, Sequence[str], None] = '2d6c5e3b3a6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "profile_skills_profile_id_skill_key", "profile_skills", ["profile_id", "skill"]
    )
    op.create_unique_constraint(
        "profile_interests_profile_id_opportunity_type_key",
        "profile_interests",
        ["profile_id", "opportunity_type"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "profile_interests_profile_id_opportunity_type_key", "profile_interests", type_="unique"
    )
    op.drop_constraint("profile_skills_profile_id_skill_key", "profile_skills", type_="unique")
