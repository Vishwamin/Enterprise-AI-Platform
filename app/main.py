"""
Application entrypoint.

Why API versioning (/api/v1)?
Once real clients depend on our API, we can't freely change response
shapes without breaking them. Versioning the URL means we can introduce
/api/v2 later with breaking changes while /api/v1 keeps working for
whoever hasn't migrated yet. Infra endpoints (/health, /) are deliberately
NOT versioned — see app/api/v1/health.py for why.

Phase 2 additions:
- Centralized settings (app/core/config.py) loaded and validated at import.
- Logging configured once, here, before anything else runs.
- A global exception handler: any unhandled exception anywhere in the app
  gets logged in full detail server-side, but the CLIENT only ever sees a
  generic, safe error response — never a raw traceback.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1 import ask, health
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enterprise AI Knowledge Platform",
    version="0.2.0",
)

# Infra endpoints: GET /health, GET /  (unversioned)
app.include_router(health.router)

# Versioned API endpoints: POST /api/v1/ask
app.include_router(ask.router, prefix="/api/v1")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catches anything that isn't already handled (e.g. not a Pydantic
    validation error or an intentionally-raised HTTPException).

    Server-side: log the full exception, with traceback, so WE can debug it.
    Client-side: return a generic, consistent message — no internals leaked.
    """
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Something went wrong. Please try again later.",
        },
    )


# Dev-only endpoint that exists purely to prove the exception handler
# above actually works. Gated on app_env so it's never reachable in
# production — a small, real example of dev-vs-prod configuration
# changing what the app exposes, not just how it logs.
if settings.app_env != "production":

    @app.get("/debug/trigger-error", tags=["debug"])
    def trigger_error():
        raise RuntimeError("Intentional test error to exercise the exception handler")
