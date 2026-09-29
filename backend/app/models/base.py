from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# The live schema stores these as `text` with CHECK constraints rather than native
# Postgres enum types, so they are plain strings here. Single-sourced because the
# matching engine and the request schemas both need to validate against them.
# "off" means no emails at all.
NOTIFICATION_CADENCES = ("instant", "daily", "weekly", "off")
INSTANT, DAILY, WEEKLY, OFF = NOTIFICATION_CADENCES
NOTIFICATION_CHANNELS = ("email", "whatsapp")
# WhatsApp is deferred, so this is the only channel anything is sent on.
EMAIL_CHANNEL = NOTIFICATION_CHANNELS[0]
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
# The one status users ever see in listings and the feed.
ACTIVE_STATUS = OPPORTUNITY_STATUSES[0]
# Pulled from the product: never served, and can't be acted on.
REMOVED_STATUS = OPPORTUNITY_STATUSES[2]
# user_opportunity_actions is a log, one row per action; a user's current state for an
# opportunity is its latest row. "unsaved" leaves no state.
USER_ACTIONS = ("saved", "unsaved", "dismissed", "applied")
SAVED, UNSAVED, DISMISSED, APPLIED = USER_ACTIONS
# Why a user dismissed an opportunity. Checked by the API only, so the list can change
# without a migration.
DISMISS_REASONS = ("not_relevant", "pay_too_low", "not_eligible", "not_interested_org", "other")

# Profile education level, and what an opportunity accepts. "graduate" means a first degree
# or HND and not studying now; "postgraduate" means a master's or PhD student or holder.
EDUCATION_LEVELS = ("secondary", "undergraduate", "graduate", "postgraduate")
