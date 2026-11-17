
"""Password hashing and verification utilities."""

from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError


# Recommended password hashing configuration uses Argon2.
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Return a secure hash for a plaintext password."""

    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string.")

    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Check a plaintext password against its stored hash."""

    if not plain_password or not hashed_password:
        return False

    try:
        return password_hash.verify(plain_password, hashed_password)
    except UnknownHashError:
        return False
