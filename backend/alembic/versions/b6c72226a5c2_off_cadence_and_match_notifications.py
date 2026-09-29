"""off cadence and match notifications

Revision ID: b6c72226a5c2
Revises: ffa8c8d23fea
Create Date: 2026-09-19 22:10:56.062494

Users can turn notification emails off, with a new "off" cadence. match_notifications
records each opportunity emailed to each user, so none is sent twice, and tells a digest
when the last email went out. Values are copied here, not imported, so this revision
never changes.

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b6c72226a5c2'
down_revision: Union[str, Sequence[str], None] = 'ffa8c8d23fea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CHECK = "users_notification_cadence_check"
TABLE = "match_notifications"
INDEX = "match_notifications_user_opp_idx"


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(CHECK, "users", type_="check")
    op.create_check_constraint(
        CHECK, "users", "notification_cadence in ('instant', 'daily', 'weekly', 'off')"
    )
    op.create_table(
        TABLE,
        sa.Column("id", sa.UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("opportunity_id", sa.UUID(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("sent_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["opportunity_id"], ["opportunities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(INDEX, TABLE, ["user_id", "opportunity_id"], unique=True)
    # Every table has RLS on (2d6c5e3b3a6b). The backend owns the tables, so it's unaffected.
    op.execute(f"alter table {TABLE} enable row level security")


def downgrade() -> None:
    """Downgrade schema."""
    # Changing "off" users to another cadence would start emailing people who opted out, so
    # refuse instead and leave the decision to whoever is downgrading.
    has_off = op.get_bind().scalar(
        sa.text("select exists (select 1 from users where notification_cadence = 'off')")
    )
    if has_off:
        raise RuntimeError(
            "Some users have notification_cadence 'off'; the old constraint can't hold it. "
            "Decide what they should become, then downgrade."
        )
    op.drop_table(TABLE)
    op.drop_constraint(CHECK, "users", type_="check")
    op.create_check_constraint(
        CHECK, "users", "notification_cadence in ('instant', 'daily', 'weekly')"
    )
