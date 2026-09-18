import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Index, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = (Index("profiles_user_id_idx", "user_id", unique=True),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    education_level: Mapped[str | None] = mapped_column(Text)
    field_of_study: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(Text)
    # ISO 3166 alpha-2, e.g. "NG". Matching's country check reads this, not `location`.
    nationality: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )


class ProfileSkill(Base):
    __tablename__ = "profile_skills"
    __table_args__ = (
        Index("profile_skills_profile_id_idx", "profile_id"),
        UniqueConstraint("profile_id", "skill", name="profile_skills_profile_id_skill_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    skill: Mapped[str] = mapped_column(Text, nullable=False)


class ProfileInterest(Base):
    __tablename__ = "profile_interests"
    __table_args__ = (
        Index("profile_interests_profile_id_idx", "profile_id"),
        UniqueConstraint(
            "profile_id",
            "opportunity_type",
            name="profile_interests_profile_id_opportunity_type_key",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_type: Mapped[str] = mapped_column(Text, nullable=False)
