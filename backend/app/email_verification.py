"""Issuing and spending email verification tokens.

A deliberate mirror of `app/password_reset.py`: same table shape, same single-use and
expiry rules, same "one answer for every failure" contract. The two differ only in what
spending a token does — a reset sets a password, a verification stamps `email_verified_at`
and hands the user back so the caller can log them straight in.
"""

from datetime import datetime
from html import escape
from urllib.parse import quote

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    VERIFICATION_TOKEN_TTL,
    generate_url_token,
    hash_url_token,
)
from app.email import EmailMessage
from app.email_template import button, link, muted, wrap
from app.models import EmailVerificationToken, User

VERIFY_SUBJECT = "Confirm your email address"
EXISTS_SUBJECT = "You already have an Opzy account"


def compose_verification_email(to: str, token: str, frontend_url: str) -> EmailMessage:
    base = frontend_url.rstrip("/")
    verify_link = f"{base}/verify-email?token={quote(token, safe='')}"
    text = (
        "Welcome to Opzy. Confirm this address to finish setting up your account:\n\n"
        f"{verify_link}\n\n"
        "The link works once and expires in 24 hours. If you didn't sign up for Opzy, "
        "ignore this email — no account will be created without this step."
    )
    cta = button("Confirm my email", escape(verify_link, quote=True))
    footnote = muted(
        "The link works once and expires in 24 hours. If you didn't sign up for Opzy, "
        "ignore this email — no account will be created without this step."
    )
    body = (
        '<p style="margin:0 0 18px 0;">Welcome to Opzy. Confirm this address to finish '
        "setting up your account.</p>"
        f'<p style="margin:0 0 18px 0;">{cta}</p>'
        f'<p style="margin:0;">{footnote}</p>'
    )
    html = wrap(body, preheader="Confirm your email to finish setting up Opzy")
    return EmailMessage(to=to, subject=VERIFY_SUBJECT, text=text, html=html)


def compose_account_exists_email(to: str, frontend_url: str) -> EmailMessage:
    """Sent when someone signs up with an address that already has an account.

    Carries no token and no link that could create or change anything. Signup answers the
    same way for a new and an existing address, so this email is the only place the
    difference shows — in the one inbox that is entitled to know.
    """
    base = frontend_url.rstrip("/")
    login_link = f"{base}/login"
    forgot_link = f"{base}/forgot-password"
    text = (
        "Someone tried to sign up for Opzy with this address, which already has an "
        f"account. Nothing has changed.\n\n"
        f"Log in: {login_link}\n"
        f"Forgot your password? {forgot_link}\n\n"
        "If this wasn't you, you can safely ignore this email."
    )
    cta = button("Log in", escape(login_link, quote=True))
    secondary = link("Forgot your password?", escape(forgot_link, quote=True))
    footnote = muted("If this wasn't you, you can safely ignore this email.")
    body = (
        '<p style="margin:0 0 18px 0;">Someone tried to sign up for Opzy with this '
        "address, which already has an account. Nothing has changed.</p>"
        f'<p style="margin:0 0 12px 0;">{cta}</p>'
        f'<p style="margin:0 0 18px 0;">{secondary}</p>'
        f'<p style="margin:0;">{footnote}</p>'
    )
    html = wrap(body, preheader="You already have an Opzy account")
    return EmailMessage(to=to, subject=EXISTS_SUBJECT, text=text, html=html)


def compose_already_verified_email(to: str, frontend_url: str) -> EmailMessage:
    """Sent when a verified account asks for another verification link."""
    base = frontend_url.rstrip("/")
    login_link = f"{base}/login"
    text = (
        "This address is already confirmed, so there's nothing left to do.\n\n"
        f"Log in: {login_link}"
    )
    cta = button("Log in", escape(login_link, quote=True))
    body = (
        '<p style="margin:0 0 18px 0;">This address is already confirmed, so there\'s '
        "nothing left to do.</p>"
        f'<p style="margin:0;">{cta}</p>'
    )
    html = wrap(body, preheader="Your email is already confirmed")
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
    # Checked and spent in one statement, as in `consume_reset_token`: two requests with one
    # token can't both see it unused.
    user_id = await db.scalar(
        update(EmailVerificationToken)
        .where(
            EmailVerificationToken.token_hash == hash_url_token(token),
            EmailVerificationToken.used_at.is_(None),
            EmailVerificationToken.expires_at > now,
        )
        .values(used_at=now)
        .returning(EmailVerificationToken.user_id)
    )
    if user_id is None:
        return None

    user = await db.get(User, user_id)
    if user is None:
        await db.rollback()
        return None

    # Re-verifying an already-verified account keeps the original instant: the address was
    # proven then, and moving the stamp forward would lose that.
    if user.email_verified_at is None:
        user.email_verified_at = now
    # Any other link already in the user's inbox dies with this one.
    await db.execute(
        update(EmailVerificationToken)
        .where(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    await db.commit()
    return user
