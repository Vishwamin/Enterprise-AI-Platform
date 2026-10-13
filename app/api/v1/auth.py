"""
Authentication endpoints.

POST /api/v1/auth/login  — public. Verifies email+password, returns a JWT.
GET  /api/v1/auth/me     — protected. Proves the token mechanism actually
                            works end-to-end: no valid token, no response.

Note what's NOT here: no /register. Creating users is deliberately out of
scope for Phase 4 — see PHASE.md. For now, scripts/create_user.py creates
users directly (a common real pattern: an admin/seed script before
self-service signup exists).
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.db.models import User
from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == request.email).first()

    # Deliberately the SAME error for "no such email" and "wrong password".
    # Telling an attacker "that email doesn't exist" vs "wrong password"
    # lets them enumerate which emails have accounts — a real information
    # leak. One generic message either way.
    invalid_credentials = HTTPException(status_code=401, detail="Invalid email or password")

    if user is None:
        logger.warning("Login attempt for unknown email: %s", request.email)
        raise invalid_credentials

    if not verify_password(request.password, user.password_hash):
        logger.warning("Failed login attempt for user_id=%s", user.id)
        raise invalid_credentials

    logger.info("User %s logged in", user.id)
    token = create_access_token(user_id=user.id)
    return TokenResponse(access_token=token)


@router.get("/auth/me", response_model=UserResponse, tags=["auth"])
def read_current_user(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
