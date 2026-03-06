"""Page 1 — Add a new job application."""

# pylint: disable=duplicate-code  # Application() kwargs mirror 3_Edit_Application.py by design

import datetime

import streamlit as st

from app.config import APP_ICON, APP_TITLE, DB_PATH
from app.database import add_application, get_all, init_db
from app.models import Application, Source, Status


def _find_existing(company: str, job_title: str) -> list[Application]:
    """Return existing apps matching company and job_title (case-insensitive)."""
    all_apps = get_all(DB_PATH, include_archived=True)
    return [
        a
        for a in all_apps
        if a.company.lower() == company.lower()
        and a.job_title.lower() == job_title.lower()
    ]


def _show_form() -> None:
    """Render the add application form."""
    if st.session_state.get("flash"):
        st.success(st.session_state.pop("flash"))

    with st.form("add_form"):
        company = st.text_input("Company *")
        job_title = st.text_input("Job Title *")
        date_applied = st.date_input("Date Applied", value=datetime.date.today())
        status = st.selectbox("Status", [s.value for s in Status])
        source = st.selectbox("Source", [s.value for s in Source])
        job_url = st.text_input("Job URL (optional)")
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Add Application")

    if not submitted:
        return

    if not company or not job_title:
        st.error("Company and Job Title are required.")
        return

    app = Application(
        company=company,
        job_title=job_title,
        date_applied=date_applied,
        status=Status(status),
        source=Source(source),
        job_url=job_url,
        notes=notes,
    )
    existing = _find_existing(company, job_title)
    if existing:
        st.session_state["pending_app"] = app
        st.session_state["dup_list"] = existing
        st.rerun()
    else:
        add_application(app, DB_PATH)
        st.success(f"Added '{job_title}' at {company}.")


def _show_confirm() -> None:
    """Show duplicate warning with Add Anyway / Cancel options."""
    app: Application = st.session_state["pending_app"]
    dups: list[Application] = st.session_state["dup_list"]

    st.warning(f"A duplicate was found for **{app.company}** — **{app.job_title}**:")
    for dup in dups:
        st.write(f"- ID {dup.id}: {dup.status.value}, applied {dup.date_applied}")

    col1, col2 = st.columns(2)
    if col1.button("Add Anyway", type="primary"):
        add_application(app, DB_PATH)
        st.session_state["flash"] = f"Added '{app.job_title}' at {app.company}."
        del st.session_state["pending_app"]
        del st.session_state["dup_list"]
        st.rerun()
    if col2.button("Cancel"):
        del st.session_state["pending_app"]
        del st.session_state["dup_list"]
        st.rerun()


def main() -> None:
    """Render the Add Application page."""
    st.set_page_config(page_title=f"Add Application — {APP_TITLE}", page_icon=APP_ICON)
    init_db(DB_PATH)
    st.title("Add Application")

    if "pending_app" in st.session_state:
        _show_confirm()
    else:
        _show_form()


main()
