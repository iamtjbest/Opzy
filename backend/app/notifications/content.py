"""The email telling a user about their new matches."""

from datetime import date
from html import escape

from app.email import EmailMessage
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
        link = f"{base}/opportunities/{opportunity.id}"
        deadline = _deadline(opportunity.deadline)
        text_items.append(f"{heading}\n{deadline}\n{match.explanation}\n{link}")
        html_items.append(
            f'<li><a href="{escape(link)}"><strong>{escape(heading)}</strong></a><br>'
            f"{escape(deadline)}<br>{escape(match.explanation)}</li>"
        )

    hidden = len(matches) - MAX_ITEMS_PER_EMAIL
    more = [f"And {hidden} more on your feed: {base}/feed"] if hidden > 0 else []
    footer = (
        f"You get these emails {HOW_OFTEN[cadence]}. "
        f"Change that or turn them off: {base}/settings"
    )

    text = "\n\n".join([intro, *text_items, *more, footer])
    html = (
        f"<p>{escape(intro)}</p><ul>{''.join(html_items)}</ul>"
        + "".join(f"<p>{escape(line)}</p>" for line in more)
        + f"<p>{escape(footer)}</p>"
    )
    return EmailMessage(to=to, subject=subject, text=text, html=html)
