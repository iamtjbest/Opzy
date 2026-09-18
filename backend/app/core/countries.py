"""ISO 3166 country codes: the one format for nationality and eligible countries."""

import pycountry


def is_country(code: str) -> bool:
    """True for an uppercase ISO 3166 alpha-2 code, e.g. "NG"."""
    return len(code) == 2 and code.isupper() and pycountry.countries.get(alpha_2=code) is not None


def country_name(code: str) -> str:
    """The name to show a person: "Nigeria", "Tanzania" (not "Tanzania, United Republic of")."""
    country = pycountry.countries.get(alpha_2=code)
    return getattr(country, "common_name", country.name)
