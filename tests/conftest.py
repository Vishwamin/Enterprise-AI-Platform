"""
Shared pytest fixtures.

`db_session` gives each database test a real session against Postgres,
and ROLLS BACK everything at the end of the test — this is the
transaction concept from the Phase 3 lesson, used as a testing tool:
nothing a test does ever persists, so tests can't pollute each other or
leave junk data behind, and we never need a separate "clean up" step.

If Postgres isn't reachable (e.g. a fresh clone where nobody's set up a
local database yet), these tests SKIP with a clear message instead of
failing confusingly — database tests are environment-dependent in a way
our Phase 1/2 tests deliberately aren't.
"""

import pytest
from sqlalchemy.exc import OperationalError

from app.db.session import SessionLocal


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        session.connection()
    except OperationalError as exc:
        session.close()
        pytest.skip(f"Postgres not reachable at the configured DATABASE_URL: {exc}")

    yield session

    session.rollback()
    session.close()
