"""enable row level security on all tables

Revision ID: 2d6c5e3b3a6b
Revises: bd8b4cb127da
Create Date: 2026-09-17 15:43:00.641900

Supabase exposes every table in `public` through its auto-generated REST API to the `anon`
and `authenticated` roles. Enabling RLS with no policies denies those roles all rows.

The backend is unaffected: it connects as the tables' owner, and RLS does not apply to a
table's owner (no FORCE ROW LEVEL SECURITY) or to superusers. Per-user policies aren't
written because the API issues its own JWTs, so Supabase's `auth.uid()` would never be set;
access control lives in the API instead.

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '2d6c5e3b3a6b'
down_revision: Union[str, Sequence[str], None] = 'bd8b4cb127da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = (
    "users",
    "profiles",
    "profile_skills",
    "profile_interests",
    "opportunities",
    "opportunity_matches",
    "user_opportunity_actions",
    "alembic_version",
)


def upgrade() -> None:
    """Upgrade schema."""
    for table in TABLES:
        op.execute(f"alter table {table} enable row level security")


def downgrade() -> None:
    """Downgrade schema."""
    for table in TABLES:
        op.execute(f"alter table {table} disable row level security")
