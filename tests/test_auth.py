"""
Tests for Phase 4 authentication, against the real database (via the
`db_session` fixture from conftest.py) and the real FastAPI app.

We create a test user directly via the ORM (bypassing the API — there's
no /register endpoint, see scripts/create_user.py and PHASE.md), then
exercise the actual HTTP login + protected-endpoint flow through
TestClient, same as every other endpoint test in this project.
"""

import jwt
import pytest

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.db.models import Organization, User
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture
def test_user(db_session):
    """
    Unlike the Phase 3 db tests, this one must actually COMMIT: the
    TestClient request below goes through app/api/deps.py's get_db(),
    which opens a SEPARATE database session. A separate session can't
    see another session's uncommitted (flushed-only) changes — that's
    normal transaction isolation, not a bug — so we commit here and
    clean up explicitly afterward instead of relying on rollback.
    """
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.flush()

    user = User(
        email="testuser@example.com",
        name="Test User",
        organization_id=org.id,
        password_hash=hash_password("correct-password"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    yield user

    db_session.delete(user)
    db_session.delete(org)
    db_session.commit()


# --- Login ---------------------------------------------------------------


def test_login_with_correct_credentials_returns_token(test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "testuser@example.com", "password": "correct-password"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_with_wrong_password_returns_401(test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "testuser@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_login_with_unknown_email_returns_401(test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "whatever"},
    )
    assert response.status_code == 401


def test_login_error_message_identical_for_unknown_email_and_wrong_password(test_user):
    # Guards against an information leak: the response shouldn't reveal
    # WHICH part was wrong.
    unknown_email = client.post(
        "/api/v1/auth/login", json={"email": "nobody@example.com", "password": "x"}
    )
    wrong_password = client.post(
        "/api/v1/auth/login",
        json={"email": "testuser@example.com", "password": "wrong-password"},
    )
    assert unknown_email.json()["detail"] == wrong_password.json()["detail"]


# --- Protected endpoint (/me) --------------------------------------------


def test_me_with_valid_token_returns_user(test_user):
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "testuser@example.com", "password": "correct-password"},
    )
    token = login_response.json()["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "testuser@example.com"
    assert body["id"] == test_user.id
    # Make sure the password hash never leaks into the response.
    assert "password_hash" not in body
    assert "password" not in body


def test_me_with_no_token_returns_401_or_403():
    # No Authorization header at all. FastAPI's HTTPBearer raises 403 for
    # a MISSING header and 401 for an INVALID one — both correctly mean
    # "you're not authenticated," so we accept either here, but the
    # invalid-token tests below pin down the 401 case precisely.
    response = client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)


def test_me_with_garbage_token_returns_401():
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_me_with_expired_token_returns_401(test_user):
    import datetime

    expired_payload = {
        "sub": str(test_user.id),
        "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=5),
    }
    expired_token = jwt.encode(expired_payload, settings.secret_key, algorithm="HS256")

    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"


def test_me_with_token_for_deleted_user_returns_401():
    # Validly signed token, but no such user id exists.
    token = create_access_token(user_id=999_999)
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
