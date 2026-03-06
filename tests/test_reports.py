"""Tests for app/reports.py."""

from datetime import date

import pandas as pd

from app.models import Application, Source, Status
from app.reports import (
    applications_per_week,
    source_breakdown,
    status_breakdown,
    to_dataframe,
)


def make_app(
    company: str = "Acme",
    job_title: str = "Dev",
    date_applied: date = date(2025, 1, 2),
    status: Status = Status.APPLIED,
    source: Source = Source.LINKEDIN,
) -> Application:
    """Create a minimal Application for testing."""
    return Application(
        company=company,
        job_title=job_title,
        date_applied=date_applied,
        status=status,
        source=source,
    )


# ---------------------------------------------------------------------------
# 5a — to_dataframe
# ---------------------------------------------------------------------------


def test_to_dataframe_shape_and_dtype():
    """Three applications produce a DataFrame with correct shape and dtypes."""
    apps = [
        make_app(company="Alpha"),
        make_app(company="Beta", date_applied=date(2025, 2, 1)),
        make_app(company="Gamma", date_applied=date(2025, 3, 1)),
    ]
    df = to_dataframe(apps)
    assert df.shape[0] == 3
    assert "date_applied" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["date_applied"])


def test_to_dataframe_empty():
    """Empty input returns an empty DataFrame."""
    df = to_dataframe([])
    assert isinstance(df, pd.DataFrame)
    assert df.empty


# ---------------------------------------------------------------------------
# 5b — applications_per_week
# ---------------------------------------------------------------------------


def test_applications_per_week_four_weeks():
    """Apps spanning 4 weeks produce 4 rows with correct counts."""
    apps = [
        make_app(date_applied=date(2025, 1, 2)),  # week ending 2025-01-04
        make_app(date_applied=date(2025, 1, 3)),  # week ending 2025-01-04
        make_app(date_applied=date(2025, 1, 7)),  # week ending 2025-01-11
        # (no apps in week ending 2025-01-18)
        make_app(date_applied=date(2025, 1, 20)),  # week ending 2025-01-25
    ]
    df = to_dataframe(apps)
    result = applications_per_week(df)

    assert list(result.columns) == ["week_ending", "count"]
    assert len(result) == 4
    assert list(result["count"]) == [2, 1, 0, 1]


def test_applications_per_week_all_saturdays():
    """All week_ending values fall on a Saturday (dayofweek == 5)."""
    apps = [
        make_app(date_applied=date(2025, 1, 2)),
        make_app(date_applied=date(2025, 1, 7)),
        make_app(date_applied=date(2025, 1, 20)),
    ]
    df = to_dataframe(apps)
    result = applications_per_week(df)
    assert (result["week_ending"].dt.dayofweek == 5).all()


# ---------------------------------------------------------------------------
# 5c — status_breakdown
# ---------------------------------------------------------------------------


def test_status_breakdown_all_statuses_present():
    """All 10 statuses appear in output even when only 3 are represented."""
    apps = [
        make_app(status=Status.APPLIED),
        make_app(status=Status.APPLIED),
        make_app(status=Status.INTERVIEW),
        make_app(status=Status.OFFER),
    ]
    df = to_dataframe(apps)
    result = status_breakdown(df)

    assert list(result.columns) == ["status", "count"]
    assert len(result) == len(Status)
    counts = dict(zip(result["status"], result["count"]))
    assert counts[Status.APPLIED.value] == 2
    assert counts[Status.INTERVIEW.value] == 1
    assert counts[Status.OFFER.value] == 1
    assert counts[Status.PHONE_SCREEN.value] == 0


# ---------------------------------------------------------------------------
# 5d — source_breakdown
# ---------------------------------------------------------------------------


def test_source_breakdown_all_sources_present():
    """All 5 sources appear in output even when only 2 are represented."""
    apps = [
        make_app(source=Source.LINKEDIN),
        make_app(source=Source.LINKEDIN),
        make_app(source=Source.REFERRAL),
    ]
    df = to_dataframe(apps)
    result = source_breakdown(df)

    assert list(result.columns) == ["source", "count"]
    assert len(result) == len(Source)
    counts = dict(zip(result["source"], result["count"]))
    assert counts[Source.LINKEDIN.value] == 2
    assert counts[Source.REFERRAL.value] == 1
    assert counts[Source.INDEED.value] == 0
