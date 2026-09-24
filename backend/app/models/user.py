import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    # Null for accounts that have never changed their password. Access tokens issued before
    # this instant are rejected, so a reset locks out anyone holding a stolen token.
    password_changed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    # Null until the address is proven by clicking an emailed link. An unverified account
    # works normally but is never sent notification email — see app/notifications/run.py.
    email_verified_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    notification_cadence: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'daily'")
    )
    notification_channel: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'email'")
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
