"""Page 4 — Reports and analytics."""

import datetime

import plotly.express as px
import streamlit as st

from app.config import APP_ICON, APP_TITLE, DB_PATH
from app.database import get_all, init_db
from app.reports import (
    applications_per_week,
    source_breakdown,
    status_breakdown,
    to_dataframe,
)


def _render_weekly_chart() -> None:
    """Render the Applications per Week bar chart."""
    st.subheader("Applications per Week")
    default_start = datetime.date.today() - datetime.timedelta(days=90)
    col1, col2 = st.columns(2)
    start = col1.date_input("From", value=default_start)
    end = col2.date_input("To", value=datetime.date.today())

    all_apps = get_all(DB_PATH, include_archived=True)
    df = to_dataframe([a for a in all_apps if start <= a.date_applied <= end])
    if df.empty:
        st.info("No applications in this date range.")
        return

    weekly = applications_per_week(df)
    weekly["week_ending"] = weekly["week_ending"].dt.strftime("%m/%d/%Y")
    fig = px.bar(
        weekly,
        x="week_ending",
        y="count",
        labels={"week_ending": "Week Ending", "count": "Applications"},
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)


def _render_status_chart() -> None:
    """Render the Status Breakdown donut chart (active applications only)."""
    st.subheader("Status Breakdown")
    active_apps = get_all(DB_PATH, include_archived=False)
    df = to_dataframe(active_apps)
    if df.empty:
        st.info("No active applications.")
        return

    breakdown = status_breakdown(df)
    nonzero = breakdown[breakdown["count"] > 0]
    total = breakdown["count"].sum()
    fig = px.pie(
        nonzero,
        values="count",
        names="status",
        hole=0.4,
        title=f"Active applications by status (total: {total})",
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_source_chart() -> None:
    """Render the Source Breakdown horizontal bar chart (all-time)."""
    st.subheader("Source Breakdown")
    all_apps = get_all(DB_PATH, include_archived=True)
    df = to_dataframe(all_apps)
    if df.empty:
        st.info("No applications yet.")
        return

    breakdown = source_breakdown(df)
    fig = px.bar(
        breakdown,
        x="count",
        y="source",
        orientation="h",
        labels={"count": "Applications", "source": "Source"},
    )
    st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    """Render the Reports page."""
    st.set_page_config(page_title=f"Reports — {APP_TITLE}", page_icon=APP_ICON)
    init_db(DB_PATH)
    st.title("Reports")

    _render_weekly_chart()
    st.divider()
    _render_status_chart()
    st.divider()
    _render_source_chart()


main()
