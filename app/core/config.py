"""
Centralized application settings.

Everything the app needs to be configured with lives HERE, as typed
fields on a single Pydantic model. Nothing else in the codebase should
call os.environ directly — it should import `settings` from this module.

Why this matters (see PHASE.md / our Phase 2 lesson):
- Validated once, at import time -> misconfiguration fails immediately
  and loudly at startup, not mysteriously deep in a request handler.
- Typed -> `settings.log_level` is a str, not "whatever os.environ handed us".
- One file to read to see every setting the app supports.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Which environment we're running in: "development" or "production".
    # Later phases use this to change behavior (log verbosity, error
    # detail, auto-reload, etc.) without duplicating code paths.
    app_env: str = "development"

    # Minimum severity of log message that actually gets emitted.
    # See app/core/logging.py.
    log_level: str = "INFO"

    # Where PostgreSQL lives. Format:
    # postgresql+psycopg2://<user>:<password>@<host>:<port>/<database>
    # The default below points at a local Postgres instance — fine for
    # development, never used as-is in production (a real deployment
    # sets DATABASE_URL via its own environment, pointing at a managed
    # database, never hardcoded here).
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/enterprise_ai_platform"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Instantiated once, at import time. Every other module imports THIS
# object rather than constructing its own Settings().
settings = Settings()
