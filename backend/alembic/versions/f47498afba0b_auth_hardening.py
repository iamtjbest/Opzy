"""auth hardening

Revision ID: f47498afba0b
Revises: b6c72226a5c2
Create Date: 2026-09-20 14:33:28.534602

Sprint 7. rate_limit_hits counts attempts per key per fixed window, so throttling survives
more than one API worker. password_reset_tokens holds only the sha256 of each issued token,
so a stolen row can't be turned back into a working link. users.password_changed_at retires
access tokens minted before a reset.

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f47498afba0b'
down_revision: Union[str, Sequence[str], None] = 'b6c72226a5c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

RATE_LIMIT_TABLE = "rate_limit_hits"
RESET_TABLE = "password_reset_tokens"
RESET_USER_INDEX = "password_reset_tokens_user_idx"


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        RATE_LIMIT_TABLE,
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("window_start", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.PrimaryKeyConstraint("key", "window_start"),
    )
    op.create_table(
        RESET_TABLE,
        sa.Column("id", sa.UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("used_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(RESET_USER_INDEX, RESET_TABLE, ["user_id"], unique=False)
    op.add_column(
        "users", sa.Column("password_changed_at", sa.TIMESTAMP(timezone=True), nullable=True)
    )
    # Same reasoning as 2d6c5e3b3a6b: RLS with no policies denies the anon/authenticated
    # roles every row, and the backend connects as the owner, which RLS doesn't apply to.
    for table in (RATE_LIMIT_TABLE, RESET_TABLE):
        op.execute(f"alter table {table} enable row level security")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "password_changed_at")
    op.drop_index(RESET_USER_INDEX, table_name=RESET_TABLE)
    op.drop_table(RESET_TABLE)
    op.drop_table(RATE_LIMIT_TABLE)
