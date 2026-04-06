"""Page 5 — Search job applications by company or title."""

import math

import streamlit as st

from app.base_page import BasePage
from app.config import DB_PATH, PAGE_SIZE
from app.database import get_all
from app.models import Application
from app.table_ui import render_csv_download, render_table


def _search(apps: list[Application], query: str) -> list[Application]:
    """Return applications whose company or title contains the query string."""
    q = query.strip().lower()
    return [a for a in apps if q in a.company.lower() or q in a.job_title.lower()]


class SearchPage(BasePage):
    """Page for searching job applications by company or title."""

    subtitle = "Search"

    def _body(self) -> None:
        st.title("Search Applications")

        st.markdown(
            "<style>[data-baseweb='tag']{"
            "background-color:rgb(66,111,245)!important}</style>",
            unsafe_allow_html=True,
        )

        show_archived = st.sidebar.toggle("Show Archived", value=False)

        query = st.text_input(
            "Search by company or job title",
            placeholder="e.g. Google, Software Engineer",
        )

        if not query.strip():
            st.info("Enter a search term above to find applications.")
            return

        all_apps = get_all(DB_PATH, include_archived=show_archived)
        results = sorted(
            _search(all_apps, query),
            key=lambda a: a.date_applied,
            reverse=True,
        )

        st.write(f"**{len(results)}** result(s) for **{query.strip()}**.")
        render_csv_download(results, file_name="search_results.csv")

        total_pages = max(1, math.ceil(len(results) / PAGE_SIZE))
        page_col, _ = st.columns([1, 5])
        page_num = page_col.selectbox("Page", range(1, total_pages + 1), index=0)
        page_apps = results[(page_num - 1) * PAGE_SIZE : page_num * PAGE_SIZE]
        render_table(
            page_apps,
            key_prefix="search_edit",
            empty_message="No applications match your search.",
        )


SearchPage().run()
