"""
Reusable FastAPI dependencies for authentication.

get_current_user is the gatekeeper: any endpoint that declares
`user: User = Depends(get_current_user)` automatically requires a valid
Bearer token before its function body runs — same pattern as get_db()
from Phase 3, and the same "validation happens before your code runs"
idea from Phase 1's Pydantic lesson.
"""

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.models import User
from app.db.session import get_db

# HTTPBearer gives us Swagger's "Authorize" button (paste just the raw
# token, no "Bearer " prefix needed there) and handles extracting the
# Authorization header for us.
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials

    try:
        user_id = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.get(User, user_id)
    if user is None:
        # Token is validly SIGNED but the user it points to no longer
        # exists (e.g. deleted after the token was issued).
        raise HTTPException(status_code=401, detail="User no longer exists")

    return user
