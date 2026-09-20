from app.core.security import RESET_TOKEN_TTL, generate_reset_token, hash_reset_token
from app.password_reset import compose_password_reset_email


def test_tokens_are_unguessable_and_distinct():
    tokens = {generate_reset_token() for _ in range(100)}

    assert len(tokens) == 100
    # token_urlsafe(32) is 32 random bytes, base64url encoded.
    assert all(len(token) >= 40 for token in tokens)


def test_hash_is_stable_and_is_not_the_token():
    token = generate_reset_token()

    assert hash_reset_token(token) == hash_reset_token(token)
    assert token not in hash_reset_token(token)
    assert len(hash_reset_token(token)) == 64


def test_token_lives_for_an_hour():
    assert RESET_TOKEN_TTL.total_seconds() == 3600


def test_reset_email_carries_a_working_link():
    message = compose_password_reset_email(
        "ada@example.com", "tok-123", "https://opzy.app/"
    )

    assert message.to == "ada@example.com"
    link = "https://opzy.app/reset-password?token=tok-123"
    assert link in message.text
    assert link in message.html
    assert "1 hour" in message.text


def test_reset_email_percent_encodes_the_token():
    # A raw "&" would end the query parameter early and truncate the token.
    message = compose_password_reset_email("ada@example.com", "a&b", "https://opzy.app")

    assert "token=a%26b" in message.text
    assert "token=a%26b" in message.html
    assert "token=a&b" not in message.html
