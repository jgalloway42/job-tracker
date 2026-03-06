"""Tests for app/database.py."""

# pylint: disable=redefined-outer-name  # pytest fixtures intentionally shadow names
import sqlite3
import time
from datetime import date

import pytest

from app.database import (
    add_application,
    delete_application,
    find_duplicates,
    get_all,
    get_by_date_range,
    get_by_status,
    init_db,
    resolve_duplicates,
    update_application,
)
from app.models import Application, Source, Status

# ── helpers ───────────────────────────────────────────────────────────────────


def make_app(**kwargs) -> Application:
    """Return an Application with sensible defaults, overridden by kwargs."""
    defaults = {
        "company": "Acme Corp",
        "job_title": "Engineer",
        "date_applied": date(2025, 1, 15),
        "status": Status.APPLIED,
        "source": Source.LINKEDIN,
    }
    defaults.update(kwargs)
    return Application(**defaults)


@pytest.fixture()
def db(tmp_path):
    """Initialised temp database path."""
    path = str(tmp_path / "test.db")
    init_db(path)
    return path


# ── 4a: init_db ───────────────────────────────────────────────────────────────


def test_init_db_creates_table(tmp_path):
    """init_db should create the applications table."""
    path = str(tmp_path / "test.db")
    init_db(path)
    with sqlite3.connect(path) as conn:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='applications'"
        ).fetchone()
    assert row is not None


def test_init_db_is_idempotent(tmp_path):
    """Calling init_db twice must not raise and table must remain empty."""
    path = str(tmp_path / "test.db")
    init_db(path)
    init_db(path)
    with sqlite3.connect(path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    assert count == 0


# ── 4b: add_application ───────────────────────────────────────────────────────


def test_add_application_returns_int(db):
    """add_application should return an integer id."""
    assert isinstance(add_application(make_app(), db), int)


def test_add_application_row_has_correct_values(db):
    """Inserted row must reflect all Application field values."""
    app = make_app(company="TestCo", job_title="Dev", status=Status.INTERVIEW)
    app_id = add_application(app, db)
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM applications WHERE id = ?", (app_id,)
        ).fetchone()
    assert row["company"] == "TestCo"
    assert row["job_title"] == "Dev"
    assert row["status"] == "Interview"
    assert row["archived"] == 0


def test_add_application_sets_archived_for_terminal_status(db):
    """Inserting an application with an archived status must set archived=1."""
    app_id = add_application(make_app(status=Status.NOT_SELECTED), db)
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT archived FROM applications WHERE id = ?", (app_id,)
        ).fetchone()
    assert row[0] == 1


def test_add_application_trims_whitespace(db):
    """Leading/trailing whitespace in company and job_title must be stripped on insert."""
    app_id = add_application(
        make_app(company="  Acme  ", job_title="  Engineer  "), db
    )
    saved = [a for a in get_all(db) if a.id == app_id][0]
    assert saved.company == "Acme"
    assert saved.job_title == "Engineer"


# ── 4c: get_all ───────────────────────────────────────────────────────────────


def test_get_all_returns_active_only(db):
    """get_all without include_archived must exclude archived records."""
    add_application(make_app(status=Status.APPLIED), db)
    add_application(make_app(status=Status.INTERVIEW), db)
    add_application(make_app(status=Status.OFFER), db)
    add_application(make_app(status=Status.NOT_SELECTED), db)
    assert len(get_all(db)) == 3


def test_get_all_include_archived_returns_all(db):
    """get_all(include_archived=True) must return all records."""
    add_application(make_app(status=Status.APPLIED), db)
    add_application(make_app(status=Status.INTERVIEW), db)
    add_application(make_app(status=Status.OFFER), db)
    add_application(make_app(status=Status.NOT_SELECTED), db)
    assert len(get_all(db, include_archived=True)) == 4


def test_get_all_empty_db_returns_empty_list(db):
    """get_all on an empty database must return an empty list."""
    assert get_all(db) == []


# ── 4d: get_by_date_range ─────────────────────────────────────────────────────


def test_get_by_date_range_returns_correct_subset(db):
    """Only records with date_applied in [start, end] should be returned."""
    add_application(make_app(date_applied=date(2025, 1, 5)), db)
    add_application(make_app(date_applied=date(2025, 2, 10)), db)
    add_application(make_app(date_applied=date(2025, 2, 20)), db)
    add_application(make_app(date_applied=date(2025, 3, 5)), db)
    results = get_by_date_range(date(2025, 2, 1), date(2025, 2, 28), db)
    assert len(results) == 2


def test_get_by_date_range_excludes_archived_by_default(db):
    """Archived records must be excluded unless include_archived=True."""
    add_application(
        make_app(date_applied=date(2025, 2, 10), status=Status.NOT_SELECTED), db
    )
    add_application(make_app(date_applied=date(2025, 2, 15), status=Status.APPLIED), db)
    results = get_by_date_range(date(2025, 2, 1), date(2025, 2, 28), db)
    assert len(results) == 1


def test_get_by_date_range_include_archived(db):
    """include_archived=True must also return archived records in range."""
    add_application(
        make_app(date_applied=date(2025, 2, 10), status=Status.NOT_SELECTED), db
    )
    add_application(make_app(date_applied=date(2025, 2, 15), status=Status.APPLIED), db)
    results = get_by_date_range(
        date(2025, 2, 1), date(2025, 2, 28), db, include_archived=True
    )
    assert len(results) == 2


# ── 4e: get_by_status ─────────────────────────────────────────────────────────


def test_get_by_status_returns_matching_records(db):
    """Only records with the requested status should be returned."""
    add_application(make_app(status=Status.APPLIED), db)
    add_application(make_app(status=Status.APPLIED), db)
    add_application(make_app(status=Status.INTERVIEW), db)
    results = get_by_status(Status.APPLIED, db)
    assert len(results) == 2
    assert all(r.status == Status.APPLIED for r in results)


def test_get_by_status_includes_archived_records(db):
    """get_by_status must return archived records when status matches."""
    add_application(make_app(status=Status.NOT_SELECTED), db)
    results = get_by_status(Status.NOT_SELECTED, db)
    assert len(results) == 1


# ── 4f: update_application ────────────────────────────────────────────────────


def test_update_application_changes_status_and_archived(db):
    """Updating status to a terminal value must flip archived to 1 in DB."""
    app_id = add_application(make_app(status=Status.APPLIED), db)
    fetched = next(a for a in get_all(db) if a.id == app_id)
    fetched.status = Status.NOT_SELECTED
    update_application(fetched, db)
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT status, archived FROM applications WHERE id = ?", (app_id,)
        ).fetchone()
    assert row[0] == "Not Selected"
    assert row[1] == 1


def test_update_application_updates_updated_at(db):
    """updated_at must be refreshed after an update call."""
    app_id = add_application(make_app(), db)
    with sqlite3.connect(db) as conn:
        original_ts = conn.execute(
            "SELECT updated_at FROM applications WHERE id = ?", (app_id,)
        ).fetchone()[0]
    time.sleep(0.01)
    fetched = next(a for a in get_all(db) if a.id == app_id)
    update_application(fetched, db)
    with sqlite3.connect(db) as conn:
        new_ts = conn.execute(
            "SELECT updated_at FROM applications WHERE id = ?", (app_id,)
        ).fetchone()[0]
    assert new_ts > original_ts


# ── 4g: find_duplicates ───────────────────────────────────────────────────────


def test_find_duplicates_returns_one_pair(db):
    """Two records with the same company+title should produce exactly one pair."""
    add_application(
        make_app(company="DupCo", job_title="Dev", date_applied=date(2025, 1, 1)), db
    )
    add_application(
        make_app(company="DupCo", job_title="Dev", date_applied=date(2025, 2, 1)), db
    )
    add_application(make_app(company="UniqueCo", job_title="Designer"), db)
    assert len(find_duplicates(db)) == 1


def test_find_duplicates_tuple_order_is_oldest_first(db):
    """The first element of each pair must be the older record."""
    add_application(
        make_app(company="DupCo", job_title="Dev", date_applied=date(2025, 2, 1)), db
    )
    add_application(
        make_app(company="DupCo", job_title="Dev", date_applied=date(2025, 1, 1)), db
    )
    oldest, newer = find_duplicates(db)[0]
    assert oldest.date_applied < newer.date_applied


def test_find_duplicates_unique_record_not_in_results(db):
    """Records without duplicates must not appear in find_duplicates output."""
    add_application(
        make_app(company="DupCo", job_title="Dev", date_applied=date(2025, 1, 1)), db
    )
    add_application(
        make_app(company="DupCo", job_title="Dev", date_applied=date(2025, 2, 1)), db
    )
    add_application(make_app(company="UniqueCo", job_title="Designer"), db)
    pairs = find_duplicates(db)
    all_companies = {a.company for pair in pairs for a in pair}
    assert "UniqueCo" not in all_companies


def test_find_duplicates_case_insensitive(db):
    """Duplicate detection must be case-insensitive for company and job_title."""
    add_application(
        make_app(company="dupco", job_title="dev", date_applied=date(2025, 1, 1)), db
    )
    add_application(
        make_app(company="DupCo", job_title="Dev", date_applied=date(2025, 2, 1)), db
    )
    assert len(find_duplicates(db)) == 1


# ── 4h: delete_application ────────────────────────────────────────────────────


def test_delete_application_removes_record(db):
    """Deleted record must no longer exist in the database."""
    app_id = add_application(make_app(), db)
    delete_application(app_id, db)
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT id FROM applications WHERE id = ?", (app_id,)
        ).fetchone()
    assert row is None


# ── Step 8: resolve_duplicates ────────────────────────────────────────────────


def test_resolve_duplicates_no_pairs_exits_early(db, capsys):
    """resolve_duplicates with no duplicates must print count and return."""
    add_application(make_app(company="UniqueA", job_title="Dev"), db)
    resolve_duplicates(db)
    output = capsys.readouterr().out
    assert "0" in output


def test_resolve_duplicates_yes_deletes_newer(db, monkeypatch):
    """Answering 'y' must delete the newer duplicate and keep the oldest."""
    oldest_id = add_application(
        make_app(company="DupCo", job_title="Dev", date_applied=date(2025, 1, 1)), db
    )
    newer_id = add_application(
        make_app(company="DupCo", job_title="Dev", date_applied=date(2025, 2, 1)), db
    )
    monkeypatch.setattr("builtins.input", lambda _: "y")
    resolve_duplicates(db)
    all_ids = [a.id for a in get_all(db, include_archived=True)]
    assert oldest_id in all_ids
    assert newer_id not in all_ids


def test_resolve_duplicates_no_leaves_records(db, monkeypatch):
    """Answering 'n' must leave all records untouched."""
    add_application(
        make_app(company="DupCo", job_title="Dev", date_applied=date(2025, 1, 1)), db
    )
    add_application(
        make_app(company="DupCo", job_title="Dev", date_applied=date(2025, 2, 1)), db
    )
    monkeypatch.setattr("builtins.input", lambda _: "n")
    resolve_duplicates(db)
    assert len(get_all(db, include_archived=True)) == 2


def test_resolve_duplicates_output_includes_pair_count(db, capsys, monkeypatch):
    """stdout must mention the number of duplicate pairs found."""
    add_application(
        make_app(company="DupCo", job_title="Dev", date_applied=date(2025, 1, 1)), db
    )
    add_application(
        make_app(company="DupCo", job_title="Dev", date_applied=date(2025, 2, 1)), db
    )
    monkeypatch.setattr("builtins.input", lambda _: "n")
    resolve_duplicates(db)
    output = capsys.readouterr().out
    assert "1" in output
