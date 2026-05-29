"""
utils/jwt.py — JWT creation/decoding and password hashing helpers.

All functions are pure (no I/O) so they are easy to unit-test.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
import bcrypt
from config import settings

# ── Password context ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Return the bcrypt hash of *plain*."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*."""
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))


# ── Token helpers ─────────────────────────────────────────────────────────────

def _create_token(subject: Any, expires_delta: timedelta, token_type: str) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": token_type,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: Any) -> str:
    """Create a short-lived access JWT."""
    return _create_token(
        subject,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )


def create_refresh_token(subject: Any) -> str:
    """Create a long-lived refresh JWT."""
    return _create_token(
        subject,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT.

    Raises ``jose.JWTError`` if the token is invalid or expired.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
