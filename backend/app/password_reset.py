"""Issuing and spending password reset tokens."""

from html import escape
from urllib.parse import quote

from app.email import EmailMessage

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
