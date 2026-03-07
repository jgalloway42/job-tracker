"""Abstract base class for all Streamlit pages."""

import os
from abc import ABC, abstractmethod

import streamlit as st

from app.config import APP_ICON, APP_TITLE, DB_PATH
from app.database import init_db


class BasePage(ABC):
    """Base class that handles shared page setup for all Streamlit pages.

    Subclasses declare a class-level ``subtitle`` and implement ``_body()``.
    Invoke a page by calling ``PageSubclass().run()`` at module level.
    """

    subtitle: str | None = None  # None → page_title = APP_TITLE

    def run(self) -> None:
        """Configure the page, initialise the DB, render body, add sidebar."""
        title = f"{self.subtitle} \u2014 {APP_TITLE}" if self.subtitle else APP_TITLE
        st.set_page_config(page_title=title, page_icon=APP_ICON, layout="wide")
        init_db(DB_PATH)
        self._body()
        with st.sidebar:
            st.divider()
            if st.button("Exit App", use_container_width=True):
                os._exit(0)  # pylint: disable=protected-access

    @abstractmethod
    def _body(self) -> None:
        """Render the page-specific content."""
