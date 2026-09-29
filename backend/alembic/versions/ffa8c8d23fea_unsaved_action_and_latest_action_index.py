"""unsaved action and latest action index

Revision ID: ffa8c8d23fea
Revises: 10d093dddd0b
Create Date: 2026-09-19 17:23:57.380905

Users can now remove a saved opportunity. The actions table is an append-only log, so
removal is recorded as a new "unsaved" action, not a delete. The index serves the
"latest action per opportunity" lookup. Values are copied here, not imported, so this
revision never changes.

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'ffa8c8d23fea'
down_revision: Union[str, Sequence[str], None] = '10d093dddd0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE = "user_opportunity_actions"
CHECK = "user_opportunity_actions_action_check"
INDEX = "user_opportunity_actions_user_opp_created_idx"


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(CHECK, TABLE, type_="check")
    op.create_check_constraint(
        CHECK, TABLE, "action in ('saved', 'unsaved', 'dismissed', 'applied')"
    )
    op.create_index(INDEX, TABLE, ["user_id", "opportunity_id", "created_at"])


def downgrade() -> None:
    """Downgrade schema."""
    # Deleting "unsaved" rows would silently turn removed items back into saved ones, so
    # refuse instead and leave the decision to whoever is downgrading.
    has_unsaved = op.get_bind().scalar(
        sa.text(f"select exists (select 1 from {TABLE} where action = 'unsaved')")
    )
    if has_unsaved:
        raise RuntimeError(
            f"{TABLE} has 'unsaved' rows; the old constraint can't hold them. "
            "Decide what they should become, then downgrade."
        )
    op.drop_index(INDEX, table_name=TABLE)
    op.drop_constraint(CHECK, TABLE, type_="check")
    op.create_check_constraint(CHECK, TABLE, "action in ('saved', 'dismissed', 'applied')")
