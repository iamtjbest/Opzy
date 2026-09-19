import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_is_not_plaintext_and_verifies():
    hashed = hash_password("correct horse battery")
    assert hashed != "correct horse battery"
    assert "correct horse battery" not in hashed
    assert verify_password("correct horse battery", hashed)


def test_wrong_password_fails():
    assert not verify_password("wrong", hash_password("correct horse battery"))


def test_same_password_hashes_differently():
    assert hash_password("same-password") != hash_password("same-password")


def test_token_round_trip():
    user_id = uuid.uuid4()
    assert decode_access_token(create_access_token(user_id)) == user_id


def test_expired_token_rejected():
    settings = get_settings()
    past = datetime.now(UTC) - timedelta(minutes=5)
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "iat": past, "exp": past, "type": "access"},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)


def test_tampered_token_rejected():
    token = create_access_token(uuid.uuid4())
    header, payload, signature = token.split(".")
    flipped = ("A" if signature[0] != "A" else "B") + signature[1:]
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(f"{header}.{payload}.{flipped}")


def test_token_signed_with_other_secret_rejected():
    token = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "exp": datetime.now(UTC) + timedelta(minutes=5),
            "type": "access",
        },
        "some-other-secret-that-is-long-enough-to-use",
        algorithm="HS256",
    )
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)


def test_unsigned_token_rejected():
    token = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "exp": datetime.now(UTC) + timedelta(minutes=5),
            "type": "access",
        },
        None,
        algorithm="none",
    )
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)


def test_non_uuid_subject_rejected():
    settings = get_settings()
    token = jwt.encode(
        {
            "sub": "not-a-uuid",
            "exp": datetime.now(UTC) + timedelta(minutes=5),
            "type": "access",
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)


def test_wrong_token_type_rejected():
    settings = get_settings()
    token = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "exp": datetime.now(UTC) + timedelta(minutes=5),
            "type": "password_reset",
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)
