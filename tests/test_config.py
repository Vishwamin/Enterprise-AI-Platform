"""
Tests for app/core/config.py.

We pass _env_file=None so these tests always check the DEFAULT values,
regardless of whatever .env happens to exist on the machine running the
tests — tests should not depend on developer-specific local state.
"""

from app.core.config import Settings


def test_settings_default_app_env_is_development():
    settings = Settings(_env_file=None)
    assert settings.app_env == "development"


def test_settings_default_log_level_is_info():
    settings = Settings(_env_file=None)
    assert settings.log_level == "INFO"


def test_settings_reads_overrides():
    settings = Settings(_env_file=None, app_env="production", log_level="WARNING")
    assert settings.app_env == "production"
    assert settings.log_level == "WARNING"
