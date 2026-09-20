"""Issuing and spending password reset tokens."""

from datetime import datetime
from html import escape
from urllib.parse import quote

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    RESET_TOKEN_TTL,
    generate_reset_token,
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
