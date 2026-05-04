"""
Password hashing and JWT token utilities.

Passwords are hashed with bcrypt via passlib before storage.
Authentication tokens are signed JWTs with a configurable expiry.
The secret key must be a long random string in production —
compromise of this key allows forging tokens for any user.
"""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# CryptContext configures the hashing algorithm.
# bcrypt automatically salts hashes, making rainbow table
# attacks infeasible. deprecated="auto" will re-hash any
# password stored with an older algorithm on next login.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Returns the bcrypt hash of a plain-text password.
    The original password is never stored.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compares a plain-text password against a stored bcrypt hash.
    Returns True if they match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    """
    Creates a signed JWT access token for the given subject (user ID).

    The token encodes:
      - sub: the user identifier
      - exp: expiry timestamp (current time + configured minutes)
      - iat: issued-at timestamp

    The token is signed with the application secret key using the
    configured algorithm (HS256). It cannot be forged without the key.
    """
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.jwt_expire_minutes)

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
    }

    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    """
    Validates a JWT token and returns the subject (user ID).

    Returns None if the token is expired, malformed, or has an
    invalid signature. Callers must treat None as authentication failure.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        subject: str | None = payload.get("sub")
        return subject
    except JWTError:
        return None
