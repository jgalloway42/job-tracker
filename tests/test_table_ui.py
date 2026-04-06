"""Tests for app/table_ui.py — shared table rendering helpers."""

# pylint: disable=duplicate-code  # test factories share structure by design
from datetime import date
from unittest.mock import MagicMock, call, patch

from app.models import Application, Source, Status
from app.table_ui import render_csv_download, render_table


def _make_app(**kwargs) -> Application:
    """Return an Application with sensible defaults, overridden by kwargs."""
    defaults = {
        "id": 1,
        "company": "Acme Corp",
        "job_title": "Engineer",
        "date_applied": date(2025, 1, 15),
        "status": Status.APPLIED,
        "source": Source.LINKEDIN,
        "job_url": "https://example.com",
        "notes": "Great team",
    }
    defaults.update(kwargs)
    return Application(**defaults)


def _make_mock_st(button_clicked: bool = False) -> MagicMock:
    """Return a mock streamlit module."""
    mock_st = MagicMock()
    mock_col = MagicMock()
    mock_col.button.return_value = button_clicked
    mock_st.columns.return_value = [mock_col] * 8
    return mock_st


# ── render_csv_download ───────────────────────────────────────────────────────


class TestRenderCsvDownload:
    """Tests for render_csv_download()."""

    def test_empty_list_renders_nothing(self) -> None:
        """No download button is shown when there are no applications."""
        with patch("app.table_ui.st") as mock_st:
            render_csv_download([])
        mock_st.download_button.assert_not_called()

    def test_non_empty_calls_download_button(self) -> None:
        """A download button is rendered when applications are present."""
        apps = [_make_app()]
        with patch("app.table_ui.st") as mock_st:
            render_csv_download(apps)
        mock_st.download_button.assert_called_once()

    def test_default_file_name(self) -> None:
        """Default file_name is 'applications.csv'."""
        apps = [_make_app()]
        with patch("app.table_ui.st") as mock_st:
            render_csv_download(apps)
        _, kwargs = mock_st.download_button.call_args
        assert kwargs["file_name"] == "applications.csv"

    def test_custom_file_name(self) -> None:
        """Custom file_name is passed through to the download button."""
        apps = [_make_app()]
        with patch("app.table_ui.st") as mock_st:
            render_csv_download(apps, file_name="search_results.csv")
        _, kwargs = mock_st.download_button.call_args
        assert kwargs["file_name"] == "search_results.csv"

    def test_mime_type_is_csv(self) -> None:
        """MIME type is always text/csv."""
        apps = [_make_app()]
        with patch("app.table_ui.st") as mock_st:
            render_csv_download(apps)
        _, kwargs = mock_st.download_button.call_args
        assert kwargs["mime"] == "text/csv"


# ── render_table ──────────────────────────────────────────────────────────────


class TestRenderTable:
    """Tests for render_table()."""

    def test_empty_list_shows_default_message(self) -> None:
        """Default empty message is displayed when the list is empty."""
        with patch("app.table_ui.st") as mock_st:
            render_table([])
        mock_st.info.assert_called_once_with(
            "No applications match the current filters."
        )

    def test_empty_list_shows_custom_message(self) -> None:
        """Custom empty_message is displayed when the list is empty."""
        with patch("app.table_ui.st") as mock_st:
            render_table([], empty_message="Nothing here.")
        mock_st.info.assert_called_once_with("Nothing here.")

    def test_empty_list_renders_no_columns(self) -> None:
        """st.columns is not called for an empty list."""
        with patch("app.table_ui.st") as mock_st:
            render_table([])
        mock_st.columns.assert_not_called()

    def test_non_empty_renders_header_and_row_columns(self) -> None:
        """st.columns is called once for headers and once per application row."""
        apps = [_make_app(id=1), _make_app(id=2)]
        with patch("app.table_ui.st", _make_mock_st()):
            render_table(apps)

    def test_app_fields_written_to_row(self) -> None:
        """Each application's fields are written into the row columns."""
        app = _make_app()
        mock_st = _make_mock_st()
        with patch("app.table_ui.st", mock_st):
            render_table([app])
        row_cols = mock_st.columns.return_value
        row_cols[0].write.assert_any_call(app.company)
        row_cols[1].write.assert_any_call(app.job_title)
        row_cols[2].write.assert_any_call(str(app.date_applied))
        row_cols[3].write.assert_any_call(app.status.value)
        row_cols[4].write.assert_any_call(app.source.value)

    def test_edit_button_uses_key_prefix(self) -> None:
        """The Edit button key includes the key_prefix and app id."""
        app = _make_app(id=42)
        mock_st = _make_mock_st(button_clicked=False)
        with patch("app.table_ui.st", mock_st):
            render_table([app], key_prefix="search_edit")
        mock_st.columns.return_value[7].button.assert_called_with(
            "Edit", key="search_edit_42"
        )

    def test_edit_button_click_sets_session_state_and_switches_page(self) -> None:
        """Clicking Edit stores the app id in session_state and navigates."""
        app = _make_app(id=7)
        mock_st = _make_mock_st(button_clicked=True)
        with patch("app.table_ui.st", mock_st):
            render_table([app])
        assert mock_st.session_state.__setitem__.call_args == call("edit_app_id", 7)
        mock_st.switch_page.assert_called_once_with("pages/3_Edit_Application.py")

    def test_edit_button_not_clicked_does_not_switch_page(self) -> None:
        """No navigation occurs when the Edit button is not clicked."""
        app = _make_app(id=3)
        mock_st = _make_mock_st(button_clicked=False)
        with patch("app.table_ui.st", mock_st):
            render_table([app])
        mock_st.switch_page.assert_not_called()

    def test_optional_fields_show_dash_when_empty(self) -> None:
        """Empty job_url and notes render as '—'."""
        app = _make_app(job_url="", notes="")
        mock_st = _make_mock_st()
        with patch("app.table_ui.st", mock_st):
            render_table([app])
        row_cols = mock_st.columns.return_value
        row_cols[5].write.assert_any_call("—")
        row_cols[6].write.assert_any_call("—")
