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

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # One client for the app's lifetime: connection reuse, and somewhere for the email
    # backend to live that isn't rebuilt per request.
    async with httpx.AsyncClient(timeout=EMAIL_TIMEOUT_SECONDS) as http:
        app.state.http = http
        yield
    await engine.dispose()


app = FastAPI(title="Opzy API", version="0.1.0", lifespan=lifespan)

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
