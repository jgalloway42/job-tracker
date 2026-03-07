"""Home page — dashboard for the Job Application Tracker."""

import streamlit as st

from app.base_page import BasePage
from app.config import APP_ICON, APP_TITLE, DB_PATH
from app.database import get_all
from app.models import Status

_OFFER_STATUSES = {Status.OFFER, Status.OFFER_ACCEPTED, Status.OFFER_DECLINED}


class HomePage(BasePage):
    """Dashboard showing key application metrics."""

    def _body(self) -> None:
        st.title(f"{APP_ICON} {APP_TITLE}")

        all_apps = get_all(DB_PATH, include_archived=True)
        active = [a for a in all_apps if not a.archived]

        total = len(all_apps)
        offers = sum(1 for a in all_apps if a.status in _OFFER_STATUSES)
        advanced = sum(1 for a in all_apps if a.status != Status.APPLIED)
        response_rate = round(advanced / total * 100, 1) if total > 0 else 0.0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Applications", total)
        col2.metric("Active Pipeline", len(active))
        col3.metric("Offers Received", offers)
        col4.metric("Response Rate", f"{response_rate}%")


HomePage().run()
