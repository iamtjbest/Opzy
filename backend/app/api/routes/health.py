from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.core.config import get_settings
from app.core.db import engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(response: Response) -> dict:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("select 1"))
    except Exception as exc:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        body = {"status": "degraded", "database": "unreachable"}
        # Connection errors can echo back the DSN, so keep them out of production responses.
        if get_settings().environment == "development":
            body["detail"] = str(exc)
        return body

    return {"status": "ok", "database": "connected"}
