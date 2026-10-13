# PHASE.md — Phase 4: Authentication

## What was added

- `app/core/security.py` — `hash_password()`/`verify_password()` (bcrypt,
  via passlib) and `create_access_token()`/`decode_access_token()` (JWT,
  via PyJWT). Pure logic, no FastAPI dependency — independently testable.
- `users.password_hash` column — new migration
  `alembic/versions/0002_add_password_hash_to_users.py`. **0001 was never
  touched** — this is a brand new file, chained on top via `down_revision`.
- `app/api/deps.py` — `get_current_user()`, a reusable FastAPI dependency
  that extracts the Bearer token, verifies it, and loads the real `User`
  row from Postgres. Any future endpoint can require auth just by adding
  `user: User = Depends(get_current_user)` to its signature.
- `app/api/v1/auth.py`:
  - `POST /api/v1/auth/login` — verifies email+password, returns a JWT.
    Returns the *same* error message for "unknown email" and "wrong
    password" (prevents account enumeration).
  - `GET /api/v1/auth/me` — protected; proves the whole chain works.
- `settings.secret_key` and `settings.access_token_expire_minutes` — new
  config (Phase 2's pattern, extended). `secret_key` is explicitly
  flagged in both code comments and `.env.example` as the first setting
  that's actually dangerous to leave at its default.
- `scripts/create_user.py` — a seed script to create a user with a
  properly hashed password, since there's no public `/register` endpoint
  yet (see "Known limitations" below for why that's deferred).
- `tests/test_auth.py` — 8 new tests, run against the real database and
  real app: successful login, wrong password, unknown email, identical
  error messages for both, valid-token `/me`, missing-token `/me`,
  garbage-token `/me`, expired-token `/me`, deleted-user-token `/me`.
- `tests/test_db.py` — updated: `password_hash` is now required on every
  `User()` construction. **This is real evidence of what the Phase 3
  lesson warned about** — the schema change broke 2 of Phase 3's existing
  tests until they were updated to match. They were fixed, not ignored.
- **27 tests total, all passing**, verified against a real local Postgres
  instance (not mocked).

## What changed

- `app/db/models.py` — `User` gained `password_hash` (not null).
- `app/main.py` — `auth.router` included under `/api/v1`; version bumped
  to `0.4.0`.
- `requirements.txt` — added `passlib`, `bcrypt`, `pyjwt`.
- `.env.example` — added `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`.

**No breaking changes to `/health`, `/`, or `/api/v1/ask`** — all still
work exactly as before. 2 of the 18 existing Phase 1-3 tests needed a
one-line fix (the `password_hash` field); none of their *behavior*
changed, only the data needed to construct a valid `User` in a test.

## Concepts learned

- Authentication (who are you) vs. authorization (what can you do) — kept
  deliberately separate; Phase 4 does NOT check permissions
- Password hashing: one-way, salted, deliberately slow (bcrypt) —
  verified for real: `psql` shows `$2b$12$...` in the database, never
  the plaintext password
- Why general-purpose fast hashes (SHA-256) are wrong for passwords
- JWT structure (`header.payload.signature`), and that the payload is
  readable-but-tamper-evident, not encrypted — the signature is what a
  forged/edited token fails to reproduce
- Access tokens (short-lived, frequent) vs. refresh tokens (long-lived,
  rare, different purpose) — refresh tokens deliberately deferred, not
  forgotten (see below)
- `401` ("I don't know who you are") vs. `403` ("you're not allowed") —
  observed both for real: a missing header returns FastAPI's own `403`,
  an invalid/garbage token returns our `401`
- Dependency injection as a gatekeeper pattern (`Depends(get_current_user)`)
  — same mechanism as `get_db()` from Phase 3 and Pydantic validation
  from Phase 1: all three stop a function body from running until a
  precondition is satisfied
- Why login returns the *same* error for "no such user" and "wrong
  password" — avoiding account enumeration
- Why a schema change (new NOT NULL column) can break existing tests,
  and why that's normal, expected, and something you fix rather than
  something that means your migration was wrong

## How to run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# edit .env -> DATABASE_URL to match your local Postgres,
# and ideally generate a real SECRET_KEY:
#   python -c "import secrets; print(secrets.token_hex(32))"
alembic upgrade head
python -m scripts.create_user --email alice@acme.example --password supersecret123 --name Alice --org "Acme Co"
uvicorn app.main:app --reload
```

## How to test

```bash
pytest -v
```

Expected: `27 passed` (3 of `test_db.py`'s and all 8 of `test_auth.py`'s
require Postgres reachable — they `SKIP` cleanly otherwise, same as Phase 3).

Manual verification (see README's "Trying auth yourself" for the exact
commands) — confirmed during this build:
```
POST /api/v1/auth/login (correct password)  -> 200, {"access_token": "...", "token_type": "bearer"}
POST /api/v1/auth/login (wrong password)    -> 401, {"detail": "Invalid email or password"}
GET  /api/v1/auth/me    (valid token)        -> 200, user info, NO password_hash field
GET  /api/v1/auth/me    (no token)           -> 403, {"detail": "Not authenticated"}
GET  /api/v1/auth/me    (garbage token)      -> 401, {"detail": "Invalid token"}
```

And in the server log:
```
2026-10-12 ... | INFO    | app.api.v1.auth | User 20 logged in
2026-10-12 ... | WARNING | app.api.v1.auth | Failed login attempt for user_id=20
```

## Known limitations

- **No `/register` endpoint.** Users are created via `scripts/create_user.py`
  only. Self-service signup brings its own concerns (email verification,
  abuse/rate-limiting) that belong in a dedicated later pass, not bundled
  into the login/token mechanics this phase is about.
- **No refresh tokens.** Access tokens expire after 30 minutes and the
  user must log in again — no silent renewal yet. Noted as a deliberate
  scope cut, not an oversight.
- **No authorization yet.** Any valid token can hit any protected
  endpoint — there's no concept of roles or permissions until Phase 5.
  `/me` is the only protected endpoint that exists so far.
- **No logout / token revocation.** A JWT is valid until it expires —
  there's no server-side way to invalidate one early yet (would need a
  blocklist, typically backed by Redis — Phase 16).
- `0002`'s migration adds `password_hash` as NOT NULL with no default —
  explicitly flagged in the migration file as only safe because the
  table is still empty; a populated table would need a 3-step
  add-column / backfill / enforce-not-null migration instead.

## What comes next — Phase 5

Authorization & RBAC: roles, permissions (`document:read`, `user:manage`,
etc.), and enforcing `403` for an authenticated-but-not-permitted user —
built directly on top of the `get_current_user` dependency from this phase.
