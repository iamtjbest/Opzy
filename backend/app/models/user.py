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
    notification_cadence: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'daily'")
    )
    notification_channel: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'email'")
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
