"""
Password hashing and JWT helpers.

Nothing in this file is FastAPI-specific — it's pure logic, reusable and
independently testable. app/api/deps.py and app/api/v1/auth.py are what
wire this into actual HTTP endpoints.
"""

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt: deliberately slow (expensive to brute-force) and auto-salts
# every hash, so two users with the same password get different hashes.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """
    Builds a signed JWT. `sub` ("subject") is the standard JWT claim name
    for "who this token is about" — we store the user's id there.
    `exp` is a standard claim too; libraries that verify JWTs (including
    PyJWT here) know to automatically reject an expired token.
    """
    expire_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": str(user_id), "exp": expire_at}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> int:
    """
    Verifies signature + expiry, and returns the user id encoded in it.
    Raises jwt.InvalidTokenError (or a subclass, e.g. ExpiredSignatureError)
    if the token is malformed, tampered with, or expired — callers (see
    app/api/deps.py) are expected to catch that and turn it into a 401.
    """
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    return int(payload["sub"])
