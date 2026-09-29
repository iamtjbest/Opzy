"""Shared chrome for every transactional email, so they read as one product instead of
bare paragraphs.

Colors and type follow docs/DESIGN_SYSTEM.md exactly, so these emails match the web app
rather than inventing their own palette. If that doc's colors change, update the
constants below and every email picks it up.

Email HTML has to use inline styles and table layout, no <style> blocks and no
flexbox/grid: most inboxes (Gmail among them) strip a <style> tag or ignore modern CSS.
Everything here is deliberately old-fashioned for that reason. The Google Fonts <link> is
a nice-to-have some clients honor (Apple Mail, some webmail) — the fallback stack carries
everyone else.
"""

NAVY = "#14213D"  # Primary/Navy — wordmark, headings, primary buttons
BLUE = "#2F6FED"  # Primary/Blue — links, secondary interactive elements
EMERALD = "#10B981"  # Success/Emerald — match confirmation only, per the design system
AMBER = "#F59E0B"  # Warning/Amber — deadline approaching
INK = "#1F2430"  # Neutral/Ink — body text
SLATE = "#6B7280"  # Neutral/Slate — secondary/muted text
BORDER = "#E2E5EA"  # Neutral/Border
MIST = "#F3F5F8"  # Neutral/Mist — page background
WHITE = "#FFFFFF"

BRAND = "Opzy"
FONT = (
    "font-family:'Bricolage Grotesque',-apple-system,Segoe UI,Roboto,Helvetica,Arial,"
    "sans-serif;"
)
FONT_IMPORT = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;'
    '700;800&display=swap" rel="stylesheet">'
)


def button(label: str, href: str) -> str:
    """A single call-to-action link styled to look like a button in every inbox."""
    return (
        f'<a href="{href}" style="display:inline-block;background:{NAVY};'
        f"color:#ffffff;text-decoration:none;padding:12px 22px;border-radius:8px;"
        f'{FONT}font-size:14px;font-weight:700;letter-spacing:0.2px;">{label}</a>'
    )


def link(label: str, href: str) -> str:
    """An inline text link in the brand's interactive color, for secondary actions."""
    return f'<a href="{href}" style="color:{BLUE};text-decoration:underline;">{label}</a>'


def pill(text: str, tone: str = "neutral") -> str:
    """A small rounded badge. `tone` picks the color: 'success' for a confirmed match
    (the design system reserves Emerald for exactly that), 'warning' for a deadline
    that's close, 'neutral' for anything informational."""
    colors = {
        "neutral": (MIST, SLATE),
        "success": ("#E7F7EF", "#0B7A54"),
        "warning": ("#FEF3E2", "#B4750B"),
    }
    bg, fg = colors.get(tone, colors["neutral"])
    return (
        f'<span style="display:inline-block;background:{bg};color:{fg};'
        f"padding:2px 10px;border-radius:999px;font-size:12px;font-weight:700;"
        f'{FONT}">{text}</span>'
    )


def wrap(body_html: str, *, preheader: str = "") -> str:
    """Wrap already-escaped inner HTML in the shared card/header/footer chrome."""
    hidden_preheader = (
        f'<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{preheader}</div>'
        if preheader
        else ""
    )
    return (
        "<!doctype html><html><head>"
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        f"{FONT_IMPORT}"
        "</head>"
        f'<body style="margin:0;padding:0;background:{MIST};{FONT}">'
        f"{hidden_preheader}"
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
        f'style="background:{MIST};padding:32px 12px;"><tr><td align="center">'
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
        f'style="max-width:520px;background:{WHITE};border-radius:14px;'
        f'border:1px solid {BORDER};">'
        '<tr><td style="padding:28px 32px 4px 32px;">'
        f'<div style="font-size:20px;font-weight:800;color:{NAVY};letter-spacing:-0.3px;'
        f'{FONT}">{BRAND}</div>'
        "</td></tr>"
        f'<tr><td style="padding:16px 32px 4px 32px;color:{INK};font-size:15px;'
        f'line-height:1.6;{FONT}">{body_html}</td></tr>'
        '<tr><td style="padding:24px 32px 28px 32px;">'
        f'<div style="height:1px;background:{BORDER};margin:0 0 16px 0;"></div>'
        f'<div style="color:{SLATE};font-size:12px;line-height:1.5;{FONT}">'
        f"You're receiving this because of activity on your {BRAND} account."
        "</div></td></tr>"
        "</table></td></tr></table>"
        "</body></html>"
    )


def card(inner_html: str) -> str:
    """A bordered card for one list item (an opportunity, say) inside the body."""
    return (
        f'<div style="border:1px solid {BORDER};background:{WHITE};border-radius:10px;'
        f'padding:14px 16px;margin:0 0 12px 0;">{inner_html}</div>'
    )


def muted(text: str) -> str:
    return f'<span style="color:{SLATE};font-size:13px;{FONT}">{text}</span>'
