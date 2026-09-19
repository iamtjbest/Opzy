from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

MIN_JWT_SECRET_LENGTH = 32

# Anything that isn't a developer's own machine. A typo like "prod" used to fall through to
# the lenient branch, so the set is closed: an unknown value fails at startup.
Environment = Literal["development", "staging", "production"]
DEPLOYED_ENVIRONMENTS = ("staging", "production")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str = Field(..., alias="DATABASE_URL")
    cors_origins: str = Field("http://localhost:3000", alias="CORS_ORIGINS")
    environment: Environment = Field("development", alias="ENVIRONMENT")
    sql_echo: bool = Field(False, alias="SQL_ECHO")

    # min_length=1 because `.env.example` ships JWT_SECRET= empty: without it, an unset
    # secret is only caught by PyJWT at sign time, as a 500 on the first login.
    jwt_secret: str = Field(..., alias="JWT_SECRET", min_length=1)
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(60, alias="ACCESS_TOKEN_EXPIRE_MINUTES", gt=0)

    @model_validator(mode="after")
    def _require_strong_secret_when_deployed(self) -> "Settings":
        # An HS256 key shorter than its 256-bit output is brute-forceable offline from any
        # issued token, so refuse to boot a deployed environment with one.
        if (
            self.environment in DEPLOYED_ENVIRONMENTS
            and len(self.jwt_secret) < MIN_JWT_SECRET_LENGTH
        ):
            raise ValueError(
                f"JWT_SECRET must be at least {MIN_JWT_SECRET_LENGTH} characters when "
                f"ENVIRONMENT is {self.environment}."
            )
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as exc:
        raise RuntimeError(
            "Failed to load settings. Copy .env.example to .env and fill in DATABASE_URL "
            "and JWT_SECRET (see comments in .env.example)."
        ) from exc
