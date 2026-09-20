import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, DbSession, EmailSenderDep, Limiter
from app.core.config import get_settings
from app.core.rate_limit import (
    LOGIN_PER_EMAIL,
    LOGIN_PER_IP,
    RESET_CONFIRM_PER_IP,
    RESET_REQUEST_PER_EMAIL,
    RESET_REQUEST_PER_IP,
    SIGNUP_PER_IP,
)
from app.core.security import (
    MAX_PASSWORD_LENGTH,
    burn_password_check,
    create_access_token,
    hash_password,
    verify_password,
)
from app.email import EmailError
from app.models import User
from app.password_reset import (
    compose_password_reset_email,
    consume_reset_token,
    issue_reset_token,
)
from app.schemas.auth import (
    PasswordResetConfirm,
    PasswordResetRequest,
    SignupRequest,
    SignupResponse,
    TokenResponse,
    UserRead,
    normalize_email,
)

router = APIRouter(prefix="/auth", tags=["auth"])

logger = logging.getLogger(__name__)

UNIQUE_VIOLATION = "23505"  # Postgres SQLSTATE

# Returned whether or not the address has an account, so the endpoint can't be used to
# find out which emails are registered.
RESET_REQUESTED = {"detail": "If that email has an account, a reset link is on its way."}


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


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    body: PasswordResetRequest, db: DbSession, limiter: Limiter, sender: EmailSenderDep
) -> dict:
    await limiter.enforce("reset-request", RESET_REQUEST_PER_IP)
    await limiter.enforce(
        "reset-request", RESET_REQUEST_PER_EMAIL, kind="email", value=body.email
    )

    user = await db.scalar(select(User).where(User.email == body.email))
    if user is not None:
        token = await issue_reset_token(db, user, now=datetime.now(UTC))
        message = compose_password_reset_email(
            user.email, token, get_settings().frontend_url
        )
        try:
            await sender.send(message)
        except EmailError:
            # Never surfaced: a failed send must not make this response differ from the
            # unknown-email one. The user can ask again.
            logger.exception("Couldn't send a password reset email")

    return RESET_REQUESTED


@router.post("/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_password_reset(
    body: PasswordResetConfirm, db: DbSession, limiter: Limiter
) -> None:
    await limiter.enforce("reset-confirm", RESET_CONFIRM_PER_IP)

    ok = await consume_reset_token(db, body.token, body.new_password, now=datetime.now(UTC))
    if not ok:
        # One message for unknown, spent and expired alike: distinguishing them would say
        # whether a token — and so an account — exists.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That reset link is invalid or has expired. Request a new one.",
        )
