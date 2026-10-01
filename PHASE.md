# PHASE.md — Phase 2: Configuration & Engineering Foundations

## What was added

- `app/core/config.py` — a centralized `Settings` object (Pydantic), reading
  `app_env` and `log_level` from `.env`. Validated once, at import time.
- `app/core/logging.py` — configures Python's `logging` module once at
  startup, driven by `settings.log_level`.
- Global exception handler in `app/main.py` — any unhandled exception is
  logged in full (with traceback) server-side, but the client only ever
  sees `{"error": "internal_error", "message": "..."}` with a 500 status.
- A dev-only `GET /debug/trigger-error` endpoint, gated on
  `settings.app_env != "production"`, that exists purely to exercise the
  exception handler above — a small real example of environment-based
  behavior, not just log verbosity.
- An EXPECTED error case in `POST /api/v1/ask`: an empty/whitespace-only
  `question` now returns `400` with a specific message, via
  `HTTPException` — distinct from the generic 500 safety net.
- `.env.example` now has real (non-secret) content: `APP_ENV`, `LOG_LEVEL`.
- 7 new tests (`test_config.py`, `test_error_handling.py`, plus one added
  to `test_ask.py`) — **15 tests total, all passing.**

## What changed

- `app/main.py` — now configures logging and settings at import, and
  registers the global exception handler. Existing `/health`, `/`,
  `/api/v1/ask` routes are unchanged in URL and success-path behavior.
- `app/api/v1/health.py`, `app/api/v1/ask.py` — now use `logging` instead
  of nothing; `ask.py` gained the empty-question validation above.
- App version bumped to `0.2.0` in FastAPI metadata (cosmetic, reflects
  the phase).

**No breaking changes** — every Phase 1 test still passes unmodified.

## Concepts learned

- Why environment variables exist (same code, different config per
  environment; secrets never live in source)
- Why secrets in Git are permanently compromised once committed, even if
  later deleted — history persists
- `.env` (real, local, gitignored) vs `.env.example` (fake, committed,
  documentation)
- Dev vs prod configuration, and using it to gate behavior (here: whether
  the debug endpoint even exists)
- Why a centralized, validated `Settings` object beats scattered
  `os.environ.get(...)` calls — fail fast at startup, not mysteriously
  mid-request
- Why `print()` doesn't scale to production: no severity, no timestamps,
  nowhere to route it, no way to filter
- Log levels and their ordering: `DEBUG < INFO < WARNING < ERROR <
  CRITICAL` — setting `LOG_LEVEL=WARNING` silently drops everything below it
- Expected errors (handled on purpose, specific status/message) vs
  unexpected exceptions (caught by a generic safety net)
- Why the client and the server-side log must show DIFFERENT levels of
  detail for the same failure (security: no leaked internals to the client;
  debuggability: full detail for us)

## How to run

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env       # optional — defaults work without it
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs`.

## How to test

```bash
pytest -v
```

Expected: `15 passed`.

Manual checks:
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/
curl -X POST http://127.0.0.1:8000/api/v1/ask -H "Content-Type: application/json" -d "{\"question\": \"What is our leave policy?\"}"

REM Expected error (400):
curl -X POST http://127.0.0.1:8000/api/v1/ask -H "Content-Type: application/json" -d "{\"question\": \"   \"}"

REM Unhandled exception (500, safe body) — dev-only:
curl http://127.0.0.1:8000/debug/trigger-error
```

Watch the terminal running uvicorn — you should see structured log lines
like:
```
2026-09-22 17:40:48,717 | INFO     | app.api.v1.ask | Received question: ...
2026-09-22 17:40:48,729 | ERROR    | app.main | Unhandled exception on GET /debug/trigger-error: ...
Traceback (most recent call last):
  ...
```
...while the HTTP response for that last one is just the generic safe JSON.

## Known limitations

- Only two settings exist so far (`app_env`, `log_level`) — more get added
  as later phases need them (`DATABASE_URL` in Phase 3, `SECRET_KEY` in
  Phase 4, an LLM API key in Phase 13)
- Logs go to console only — no shipping to a log aggregator yet (out of
  scope until we're actually deploying somewhere)
- The `/debug/trigger-error` endpoint is a teaching tool, not a real
  feature — it'll likely be removed or replaced by proper test coverage
  once we have real code paths that can fail on their own
- No authentication, no database, no real AI — all still ahead

## What comes next — Phase 3

Database Foundation: introduce PostgreSQL, teach tables/keys/relationships/
migrations, and design the initial schema (starting with `users` and
`organizations`, since those are needed before Phase 4's auth).
