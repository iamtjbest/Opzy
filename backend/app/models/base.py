from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# The live schema stores these as `text` with CHECK constraints rather than native
# Postgres enum types, so they are plain strings here. Single-sourced because the
# matching engine and the request schemas both need to validate against them.
NOTIFICATION_CADENCES = ("instant", "daily", "weekly")
NOTIFICATION_CHANNELS = ("email", "whatsapp")
OPPORTUNITY_TYPES = (
    "job",
    "internship",
    "scholarship",
    "fellowship",
    "grant",
    "hackathon",
    "competition",
)
OPPORTUNITY_STATUSES = ("active", "expired", "removed")
USER_ACTIONS = ("saved", "dismissed", "applied")
