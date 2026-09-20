import uuid
from datetime import UTC, datetime
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.config import get_settings
from app.core.db import get_db
from app.core.rate_limit import RateLimiter, client_ip
from app.core.security import decode_access_token_claims
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_rate_limiter(request: Request, db: DbSession) -> RateLimiter:
    return RateLimiter(db, client_ip(request, get_settings()))


Limiter = Annotated[RateLimiter, Depends(get_rate_limiter)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: DbSession
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        claims = decode_access_token_claims(token)
        user_id = uuid.UUID(claims["sub"])
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise credentials_error from None

    # Tokens are stateless, so a deleted user's token stays valid until expiry; this lookup
    # is what shuts them out.
    user = await db.get(User, user_id)
    if user is None:
        raise credentials_error

    # A password change retires every token minted before it, so resetting a password
    # actually locks out whoever prompted the reset.
    if user.password_changed_at is not None:
        issued_at = datetime.fromtimestamp(claims["iat"], tz=UTC)
        if issued_at < user.password_changed_at:
            raise credentials_error
    return user


# Use this on any route that needs a logged-in user: `def route(user: CurrentUser): ...`
CurrentUser = Annotated[User, Depends(get_current_user)]
