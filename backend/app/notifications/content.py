"""The email telling a user about their new matches."""

from datetime import date
from html import escape

from app.email import EmailMessage
from app.email_template import BLUE, INK, SLATE, card, muted, pill, wrap
from app.matching.feed import Match
from app.models.base import DAILY, INSTANT, WEEKLY

# Past this the email stops being skimmable; the rest are waiting on the feed.
MAX_ITEMS_PER_EMAIL = 10

HOW_OFTEN = {
    INSTANT: "as soon as we find a strong match",
    DAILY: "at most once a day",
    WEEKLY: "at most once a week",
}


def _deadline(deadline: date | None) -> str:
    if deadline is None:
        return "Rolling deadline"
    return f"Deadline: {deadline.day} {deadline:%b %Y}"


def compose_match_email(
    to: str, matches: list[Match], cadence: str, frontend_url: str
) -> EmailMessage:
    """One email listing `matches` (never empty) in the order given, best first."""
    base = frontend_url.rstrip("/")
    if len(matches) == 1:
        subject = f"New match: {matches[0].opportunity.title}"
    else:
        subject = f"{len(matches)} new opportunities picked for you"

    intro = "New opportunities that fit your profile:"
    text_items: list[str] = []
    html_items: list[str] = []
    for match in matches[:MAX_ITEMS_PER_EMAIL]:
        opportunity = match.opportunity
        heading = opportunity.title
        if opportunity.organization:
            heading += f" — {opportunity.organization}"
        opp_link = f"{base}/opportunities/{opportunity.id}"
        deadline = _deadline(opportunity.deadline)
        text_items.append(
            f"{heading} ({match.score}% match)\n{deadline}\n{match.explanation}\n{opp_link}"
        )
        html_items.append(
            card(
                f'<a href="{escape(opp_link)}" style="color:{INK};text-decoration:none;'
                f'font-weight:700;font-size:15px;">{escape(heading)}</a><br>'
                f'<div style="margin:6px 0;">'
                f'{pill(f"{match.score}% match", tone="success")} '
                f'{pill(escape(deadline))}</div>'
                f"{muted(escape(match.explanation))}"
            )
        )

    hidden = len(matches) - MAX_ITEMS_PER_EMAIL
    feed_link = f"{base}/feed"
    settings_link = f"{base}/settings"
    more = [f"And {hidden} more on your feed: {feed_link}"] if hidden > 0 else []
    footer_note = f"You get these emails {HOW_OFTEN[cadence]}. Change that or turn them off:"
    footer = f"{footer_note} {settings_link}"

    text = "\n\n".join([intro, *text_items, *more, footer])
    more_html = (
        f'<p style="margin:4px 0 16px 0;">And {hidden} more on '
        f'<a href="{escape(feed_link)}" style="color:{BLUE};">your feed</a>.</p>'
        if hidden > 0
        else ""
    )
    html_body = (
        f'<p style="margin:0 0 16px 0;">{escape(intro)}</p>'
        + "".join(html_items)
        + more_html
        + f'<p style="margin:8px 0 0 0;">{muted(escape(footer_note))} '
        f'<a href="{escape(settings_link)}" style="color:{SLATE};text-decoration:underline;">'
        f"Notification settings</a></p>"
    )
    html = wrap(html_body, preheader=intro)
    return EmailMessage(to=to, subject=subject, text=text, html=html)
