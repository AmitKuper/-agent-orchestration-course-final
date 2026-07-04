"""Password hashing and JWT token utilities.

No secrets are stored here — all keys come from environment variables
via the application settings object.
"""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from cop_thief.constants import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM
from cop_thief.shared.errors import PermissionError

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*."""
    return _pwd_context.verify(plain, hashed)


def create_access_token(
    subject: str, secret_key: str, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    """Create a signed JWT access token for *subject* (username or user id)."""
    expire = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str, secret_key: str) -> str:
    """Decode *token* and return the subject claim.

    Raises PermissionError if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[JWT_ALGORITHM])
        sub: str | None = payload.get("sub")
        if sub is None:
            raise PermissionError("Token missing subject claim.")
        return sub
    except JWTError as exc:
        raise PermissionError("Invalid or expired token.") from exc
