"""Tests for app/base_page.py — BasePage abstract class."""

from unittest.mock import MagicMock, patch

import pytest

from app.base_page import BasePage
from app.config import APP_ICON, APP_TITLE, DB_PATH


class _ConcretePage(BasePage):
    """Minimal concrete subclass used for testing."""

    subtitle = "Test Page"

    def __init__(self) -> None:
        self.body_called = False

    def _body(self) -> None:
        self.body_called = True


class _NoSubtitlePage(BasePage):
    """Concrete subclass with no subtitle — uses APP_TITLE directly."""

    def _body(self) -> None:
        pass


def _make_mock_st(button_clicked: bool = False) -> MagicMock:
    """Return a mock streamlit module with sensible defaults."""
    mock_st = MagicMock()
    mock_st.button.return_value = button_clicked
    return mock_st


class TestBasePageRun:
    """Tests for BasePage.run()."""

    def test_set_page_config_called_with_subtitle(self) -> None:
        """run() builds the title from subtitle and APP_TITLE."""
        page = _ConcretePage()
        with patch("app.base_page.st", _make_mock_st()) as mock_st, \
             patch("app.base_page.init_db"):
            page.run()
        mock_st.set_page_config.assert_called_once_with(
            page_title=f"Test Page \u2014 {APP_TITLE}",
            page_icon=APP_ICON,
            layout="wide",
        )

    def test_set_page_config_uses_app_title_when_no_subtitle(self) -> None:
        """run() falls back to APP_TITLE when subtitle is None."""
        page = _NoSubtitlePage()
        with patch("app.base_page.st", _make_mock_st()) as mock_st, \
             patch("app.base_page.init_db"):
            page.run()
        mock_st.set_page_config.assert_called_once_with(
            page_title=APP_TITLE,
            page_icon=APP_ICON,
            layout="wide",
        )

    def test_init_db_called_with_db_path(self) -> None:
        """run() initialises the database before rendering."""
        page = _ConcretePage()
        with patch("app.base_page.st", _make_mock_st()), \
             patch("app.base_page.init_db") as mock_init_db:
            page.run()
        mock_init_db.assert_called_once_with(DB_PATH)

    def test_body_is_called(self) -> None:
        """run() delegates page content to _body()."""
        page = _ConcretePage()
        with patch("app.base_page.st", _make_mock_st()), \
             patch("app.base_page.init_db"):
            page.run()
        assert page.body_called

    def test_exit_button_calls_os_exit(self) -> None:
        """run() calls os._exit(0) when the Exit App button is clicked."""
        page = _ConcretePage()
        with patch("app.base_page.st", _make_mock_st(button_clicked=True)), \
             patch("app.base_page.init_db"), \
             patch("app.base_page.os") as mock_os:
            page.run()
        mock_os._exit.assert_called_once_with(0)  # pylint: disable=protected-access

    def test_exit_button_not_called_when_not_clicked(self) -> None:
        """run() does not call os._exit when the button is not clicked."""
        page = _ConcretePage()
        with patch("app.base_page.st", _make_mock_st(button_clicked=False)), \
             patch("app.base_page.init_db"), \
             patch("app.base_page.os") as mock_os:
            page.run()
        mock_os._exit.assert_not_called()  # pylint: disable=protected-access


class TestBasePageAbstract:
    """Tests for BasePage ABC enforcement."""

    def test_cannot_instantiate_base_page_directly(self) -> None:
        """BasePage is abstract and cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BasePage()  # type: ignore[abstract]  # pylint: disable=abstract-class-instantiated
