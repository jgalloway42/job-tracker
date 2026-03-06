"""Reporting and analytics functions for the Job Application Tracker."""

import dataclasses

import pandas as pd

from app.models import Application, Source, Status


def to_dataframe(applications: list[Application]) -> pd.DataFrame:
    """Convert a list of Application objects to a pandas DataFrame."""
    if not applications:
        return pd.DataFrame()
    records = [dataclasses.asdict(app) for app in applications]
    df = pd.DataFrame(records)
    df["date_applied"] = pd.to_datetime(df["date_applied"])
    return df


def applications_per_week(df: pd.DataFrame) -> pd.DataFrame:
    """Group applications by week-ending Saturday, including zero-count weeks."""
    weekly = df.set_index("date_applied").resample("W-SAT").size().reset_index()
    weekly.columns = pd.Index(["week_ending", "count"])
    return weekly


def status_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Return counts per status; all statuses appear even with count 0."""
    counts = df["status"].value_counts()
    all_statuses = [s.value for s in Status]
    result = pd.DataFrame({"status": all_statuses})
    result["count"] = result["status"].map(counts).fillna(0).astype(int)
    return result


def source_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Return counts per source; all sources appear even with count 0."""
    counts = df["source"].value_counts()
    all_sources = [s.value for s in Source]
    result = pd.DataFrame({"source": all_sources})
    result["count"] = result["source"].map(counts).fillna(0).astype(int)
    return result
