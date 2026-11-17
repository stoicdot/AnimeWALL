
"""Tests for password hashing and verification."""

import pytest

from app.services.security import hash_password, verify_password


def test_password_is_stored_as_hash():
    password = "AnimeWall-Test-Password-123!"

    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2id$")


def test_correct_password_is_verified():
    password = "AnimeWall-Test-Password-123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_incorrect_password_is_rejected():
    hashed = hash_password("Correct-Password-123!")

    assert verify_password("Wrong-Password-123!", hashed) is False


def test_same_password_generates_different_hashes():
    password = "AnimeWall-Test-Password-123!"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert verify_password(password, first_hash)
    assert verify_password(password, second_hash)


def test_empty_password_is_rejected():
    with pytest.raises(ValueError):
        hash_password("")


def test_empty_password_verification_returns_false():
    hashed = hash_password("AnimeWall-Test-Password-123!")

    assert verify_password("", hashed) is False


def test_invalid_hash_returns_false():
    assert verify_password(
        "Some-Password-123!",
        "not-a-valid-hash",
    ) is False
