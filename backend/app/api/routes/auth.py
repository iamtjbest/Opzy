import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
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
    SIGNUP_PER_EMAIL,
    SIGNUP_PER_IP,
    VERIFY_CONFIRM_PER_IP,
    VERIFY_RESEND_PER_EMAIL,
    VERIFY_RESEND_PER_IP,
)
from app.core.security import (
    MAX_PASSWORD_LENGTH,
    burn_password_check,
    create_access_token,
    hash_password,
    verify_password,
)
from app.email import EmailError, EmailMessage, EmailSender
from app.email_verification import (
    compose_account_exists_email,
    compose_already_verified_email,
    compose_verification_email,
    consume_verification_token,
    issue_verification_token,
)
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
    TokenResponse,
    UserRead,
    VerifyEmailConfirm,
    VerifyEmailResend,
    normalize_email,
)

router = APIRouter(prefix="/auth", tags=["auth"])

logger = logging.getLogger(__name__)

UNIQUE_VIOLATION = "23505"  # Postgres SQLSTATE

# Returned whether or not the address has an account, so the endpoint can't be used to
# find out which emails are registered.
RESET_REQUESTED = {"detail": "If that email has an account, a reset link is on its way."}
# Likewise for signup and for asking again for a verification link. Both answer this whether
# the address is new, already registered, or has never been seen.
SIGNUP_ACCEPTED = {"detail": "Check your email to finish setting up your Opzy account."}
VERIFY_RESENT = {"detail": "If that email needs confirming, a new link is on its way."}


@router.post("/signup", status_code=status.HTTP_202_ACCEPTED)
async def signup(
    body: SignupRequest,
    db: DbSession,
    limiter: Limiter,
    sender: EmailSenderDep,
    background: BackgroundTasks,
) -> dict:
    # Before anything hashes a password: Argon2 costs ~64 MB per call, so unthrottled
    # concurrent signups are a memory-exhaustion vector on their own.
    await limiter.enforce("signup", SIGNUP_PER_IP)
    # Signup now mails the address either way, so it also needs a per-address budget or it
    # becomes a way to bomb one inbox.
    await limiter.enforce("signup", SIGNUP_PER_EMAIL, kind="email", value=body.email)

    now = datetime.now(UTC)
    # Hashed before the branch, not inside it: both paths must cost the same Argon2 call,
    # or response timing tells the caller whether the address was already registered — the
    # exact thing this endpoint's identical response exists to hide.
    password_hash = hash_password(body.password)

    user = User(email=body.email, password_hash=password_hash)
    db.add(user)
    # Insert and catch the unique violation rather than checking first: a check-then-insert
    # lets two concurrent signups for the same email both pass the check.
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        # Only a unique violation means "email taken". Any other constraint (a CHECK on the
        # notification columns, say) is a bug here, and must not be swallowed.
        if getattr(exc.orig, "sqlstate", None) != UNIQUE_VIOLATION:
            raise
        # The address is spoken for. Tell its owner — in their inbox, which is the only
        # place entitled to know — and answer the caller exactly as for a new signup. The
        # existing account is not touched: no new password, no new token.
        existing = await db.scalar(select(User).where(User.email == body.email))
        if existing is not None:
            background.add_task(
                _send_quietly,
                sender,
                compose_account_exists_email(existing.email, get_settings().frontend_url),
            )
        return SIGNUP_ACCEPTED

    # id, created_at and the notification defaults are set by the database.
    await db.refresh(user)
    token = await issue_verification_token(db, user, now=now)
    # Queued rather than awaited, for the same timing reason as the hash above: a call out
    # to Resend takes seconds, and waiting for it here would make one path measurably
    # slower than the other.
    background.add_task(
        _send_quietly,
        sender,
        compose_verification_email(user.email, token, get_settings().frontend_url),
    )
    return SIGNUP_ACCEPTED


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


async def _send_quietly(sender: EmailSender, message: EmailMessage) -> None:
    try:
        await sender.send(message)
    except EmailError:
        # Never surfaced: a failed send must not make the response differ from the
        # unknown-email one. The user can ask again.
        logger.exception("Couldn't send an account email to %s", message.to)


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    body: PasswordResetRequest,
    db: DbSession,
    limiter: Limiter,
    sender: EmailSenderDep,
    background: BackgroundTasks,
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
        # Queued rather than awaited: sending is a call out to Resend that can take seconds,
        # and only a real account has one to make. Waiting for it here would make a
        # registered address measurably slower to answer than an unregistered one, which is
        # the enumeration this endpoint's identical response exists to prevent.
        background.add_task(_send_quietly, sender, message)

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


@router.post("/verify-email/confirm", response_model=TokenResponse)
async def confirm_email_verification(
    body: VerifyEmailConfirm, db: DbSession, limiter: Limiter
) -> TokenResponse:
    await limiter.enforce("verify-confirm", VERIFY_CONFIRM_PER_IP)

    user = await consume_verification_token(db, body.token, now=datetime.now(UTC))
    if user is None:
        # One message for unknown, spent and expired alike, exactly as the reset
        # equivalent: distinguishing them would say whether an account exists.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That confirmation link is invalid or has expired. Ask for a new one.",
        )

    # Clicking the link proves the address, which is at least as good as a password, so the
    # user lands logged in rather than being bounced to a login form.
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/verify-email/resend", status_code=status.HTTP_202_ACCEPTED)
async def resend_email_verification(
    body: VerifyEmailResend,
    db: DbSession,
    limiter: Limiter,
    sender: EmailSenderDep,
    background: BackgroundTasks,
) -> dict:
    await limiter.enforce("verify-resend", VERIFY_RESEND_PER_IP)
    await limiter.enforce(
        "verify-resend", VERIFY_RESEND_PER_EMAIL, kind="email", value=body.email
    )

    user = await db.scalar(select(User).where(User.email == body.email))
    if user is not None:
        frontend_url = get_settings().frontend_url
        if user.email_verified_at is None:
            token = await issue_verification_token(db, user, now=datetime.now(UTC))
            message = compose_verification_email(user.email, token, frontend_url)
        else:
            # No new token for an address that's already proven — there is nothing left to
            # prove, and minting one would be a live link nobody asked for.
            message = compose_already_verified_email(user.email, frontend_url)
        # Queued, not awaited: same enumeration-by-timing reasoning as the reset request.
        background.add_task(_send_quietly, sender, message)

    return VERIFY_RESENT
