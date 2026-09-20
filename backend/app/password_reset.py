"""Issuing and spending password reset tokens."""

from datetime import datetime
from html import escape
from urllib.parse import quote

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    RESET_TOKEN_TTL,
    generate_reset_token,
    hash_password,
    hash_reset_token,
)
from app.email import EmailMessage
from app.models import PasswordResetToken, User

SUBJECT = "Reset your Opzy password"


def compose_password_reset_email(to: str, token: str, frontend_url: str) -> EmailMessage:
    link = f"{frontend_url.rstrip('/')}/reset-password?token={quote(token, safe='')}"
    text = (
        "Someone asked to reset the password for this Opzy account.\n\n"
        f"{link}\n\n"
        "The link works once and expires in 1 hour. If this wasn't you, ignore this "
        "email — your password hasn't changed."
    )
    html = (
        "<p>Someone asked to reset the password for this Opzy account.</p>"
        f'<p><a href="{escape(link, quote=True)}">Choose a new password</a></p>'
        "<p>The link works once and expires in 1 hour. If this wasn't you, ignore this "
        "email — your password hasn't changed.</p>"
    )
    return EmailMessage(to=to, subject=SUBJECT, text=text, html=html)


async def issue_reset_token(db: AsyncSession, user: User, *, now: datetime) -> str:
    """Retire this user's outstanding tokens, mint a new one, return the plaintext."""
    await db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    token = generate_reset_token()
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=hash_reset_token(token),
            expires_at=now + RESET_TOKEN_TTL,
        )
    )
    await db.commit()
    return token


async def consume_reset_token(
    db: AsyncSession, token: str, new_password: str, *, now: datetime
) -> bool:
    """Spend a token and set the new password. False if the token can't be used.

    Unknown, already-spent and expired tokens all return False, so the caller can answer
    with a single message and leak nothing about which it was.
    """
    row = await db.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == hash_reset_token(token)
        )
    )
    if row is None or row.used_at is not None or row.expires_at <= now:
        return False

    user = await db.get(User, row.user_id)
    if user is None:
        return False

    user.password_hash = hash_password(new_password)
    user.password_changed_at = now
    row.used_at = now
    # Any other link already in the user's inbox dies with this one.
    await db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == row.user_id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    await db.commit()
    return True
