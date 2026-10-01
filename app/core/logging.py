"""
Application-wide logging configuration.

Called once, at startup, from app/main.py. After this runs, any module
can do:

    import logging
    logger = logging.getLogger(__name__)
    logger.info("something happened")

and it will be formatted and filtered consistently, using the level
configured via LOG_LEVEL in .env / app/core/config.py.
"""

import logging

from app.core.config import settings


def configure_logging() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured. app_env=%s log_level=%s",
        settings.app_env,
        settings.log_level,
    )
