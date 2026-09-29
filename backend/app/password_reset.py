"""Issuing and spending password reset tokens."""

from datetime import datetime
from html import escape
from urllib.parse import quote

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    RESET_TOKEN_TTL,
    generate_url_token,
    hash_password,
    hash_url_token,
)
from app.email import EmailMessage
from app.email_template import button, muted, wrap
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
    safe_link = escape(link, quote=True)
    cta = button("Choose a new password", safe_link)
    footnote = muted(
        "The link works once and expires in 1 hour. If this wasn't you, ignore this "
        "email — your password hasn't changed."
    )
    body = (
        '<p style="margin:0 0 18px 0;">Someone asked to reset the password for this '
        "account.</p>"
        f'<p style="margin:0 0 18px 0;">{cta}</p>'
        f'<p style="margin:0;">{footnote}</p>'
    )
    html = wrap(body, preheader="Reset your password")
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
    token = generate_url_token()
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=hash_url_token(token),
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
    # Spent in the same statement that checks it's spendable. A read-then-write would let
    # two requests carrying one token both see it unused and both go through; here the
    # second waits on the row lock, then finds used_at set and matches nothing.
    user_id = await db.scalar(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.token_hash == hash_url_token(token),
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > now,
        )
        .values(used_at=now)
        .returning(PasswordResetToken.user_id)
    )
    if user_id is None:
        return False

    user = await db.get(User, user_id)
    if user is None:
        await db.rollback()
        return False

    user.password_hash = hash_password(new_password)
    user.password_changed_at = now
    # Any other link already in the user's inbox dies with this one.
    await db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    await db.commit()
    return True
