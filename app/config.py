"""Configuration module for the Job Application Tracker.

Loads environment variables from a .env file and exposes typed constants.
All other modules must import config values from here — never call
os.getenv() directly elsewhere.
"""

import os

from dotenv import load_dotenv

load_dotenv()

DB_PATH: str = os.getenv("DB_PATH", "jobs.db")
APP_TITLE: str = os.getenv("APP_TITLE", "Job Application Tracker")
APP_ICON: str = os.getenv("APP_ICON", "💼")
WEEK_ENDING_DAY: str = os.getenv("WEEK_ENDING_DAY", "SAT")
PAGE_SIZE: int = int(os.getenv("PAGE_SIZE", "25"))
