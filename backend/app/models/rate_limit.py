from datetime import datetime

from sqlalchemy import TIMESTAMP, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RateLimitHit(Base):
    """Attempts against one key inside one fixed window.

    Counted in the database rather than in memory so the limit still holds when the API
    runs as more than one worker.
    """

    __tablename__ = "rate_limit_hits"

    key: Mapped[str] = mapped_column(Text, primary_key=True)
    window_start: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), primary_key=True
    )
    count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
