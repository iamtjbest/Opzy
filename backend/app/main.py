import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    account,
    actions,
    auth,
    feed,
    health,
    notification_settings,
    opportunities,
    profile,
)
from app.core.config import get_settings
from app.core.db import engine
from app.email import EMAIL_TIMEOUT_SECONDS

# Without this, every logger.info() call in the app (notably ConsoleSender in app/email.py,
# which is how a verification/reset email shows up at all in local dev) is silently
# dropped: Python's root logger has no handler and defaults to WARNING until something
# configures it, and uvicorn only sets up its own "uvicorn"/"uvicorn.access"/"uvicorn.error"
# loggers, never the root one. scripts/send_notifications.py already does this for the
# standalone cron entrypoint; this is the same fix for the API process.
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # One client for the app's lifetime: connection reuse, and somewhere for the email
    # backend to live that isn't rebuilt per request.
    async with httpx.AsyncClient(timeout=EMAIL_TIMEOUT_SECONDS) as http:
        app.state.http = http
        yield
    await engine.dispose()


# The interactive docs are a map of every endpoint and its inputs. Handy locally; nobody
# outside needs one of the deployed API.
DOCS_OFF = {"docs_url": None, "redoc_url": None, "openapi_url": None}

app = FastAPI(
    title="Opzy API",
    version="0.1.0",
    lifespan=lifespan,
    **(DOCS_OFF if settings.is_deployed else {}),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(opportunities.router)
app.include_router(feed.router)
app.include_router(actions.router)
app.include_router(notification_settings.router)
app.include_router(account.router)
