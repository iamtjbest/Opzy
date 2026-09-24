"""Issuing and spending email verification tokens.

A deliberate mirror of `app/password_reset.py`: same table shape, same single-use and
expiry rules, same "one answer for every failure" contract. The two differ only in what
spending a token does — a reset sets a password, a verification stamps `email_verified_at`
and hands the user back so the caller can log them straight in.
"""

from datetime import datetime
from html import escape
from urllib.parse import quote

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    VERIFICATION_TOKEN_TTL,
    generate_url_token,
    hash_url_token,
)
from app.email import EmailMessage
from app.models import EmailVerificationToken, User

VERIFY_SUBJECT = "Confirm your email address"
EXISTS_SUBJECT = "You already have an Opzy account"


def compose_verification_email(to: str, token: str, frontend_url: str) -> EmailMessage:
    base = frontend_url.rstrip("/")
    link = f"{base}/verify-email?token={quote(token, safe='')}"
    text = (
        "Welcome to Opzy. Confirm this address to finish setting up your account:\n\n"
        f"{link}\n\n"
        "The link works once and expires in 24 hours. If you didn't sign up for Opzy, "
        "ignore this email — no account will be created without this step."
    )
    html = (
        "<p>Welcome to Opzy. Confirm this address to finish setting up your account.</p>"
        f'<p><a href="{escape(link, quote=True)}">Confirm my email</a></p>'
        "<p>The link works once and expires in 24 hours. If you didn't sign up for Opzy, "
        "ignore this email — no account will be created without this step.</p>"
    )
    return EmailMessage(to=to, subject=VERIFY_SUBJECT, text=text, html=html)


def compose_account_exists_email(to: str, frontend_url: str) -> EmailMessage:
    """Sent when someone signs up with an address that already has an account.

    Carries no token and no link that could create or change anything. Signup answers the
    same way for a new and an existing address, so this email is the only place the
    difference shows — in the one inbox that is entitled to know.
    """
    base = frontend_url.rstrip("/")
    text = (
        "Someone tried to sign up for Opzy with this address, which already has an "
        f"account. Nothing has changed.\n\n"
        f"Log in: {base}/login\n"
        f"Forgot your password? {base}/forgot-password\n\n"
        "If this wasn't you, you can safely ignore this email."
    )
    html = (
        "<p>Someone tried to sign up for Opzy with this address, which already has an "
        "account. Nothing has changed.</p>"
        f'<p><a href="{escape(base + "/login", quote=True)}">Log in</a> · '
        f'<a href="{escape(base + "/forgot-password", quote=True)}">Forgot your password?'
        "</a></p>"
        "<p>If this wasn't you, you can safely ignore this email.</p>"
    )
    return EmailMessage(to=to, subject=EXISTS_SUBJECT, text=text, html=html)


def compose_already_verified_email(to: str, frontend_url: str) -> EmailMessage:
    """Sent when a verified account asks for another verification link."""
    base = frontend_url.rstrip("/")
    text = (
        "This address is already confirmed, so there's nothing left to do.\n\n"
        f"Log in: {base}/login"
    )
    html = (
        "<p>This address is already confirmed, so there's nothing left to do.</p>"
        f'<p><a href="{escape(base + "/login", quote=True)}">Log in</a></p>'
    )
    return EmailMessage(to=to, subject=EXISTS_SUBJECT, text=text, html=html)


async def issue_verification_token(db: AsyncSession, user: User, *, now: datetime) -> str:
    """Retire this user's outstanding tokens, mint a new one, return the plaintext."""
    await db.execute(
        update(EmailVerificationToken)
        .where(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    token = generate_url_token()
    db.add(
        EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_url_token(token),
            expires_at=now + VERIFICATION_TOKEN_TTL,
        )
    )
    await db.commit()
    return token


async def consume_verification_token(
    db: AsyncSession, token: str, *, now: datetime
) -> User | None:
    """Spend a token and mark the address verified. None if the token can't be used.

    Unknown, already-spent and expired tokens all return None, so the caller can answer
    with a single message and leak nothing about which it was — in particular, nothing
    about whether an account exists.
    """
    row = await db.scalar(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == hash_url_token(token)
        )
    )
    if row is None or row.used_at is not None or row.expires_at <= now:
        return None

    user = await db.get(User, row.user_id)
    if user is None:
        return None

    # Re-verifying an already-verified account keeps the original instant: the address was
    # proven then, and moving the stamp forward would lose that.
    if user.email_verified_at is None:
        user.email_verified_at = now
    row.used_at = now
    # Any other link already in the user's inbox dies with this one.
    await db.execute(
        update(EmailVerificationToken)
        .where(
            EmailVerificationToken.user_id == row.user_id,
            EmailVerificationToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    await db.commit()
    return user
