"""Tests for app/database.py."""

import app.database


def test_module_importable():
    """Database module must be importable without errors."""
    assert app.database is not None
