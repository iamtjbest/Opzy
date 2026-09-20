from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, DbSession, Limiter
from app.core.rate_limit import LOGIN_PER_EMAIL, LOGIN_PER_IP, SIGNUP_PER_IP
from app.core.security import (
    MAX_PASSWORD_LENGTH,
    burn_password_check,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    TokenResponse,
    UserRead,
    normalize_email,
)

router = APIRouter(prefix="/auth", tags=["auth"])

UNIQUE_VIOLATION = "23505"  # Postgres SQLSTATE


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=SignupResponse)
async def signup(body: SignupRequest, db: DbSession, limiter: Limiter) -> SignupResponse:
    # Before anything hashes a password: Argon2 costs ~64 MB per call, so unthrottled
    # concurrent signups are a memory-exhaustion vector on their own.
    await limiter.enforce("signup", SIGNUP_PER_IP)

    user = User(email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    # Insert and catch the unique violation rather than checking first: a check-then-insert
    # lets two concurrent signups for the same email both pass the check.
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        # Only a unique violation means "email taken". Any other constraint (a CHECK on the
        # notification columns, say) is a bug here, and must not be reported as a conflict.
        if getattr(exc.orig, "sqlstate", None) != UNIQUE_VIOLATION:
            raise
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from None
    # id, created_at and the notification defaults are set by the database.
    await db.refresh(user)

    return SignupResponse(
        access_token=create_access_token(user.id), user=UserRead.model_validate(user)
    )


# Form-encoded (OAuth2 password flow) so the "Authorize" button in /docs works.
# The form's `username` field carries the email.
@router.post("/login", response_model=TokenResponse)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
    limiter: Limiter,
) -> TokenResponse:
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = normalize_email(form.username)
    await limiter.enforce("login", LOGIN_PER_IP)
    await limiter.enforce("login", LOGIN_PER_EMAIL, kind="email", value=email)

    # Signup can never have stored a longer password, so skip hashing attacker-sized input.
    if len(form.password) > MAX_PASSWORD_LENGTH:
        raise invalid

    user = await db.scalar(select(User).where(User.email == email))
    if user is None:
        burn_password_check(form.password)
        raise invalid
    if not verify_password(form.password, user.password_hash):
        raise invalid

    # The attempt was legitimate, so it shouldn't count against this account's budget.
    await limiter.give_back("login", LOGIN_PER_EMAIL, kind="email", value=email)

    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser) -> User:
    return user
