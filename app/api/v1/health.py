"""
Health check and root endpoints.

These are NOT versioned under /api/v1 — health checks and root info are
infrastructure-level endpoints (load balancers, uptime monitors, humans
poking the API) that should stay stable regardless of API version.
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", tags=["infra"])
def health_check():
    """
    Used by load balancers / orchestrators / uptime monitors to check
    if this service instance is alive and able to respond.

    In later phases this will also check dependencies (database,
    vector store, etc.) — for now it just proves the process is up.
    """
    logger.debug("Health check requested")
    return {"status": "healthy"}


@router.get("/", tags=["infra"])
def root():
    """
    Basic info about the API. Useful for humans hitting the base URL
    and for quick sanity checks that the right service is running.
    """
    return {
        "message": "Enterprise AI Knowledge Platform is running",
        "version": "0.2.0",
        "docs": "/docs",
    }
