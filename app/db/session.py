"""
Database engine and session setup.

CONCEPTS:

- `engine`   — manages the actual connection pool to Postgres (see Phase 3
               lesson on connection pooling). Created ONCE, reused everywhere.
- `Session`  — a single "conversation" with the database: you open one,
               do some work (queries, inserts), commit or rollback, close it.
               A session is NOT a connection itself — it borrows one from
               the engine's pool for as long as it needs it.
- `get_db()` — a FastAPI dependency. Used like:

      @router.get("/something")
      def handler(db: Session = Depends(get_db)):
          ...

  FastAPI calls get_db() before the handler runs, hands the handler the
  yielded session, and — critically — resumes this generator after the
  handler returns to run the `finally` block, guaranteeing the session is
  always closed, even if the handler raised an exception.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
