"""Tests for app/config.py — typed constants loaded from environment."""

import importlib
from unittest.mock import patch

from app import config


class TestKeysPresent:
    """Assert every expected configuration key is exported."""

    def test_db_path_present(self):
        """DB_PATH must be defined."""
        assert hasattr(config, "DB_PATH")

    def test_app_title_present(self):
        """APP_TITLE must be defined."""
        assert hasattr(config, "APP_TITLE")

    def test_app_icon_present(self):
        """APP_ICON must be defined."""
        assert hasattr(config, "APP_ICON")

    def test_week_ending_day_present(self):
        """WEEK_ENDING_DAY must be defined."""
        assert hasattr(config, "WEEK_ENDING_DAY")

    def test_page_size_present(self):
        """PAGE_SIZE must be defined."""
        assert hasattr(config, "PAGE_SIZE")


class TestTypes:
    """Assert configuration values carry the correct Python types."""

    def test_db_path_is_str(self):
        """DB_PATH must be a str."""
        assert isinstance(config.DB_PATH, str)

    def test_app_title_is_str(self):
        """APP_TITLE must be a str."""
        assert isinstance(config.APP_TITLE, str)

    def test_app_icon_is_str(self):
        """APP_ICON must be a str."""
        assert isinstance(config.APP_ICON, str)

    def test_week_ending_day_is_str(self):
        """WEEK_ENDING_DAY must be a str."""
        assert isinstance(config.WEEK_ENDING_DAY, str)

    def test_page_size_is_int(self):
        """PAGE_SIZE must be an int."""
        assert isinstance(config.PAGE_SIZE, int)


class TestCustomValues:
    """Assert custom env vars are picked up correctly after a reload."""

    def test_custom_db_path(self, monkeypatch):
        """Custom DB_PATH env var is reflected after reload."""
        monkeypatch.setenv("DB_PATH", "custom.db")
        importlib.reload(config)
        assert config.DB_PATH == "custom.db"

    def test_page_size_cast_to_int(self, monkeypatch):
        """PAGE_SIZE string env var is cast to int."""
        monkeypatch.setenv("PAGE_SIZE", "50")
        importlib.reload(config)
        assert isinstance(config.PAGE_SIZE, int)
        assert config.PAGE_SIZE == 50

    def test_all_custom_values(self, monkeypatch):
        """All five env vars are picked up after reload."""
        monkeypatch.setenv("DB_PATH", "test.db")
        monkeypatch.setenv("APP_TITLE", "My Tracker")
        monkeypatch.setenv("APP_ICON", "🚀")
        monkeypatch.setenv("WEEK_ENDING_DAY", "FRI")
        monkeypatch.setenv("PAGE_SIZE", "10")
        importlib.reload(config)
        assert config.DB_PATH == "test.db"
        assert config.APP_TITLE == "My Tracker"
        assert config.APP_ICON == "🚀"
        assert config.WEEK_ENDING_DAY == "FRI"
        assert config.PAGE_SIZE == 10


class TestDefaults:
    """Assert hardcoded defaults apply when env vars are absent."""

    def test_defaults_when_env_absent(self, monkeypatch):
        """All five constants fall back to their documented defaults."""
        for key in ["DB_PATH", "APP_TITLE", "APP_ICON", "WEEK_ENDING_DAY", "PAGE_SIZE"]:
            monkeypatch.delenv(key, raising=False)
        with patch("dotenv.load_dotenv"):
            importlib.reload(config)
        assert config.DB_PATH == "jobs.db"
        assert config.APP_TITLE == "Job Application Tracker"
        assert config.APP_ICON == "💼"
        assert config.WEEK_ENDING_DAY == "SAT"
        assert config.PAGE_SIZE == 25
        assert isinstance(config.PAGE_SIZE, int)

    def test_page_size_default_is_twenty_five(self, monkeypatch):
        """PAGE_SIZE default must be 25 when not set in environment."""
        monkeypatch.delenv("PAGE_SIZE", raising=False)
        with patch("dotenv.load_dotenv"):
            importlib.reload(config)
        assert config.PAGE_SIZE == 25
