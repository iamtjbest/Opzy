import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.security import MAX_PASSWORD_LENGTH


def normalize_email(email: str) -> str:
    # The users.email unique constraint is case-sensitive, so normalize before it's hit.
    return email.strip().lower()


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=MAX_PASSWORD_LENGTH)

    @field_validator("email", mode="before")
    @classmethod
    def _normalize_email(cls, value: object) -> object:
        return normalize_email(value) if isinstance(value, str) else value


class UserRead(BaseModel):
    """Public view of a user. Deliberately has no password field of any kind."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    notification_cadence: str
    notification_channel: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SignupResponse(TokenResponse):
    user: UserRead


class PasswordResetRequest(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def _normalize_email(cls, value: object) -> object:
        return normalize_email(value) if isinstance(value, str) else value


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=8, max_length=MAX_PASSWORD_LENGTH)
