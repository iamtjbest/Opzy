from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.models import User
from app.schemas.notification_settings import NotificationSettings, NotificationSettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


def _read(user: User) -> NotificationSettings:
    return NotificationSettings(
        cadence=user.notification_cadence, channel=user.notification_channel
    )


@router.get("/notifications", response_model=NotificationSettings)
async def get_notification_settings(user: CurrentUser) -> NotificationSettings:
    return _read(user)


@router.put("/notifications", response_model=NotificationSettings)
async def put_notification_settings(
    body: NotificationSettingsUpdate, user: CurrentUser, db: DbSession
) -> NotificationSettings:
    # `user` was loaded through this request's session, so this updates its row.
    user.notification_cadence = body.cadence
    await db.commit()
    return _read(user)
