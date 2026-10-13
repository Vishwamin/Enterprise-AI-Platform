# Enterprise AI Knowledge Platform

An internal enterprise RAG platform: employees securely ask questions about
company documents and get grounded answers with citations.

This project is being built **phase by phase**, as a learning-while-building
exercise. See `PHASE.md` for what's currently implemented, `architecture.md`
for the system design, and `requirements.md` for the functional/non-functional
requirements driving it.

## Current status: Phase 4 — Authentication

Users can log in and get a JWT; a protected `/me` endpoint proves the
token mechanism works end-to-end. No authorization/RBAC yet (any logged-in
user can do anything — that's Phase 5), no AI yet. See `PHASE.md`.

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

# 4. Apply database migrations (creates/updates the tables)
alembic upgrade head

# 5. Create a user to log in as (no public /register endpoint yet)
python -m scripts.create_user --email alice@acme.example --password supersecret123 --name Alice --org "Acme Co"

# 6. Run the app
uvicorn app.main:app --reload

# 7. Open the interactive docs
# http://127.0.0.1:8000/docs
```

## Trying auth yourself

```bash
# Log in — get a token
curl -X POST http://127.0.0.1:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\": \"alice@acme.example\", \"password\": \"supersecret123\"}"

# Use the token (replace TOKEN with the access_token from above)
curl http://127.0.0.1:8000/api/v1/auth/me -H "Authorization: Bearer TOKEN"
```

Or in `/docs`: click **Authorize**, paste just the token (no `Bearer `
prefix needed there), and try `/api/v1/auth/me` directly in the browser.

## Project structure

```text
enterprise-ai-platform/
├── app/
│   ├── main.py              # FastAPI app entrypoint, global exception handler
│   ├── api/
│   │   ├── deps.py           # get_current_user dependency (Phase 4)
│   │   └── v1/
│   │       ├── health.py    # GET /health, GET /
│   │       ├── ask.py       # POST /api/v1/ask
│   │       └── auth.py       # POST /api/v1/auth/login, GET /api/v1/auth/me (Phase 4)
│   ├── schemas/
│   │   ├── ask.py            # Pydantic request/response models
│   │   └── auth.py            # LoginRequest, TokenResponse, UserResponse (Phase 4)
│   ├── core/
│   │   ├── config.py          # centralized Settings (+SECRET_KEY, token expiry in Phase 4)
│   │   ├── logging.py         # logging setup (Phase 2)
│   │   └── security.py         # password hashing + JWT helpers (Phase 4)
│   └── db/
│       ├── session.py          # SQLAlchemy engine, session, get_db() dependency (Phase 3)
│       └── models.py           # Organization, User ORM models (+password_hash in Phase 4)
├── alembic/
│   ├── env.py                  # wired to our Settings + models (Phase 3)
│   └── versions/
│       ├── 0001_create_organizations_and_users.py
│       └── 0002_add_password_hash_to_users.py
├── alembic.ini
├── scripts/
│   └── create_user.py           # seed script to create a user (Phase 4)
├── tests/
│   ├── conftest.py             # db_session fixture (Phase 3)
│   ├── test_health.py
│   ├── test_root.py
│   ├── test_ask.py
│   ├── test_config.py          # Phase 2
│   ├── test_error_handling.py  # Phase 2
│   ├── test_db.py              # Phase 3
│   └── test_auth.py             # Phase 4
├── requirements.md             # Phase 0
├── architecture.md             # Phase 0
├── PHASE.md                    # what's in THIS phase
├── requirements.txt            # Python dependencies
├── .env.example
└── .gitignore
```

## Running tests

```bash
pytest
```
