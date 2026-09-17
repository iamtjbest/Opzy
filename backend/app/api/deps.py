from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import decode_access_token
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: DbSession
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = decode_access_token(token)
    except jwt.InvalidTokenError:
        raise credentials_error from None

    # Tokens are stateless, so a deleted user's token stays valid until expiry; this lookup
    # is what shuts them out.
    user = await db.get(User, user_id)
    if user is None:
        raise credentials_error
    return user


# Use this on any route that needs a logged-in user: `def route(user: CurrentUser): ...`
CurrentUser = Annotated[User, Depends(get_current_user)]
