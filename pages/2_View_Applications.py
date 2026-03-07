"""Page 2 — View and query job applications."""

import datetime
import math

import pandas as pd
import streamlit as st

from app.base_page import BasePage
from app.config import DB_PATH, PAGE_SIZE
from app.database import get_all
from app.models import ARCHIVED_STATUSES, Application, Source, Status
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


def _apply_filters(
    apps: list[Application],
    statuses: list[str],
    sources: list[str],
    start: datetime.date,
    end: datetime.date,
) -> list[Application]:
    """Filter applications by status, source, and date range."""
    return [
        a
        for a in apps
        if a.status.value in statuses
        and a.source.value in sources
        and start <= a.date_applied <= end
    ]


def _render_csv_download(apps: list[Application]) -> None:
    """Render a CSV download button for the filtered results."""
    if not apps:
        return
    df: pd.DataFrame = to_dataframe(apps)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Export to CSV",
        data=csv,
        file_name="applications.csv",
        mime="text/csv",
    )


def _render_table(apps: list[Application]) -> None:
    """Render a paginated table of applications with Edit buttons."""
    if not apps:
        st.info("No applications match the current filters.")
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
        if row[7].button("Edit", key=f"edit_{app.id}"):
            st.session_state["edit_app_id"] = app.id
            st.switch_page("pages/3_Edit_Application.py")


class ViewApplicationsPage(BasePage):
    """Page for browsing and filtering job applications."""

    subtitle = "View Applications"

    def _body(self) -> None:
        st.title("View Applications")

        st.sidebar.header("Filters")
        show_archived = st.sidebar.toggle("Show Archived", value=False)

        default_statuses = [s.value for s in Status if s not in ARCHIVED_STATUSES]
        selected_statuses = st.sidebar.multiselect(
            "Status", [s.value for s in Status], default=default_statuses
        )
        selected_sources = st.sidebar.multiselect(
            "Source", [s.value for s in Source], default=[s.value for s in Source]
        )
        start_date: datetime.date = st.sidebar.date_input(
            "From", value=datetime.date(2000, 1, 1)
        )  # type: ignore[assignment]
        end_date: datetime.date = st.sidebar.date_input(
            "To", value=datetime.date.today()
        )  # type: ignore[assignment]

        all_apps = get_all(DB_PATH, include_archived=show_archived)
        filtered = sorted(
            _apply_filters(
                all_apps, selected_statuses, selected_sources, start_date, end_date
            ),
            key=lambda a: a.date_applied,
            reverse=True,
        )

        st.write(f"**{len(filtered)}** application(s) found.")
        _render_csv_download(filtered)

        total_pages = max(1, math.ceil(len(filtered) / PAGE_SIZE))
        page_num = st.selectbox("Page", range(1, total_pages + 1), index=0)
        page_apps = filtered[(page_num - 1) * PAGE_SIZE : page_num * PAGE_SIZE]
        _render_table(page_apps)


ViewApplicationsPage().run()
