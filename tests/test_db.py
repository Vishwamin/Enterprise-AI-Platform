"""
Tests against the real Postgres database (via the `db_session` fixture
in conftest.py), proving the schema from
alembic/versions/0001_create_organizations_and_users.py actually
enforces what we expect — not just that the Python classes exist.

`db_session.flush()` sends pending changes to Postgres (so constraints
are checked) WITHOUT committing — everything is rolled back by the
fixture when the test ends. See the Phase 3 lesson on transactions.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.models import Organization, User


def test_create_organization_and_user(db_session):
    org = Organization(name="Acme Co")
    db_session.add(org)
    db_session.flush()  # org.id is now assigned by Postgres

    user = User(email="alice@acme.example", name="Alice", organization_id=org.id)
    db_session.add(user)
    db_session.flush()

    assert user.id is not None
    assert user.organization_id == org.id
    # Proves the relationship() mapping in models.py works, not just the FK column
    assert user.organization.name == "Acme Co"


def test_foreign_key_rejects_nonexistent_organization(db_session):
    # No organization with this id exists — the database itself
    # (not our Python code) must reject this insert.
    user = User(email="ghost@nowhere.example", name="Ghost", organization_id=999_999)
    db_session.add(user)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_email_must_be_unique(db_session):
    org = Organization(name="Dup Co")
    db_session.add(org)
    db_session.flush()

    db_session.add(User(email="dup@dup.example", name="First", organization_id=org.id))
    db_session.flush()

    db_session.add(User(email="dup@dup.example", name="Second", organization_id=org.id))
    with pytest.raises(IntegrityError):
        db_session.flush()
