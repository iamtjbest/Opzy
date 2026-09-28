import pytest
from pydantic import ValidationError

from app.core.config import Settings

DB_URL = "postgresql://user:pass@127.0.0.1:55432/opzy"
STRONG_SECRET = "s" * 32

RESEND = {
    "EMAIL_BACKEND": "resend",
    "RESEND_API_KEY": "re_test",
    "EMAIL_FROM": "Opzy <hello@example.com>",
}
# Everything a deployed environment needs on top of the database and JWT secret.
DEPLOYED = {**RESEND, "INTERNAL_API_SECRET": "i" * 32}


def build(**overrides) -> Settings:
    return Settings(DATABASE_URL=DB_URL, JWT_SECRET=STRONG_SECRET, **overrides)


def test_defaults_to_development():
    assert build().environment == "development"


@pytest.mark.parametrize("environment", ["development", "staging", "production"])
def test_known_environments_accepted(environment):
    assert build(ENVIRONMENT=environment, **DEPLOYED).environment == environment


@pytest.mark.parametrize("environment", ["prod", "Production", "live", ""])
def test_unknown_environment_rejected(environment):
    # A typo used to fall through to the lenient branch and skip the secret check.
    with pytest.raises(ValidationError):
        build(ENVIRONMENT=environment)


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_weak_secret_rejected_when_deployed(environment):
    with pytest.raises(ValidationError):
        Settings(DATABASE_URL=DB_URL, JWT_SECRET="too-short", ENVIRONMENT=environment)


def test_weak_secret_allowed_in_development():
    assert Settings(DATABASE_URL=DB_URL, JWT_SECRET="dev", ENVIRONMENT="development")


def test_empty_secret_always_rejected():
    # .env.example ships JWT_SECRET= empty; this must fail at startup, not at first login.
    with pytest.raises(ValidationError):
        Settings(DATABASE_URL=DB_URL, JWT_SECRET="", ENVIRONMENT="development")


def test_missing_secret_rejected(monkeypatch):
    # Both sources have to go: the .env file and any real JWT_SECRET in the environment
    # (CI sets one), otherwise this passes for the wrong reason.
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(ValidationError):
        Settings(DATABASE_URL=DB_URL, _env_file=None)


def test_email_backend_defaults_to_console():
    assert build(EMAIL_BACKEND="console").email_backend == "console"


@pytest.mark.parametrize("missing", ["RESEND_API_KEY", "EMAIL_FROM"])
def test_resend_needs_a_key_and_a_sender(missing):
    with pytest.raises(ValidationError):
        build(**{**RESEND, missing: ""})


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_console_email_rejected_when_deployed(environment):
    # The console backend only logs, so a deployed app would silently send nothing.
    with pytest.raises(ValidationError):
        build(ENVIRONMENT=environment, EMAIL_BACKEND="console")


@pytest.mark.parametrize("environment", ["staging", "production"])
@pytest.mark.parametrize("secret", [None, "too-short"])
def test_internal_secret_required_when_deployed(environment, secret):
    # Without it every browser's requests share the Next.js server's rate-limit bucket.
    extra = {} if secret is None else {"INTERNAL_API_SECRET": secret}
    with pytest.raises(ValidationError):
        build(ENVIRONMENT=environment, **RESEND, **extra)


def test_internal_secret_optional_in_development():
    assert build().internal_api_secret is None


@pytest.mark.parametrize(
    ("environment", "deployed"), [("development", False), ("staging", True), ("production", True)]
)
def test_is_deployed(environment, deployed):
    extra = DEPLOYED if deployed else {}
    assert build(ENVIRONMENT=environment, **extra).is_deployed is deployed
