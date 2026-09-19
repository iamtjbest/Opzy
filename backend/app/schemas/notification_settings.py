from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.models.base import NOTIFICATION_CADENCES, NOTIFICATION_CHANNELS

Cadence = Literal[NOTIFICATION_CADENCES]  # type: ignore[valid-type]
Channel = Literal[NOTIFICATION_CHANNELS]  # type: ignore[valid-type]


class NotificationSettingsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cadence: Cadence


class NotificationSettings(BaseModel):
    cadence: Cadence
    # Read-only for now: email is the only channel until WhatsApp is built.
    channel: Channel
