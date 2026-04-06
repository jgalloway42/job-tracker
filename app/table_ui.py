"""Shared table rendering helpers used by multiple pages."""

import pandas as pd
import streamlit as st

from app.models import Application
from app.reports import to_dataframe

_COL_WIDTHS = [2, 2, 1.5, 2, 1.5, 2, 2, 1]
_COL_HEADERS = [
    "Company",
    "Job Title",
    "Date Applied",
    "Status",
    "Source",
    "Job URL",
    "Notes",
    "",
]


def render_csv_download(
    apps: list[Application], file_name: str = "applications.csv"
) -> None:
    """Render a CSV download button for the given applications."""
    if not apps:
        return
    df: pd.DataFrame = to_dataframe(apps)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Export to CSV",
        data=csv,
        file_name=file_name,
        mime="text/csv",
    )


def render_table(
    apps: list[Application],
    key_prefix: str = "edit",
    empty_message: str = "No applications match the current filters.",
) -> None:
    """Render a paginated table of applications with Edit buttons."""
    if not apps:
        st.info(empty_message)
        return

    header_cols = st.columns(_COL_WIDTHS)
    for col, header in zip(header_cols, _COL_HEADERS):
        if header:
            col.markdown(f"<u>**{header}**</u>", unsafe_allow_html=True)

    for app in apps:
        row = st.columns(_COL_WIDTHS)
        row[0].write(app.company)
        row[1].write(app.job_title)
        row[2].write(str(app.date_applied))
        row[3].write(app.status.value)
        row[4].write(app.source.value)
        row[5].write(app.job_url or "—")
        row[6].write(app.notes or "—")
        if row[7].button("Edit", key=f"{key_prefix}_{app.id}"):
            st.session_state["edit_app_id"] = app.id
            st.switch_page("pages/3_Edit_Application.py")
