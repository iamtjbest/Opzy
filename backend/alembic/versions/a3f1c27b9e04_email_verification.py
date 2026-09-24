"""email verification

Revision ID: a3f1c27b9e04
Revises: f47498afba0b
Create Date: 2026-09-22 00:00:00.000000

Sprint 9. email_verification_tokens mirrors password_reset_tokens — only the sha256 of each
issued token is stored, so a stolen row can't be turned back into a working link. It is a
separate table rather than a `purpose` column on the reset one so that a reset token can
never be spent as proof of address. users.email_verified_at records when the address was
proven; an unverified account works normally but is sent no notification email.

Existing rows are backfilled as verified: the only accounts in the database are development
and test ones, and leaving them null would silence local notification runs without telling
anyone anything true about those addresses.

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a3f1c27b9e04'
down_revision: Union[str, Sequence[str], None] = 'f47498afba0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

VERIFICATION_TABLE = "email_verification_tokens"
VERIFICATION_USER_INDEX = "email_verification_tokens_user_idx"


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        VERIFICATION_TABLE,
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
    op.create_index(VERIFICATION_USER_INDEX, VERIFICATION_TABLE, ["user_id"], unique=False)
    op.add_column(
        "users", sa.Column("email_verified_at", sa.TIMESTAMP(timezone=True), nullable=True)
    )
    # Grandfather the accounts that predate verification. See the note above.
    op.execute("update users set email_verified_at = now() where email_verified_at is null")
    # Same reasoning as 2d6c5e3b3a6b: RLS with no policies denies the anon/authenticated
    # roles every row, and the backend connects as the owner, which RLS doesn't apply to.
    op.execute(f"alter table {VERIFICATION_TABLE} enable row level security")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "email_verified_at")
    op.drop_index(VERIFICATION_USER_INDEX, table_name=VERIFICATION_TABLE)
    op.drop_table(VERIFICATION_TABLE)
