"""Page 3 — Edit an existing job application."""

# pylint: disable=duplicate-code  # Application() kwargs mirror 1_Add_Application.py by design

import streamlit as st

from app.base_page import BasePage
from app.config import DB_PATH
from app.database import get_all, update_application
from app.models import Application, Source, Status


def _get_application(app_id: int) -> Application | None:
    """Retrieve an application by id, including archived records."""
    all_apps = get_all(DB_PATH, include_archived=True)
    matches = [a for a in all_apps if a.id == app_id]
    return matches[0] if matches else None


def _show_form(app: Application) -> None:
    """Render the edit form pre-populated with the given application."""
    status_values = [s.value for s in Status]
    source_values = [s.value for s in Source]

    with st.form("edit_form"):
        company = st.text_input("Company *", value=app.company)
        job_title = st.text_input("Job Title *", value=app.job_title)
        date_applied = st.date_input("Date Applied", value=app.date_applied)
        status = st.selectbox(
            "Status",
            status_values,
            index=status_values.index(app.status.value),
        )
        source = st.selectbox(
            "Source",
            source_values,
            index=source_values.index(app.source.value),
        )
        job_url = st.text_input("Job URL (optional)", value=app.job_url)
        notes = st.text_area("Notes (optional)", value=app.notes)

        col1, col2 = st.columns(2)
        saved = col1.form_submit_button("Save", type="primary")
        cancelled = col2.form_submit_button("Cancel")

    if saved:
        if not company or not job_title:
            st.error("Company and Job Title are required.")
            return
        updated = Application(
            id=app.id,
            company=company,
            job_title=job_title,
            date_applied=date_applied,
            status=Status(status),
            source=Source(source),
            job_url=job_url,
            notes=notes,
            created_at=app.created_at,
        )
        update_application(updated, DB_PATH)
        st.success("Application updated.")
        del st.session_state["edit_app_id"]

    if cancelled:
        del st.session_state["edit_app_id"]
        st.switch_page("pages/2_View_Applications.py")


class EditApplicationPage(BasePage):
    """Page for editing an existing job application."""

    subtitle = "Edit Application"

    def _body(self) -> None:
        st.title("Edit Application")

        if "edit_app_id" not in st.session_state:
            st.info("No application selected.")
            if st.button("← Back to View"):
                st.switch_page("pages/2_View_Applications.py")
            return

        app_id: int = st.session_state["edit_app_id"]
        app = _get_application(app_id)

        if app is None:
            st.error(f"Application ID {app_id} not found.")
            del st.session_state["edit_app_id"]
            return

        st.caption(f"Editing ID {app.id} — created {app.created_at}")
        _show_form(app)


EditApplicationPage().run()
