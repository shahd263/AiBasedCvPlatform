"""Password hashing and JWT utilities."""
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from Core.config import settings

# Bcrypt accepts at most 72 bytes; we normalize so bcrypt never raises (bcrypt 5.0+).
BCRYPT_MAX_PASSWORD_BYTES = 72


def _normalize_password_bytes(password: str) -> bytes:
    """Return password as bytes, truncated to 72 bytes so bcrypt never raises."""
    encoded = password.encode("utf-8")
    if len(encoded) <= BCRYPT_MAX_PASSWORD_BYTES:
        return encoded
    return encoded[:BCRYPT_MAX_PASSWORD_BYTES]


def hash_password(password: str) -> str:
    """Hash a plain password (input normalized to bcrypt's 72-byte limit)."""
    pw_bytes = _normalize_password_bytes(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw_bytes, salt)
    return hashed.decode("ascii")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash (input normalized to bcrypt's 72-byte limit)."""
    pw_bytes = _normalize_password_bytes(plain_password)
    try:
        return bcrypt.checkpw(pw_bytes, hashed_password.encode("ascii"))
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int, email: str) -> str:
    """Create a JWT containing user_id, email, and expiration."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    """Decode and validate JWT. Returns payload dict or None if invalid."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
