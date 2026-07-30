import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings

_hasher = PasswordHasher()

# Hardcoded, not settings-driven: a configurable algorithm (e.g. from .env) is an
# unnecessary injection surface for something that should never change per-deploy.
_JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def generate_token() -> str:
    """Opaque, unguessable token for email verification / password reset links."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Deterministic hash for lookup — tokens are stored hashed so a DB leak alone
    doesn't yield usable verification/reset links."""
    return hashlib.sha256(token.encode()).hexdigest()


def create_session_token(user_id: UUID, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=_JWT_ALGORITHM)


def decode_session_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[_JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
