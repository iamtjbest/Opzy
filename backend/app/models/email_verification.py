import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Index, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EmailVerificationToken(Base):
    """One issued email-verification token. Only the hash is stored, never the token.

    Deliberately its own table rather than a `purpose` column on `password_reset_tokens`:
    sharing one table means a reset token can be spent as a verification token wherever a
    query forgets to filter, which would turn "I clicked forgot password" into "my address
    is proven". Two tables make that mistake impossible to write.
    """

    __tablename__ = "email_verification_tokens"
    __table_args__ = (
        # Issuing a token retires the user's outstanding ones, which reads by user_id.
        Index("email_verification_tokens_user_idx", "user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # sha256 hex of the token. Unique, so a lookup is a single indexed match.
    token_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    # Set the moment the token is spent, which is what makes it single-use.
    used_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
