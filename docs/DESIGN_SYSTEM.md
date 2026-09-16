# Design System: Opzy

**Status:** v1. Color roles, typography, and logo mark are all settled.
**Font:** Bricolage Grotesque (Google Fonts, SIL Open Font License). Free for commercial
use, no license to track down. It's a variable font with weight and optical-size axes,
so it can carry both headlines and body text without needing a second family.

---

## Color styles

Create these as Figma **Color Styles**, named exactly as shown so the group/name structure
shows up as folders in the Figma styles panel.

| Figma style name | Hex | Usage |
|---|---|---|
| `Primary/Navy` | `#14213D` | Primary text, wordmark, primary buttons, nav/header |
| `Primary/Blue` | `#2F6FED` | Interactive elements: links, active states, secondary buttons, selected tabs |
| `Success/Emerald` | `#10B981` | Match/eligibility confirmation only: score badges, "eligible" tags, saved confirmations. Not for logo or general decoration. |
| `Warning/Amber` | `#F59E0B` | Deadline approaching, soft warnings |
| `Danger/Red` | `#DC2626` | Errors, expired/ineligible states |
| `Neutral/Ink` | `#1F2430` | Body text alternative to Navy where less emphasis is wanted |
| `Neutral/Slate` | `#6B7280` | Secondary/muted text: timestamps, helper text, placeholders |
| `Neutral/Border` | `#E2E5EA` | Dividers, card borders, input borders |
| `Neutral/Mist` | `#F3F5F8` | Page background, subtle section backgrounds |
| `Neutral/White` | `#FFFFFF` | Surface/card background |

**Usage rule to carry into the UI (not just the logo):** Emerald means "this is a confirmed
good match or success state," nowhere else. If it starts showing up as decoration, it stops
meaning anything, and given how much the validation data emphasized trust and legitimacy,
that signal needs to stay reliable.

---

## Text styles

Base font: Bricolage Grotesque (Bold for headings/buttons, Regular for body/caption).

| Figma style name | Weight | Size | Line height | Usage |
|---|---|---|---|---|
| `Display/Large` | Bold | 40px | 48px | Landing hero, onboarding welcome |
| `Heading/H1` | Bold | 28px | 34px | Page titles |
| `Heading/H2` | Bold | 22px | 28px | Section headers |
| `Heading/H3` | Bold | 18px | 24px | Card titles, opportunity title in feed |
| `Body/Large` | Regular | 16px | 24px | Primary reading text, opportunity descriptions |
| `Body/Regular` | Regular | 14px | 20px | Secondary text, form labels |
| `Caption` | Regular | 12px | 16px | Timestamps, tags, metadata |
| `Button/Label` | Bold | 14px | 20px | Button text, letter-spacing 0.2px |
| `Numeric/Badge` | Bold | 13px | 16px | Match-score badges, e.g. "92% Match" |

**One thing to watch:** at body-text sizes, use Bricolage Grotesque's lighter/text optical
grade rather than its heavier display cut, or paragraphs will read heavier than intended.
Fine as-is for headings, buttons, and badges; worth checking on FAQ answers and opportunity
descriptions specifically.

---

## Logo

Favicon and app icon mark: navy rounded square (`Primary/Navy`) with a white lowercase "z"
in Bricolage Grotesque ExtraBold, centered. Built off the "z" in Opzy rather than an "O"
shape, since OPay's identity is built around a green "O" loop mark and the shared Nigerian
audience made that collision worth avoiding. Master file lives at 512px with a 32px favicon
preview alongside it in the Figma file.
