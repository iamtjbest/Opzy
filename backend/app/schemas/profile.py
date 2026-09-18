from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from app.models.base import OPPORTUNITY_TYPES

MAX_TEXT_LENGTH = 100
MAX_SKILLS = 30
MAX_SKILL_LENGTH = 50

OpportunityType = Literal[OPPORTUNITY_TYPES]  # type: ignore[valid-type]

ProfileText = Annotated[str, Field(max_length=MAX_TEXT_LENGTH)]

# Lowercased so "Python" and "python" are one skill; matching compares them as equal anyway.
Skill = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_lower=True, min_length=1, max_length=MAX_SKILL_LENGTH
    ),
]


class ProfileUpdate(BaseModel):
    """The whole profile, replacing what's stored.

    Every field is required: with full replacement, a key the client forgot would silently
    wipe that field. Send null or [] to clear one.
    """

    model_config = ConfigDict(extra="forbid")

    education_level: ProfileText | None
    field_of_study: ProfileText | None
    location: ProfileText | None
    skills: list[Skill] = Field(max_length=MAX_SKILLS)
    interests: list[OpportunityType] = Field(max_length=len(OPPORTUNITY_TYPES))

    @field_validator("education_level", "field_of_study", "location", mode="before")
    @classmethod
    def _blank_to_none(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip() or None
        return value

    @field_validator("skills", "interests")
    @classmethod
    def _dedupe(cls, value: list[str]) -> list[str]:
        return list(dict.fromkeys(value))


class ProfileRead(BaseModel):
    education_level: str | None
    field_of_study: str | None
    location: str | None
    skills: list[str]
    interests: list[OpportunityType]
    updated_at: datetime
