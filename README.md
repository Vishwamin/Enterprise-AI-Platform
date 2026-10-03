# Enterprise AI Knowledge Platform

An internal enterprise RAG platform: employees securely ask questions about
company documents and get grounded answers with citations.

This project is being built **phase by phase**, as a learning-while-building
exercise. See `PHASE.md` for what's currently implemented, `architecture.md`
for the system design, and `requirements.md` for the functional/non-functional
requirements driving it.

## Current status: Phase 3 — Database Foundation

PostgreSQL is now part of the stack: `organizations` and `users` tables,
managed via Alembic migrations. Still no auth, no AI — those come in
later phases. See `PHASE.md` for details.

## Prerequisites (new in Phase 3)

You need a local PostgreSQL server running. If you don't have one:
- Windows: install from https://www.postgresql.org/download/windows/
  (the installer sets a password for the `postgres` user — remember it)
- During/after install, create a database for this project:
  ```powershell
  psql -U postgres -c "CREATE DATABASE enterprise_ai_platform;"
  ```

## Quickstart

```bash
# 1. Create and activate a virtual environment (from inside this folder)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy the example env file and set your real Postgres credentials
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
# then edit .env -> DATABASE_URL with your actual postgres user/password

# 4. Apply database migrations (creates the tables)
alembic upgrade head

# 5. Run the app
uvicorn app.main:app --reload

# 6. Open the interactive docs
# http://127.0.0.1:8000/docs
```

## Project structure

```text
enterprise-ai-platform/
├── app/
│   ├── main.py              # FastAPI app entrypoint, global exception handler
│   ├── api/
│   │   └── v1/
│   │       ├── health.py    # GET /health, GET /
│   │       └── ask.py       # POST /api/v1/ask
│   ├── schemas/
│   │   └── ask.py           # Pydantic request/response models
│   ├── core/
│   │   ├── config.py         # centralized Settings (Phase 2, +DATABASE_URL in Phase 3)
│   │   └── logging.py        # logging setup (Phase 2)
│   └── db/
│       ├── session.py         # SQLAlchemy engine, session, get_db() dependency (Phase 3)
│       └── models.py          # Organization, User ORM models (Phase 3)
├── alembic/
│   ├── env.py                 # wired to our Settings + models (Phase 3)
│   └── versions/
│       └── 0001_create_organizations_and_users.py
├── alembic.ini
├── tests/
│   ├── conftest.py            # db_session fixture (Phase 3)
│   ├── test_health.py
│   ├── test_root.py
│   ├── test_ask.py
│   ├── test_config.py         # Phase 2
│   ├── test_error_handling.py # Phase 2
│   └── test_db.py             # Phase 3
├── requirements.md            # Phase 0
├── architecture.md            # Phase 0
├── PHASE.md                   # what's in THIS phase
├── requirements.txt           # Python dependencies
├── .env.example
└── .gitignore
```

## Running tests

```bash
pytest
```
