"""Database access layer for the Job Application Tracker."""

import sqlite3
from datetime import date, datetime, timezone

from app.models import ARCHIVED_STATUSES, Application, Source, Status

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS applications (
    id           INTEGER   PRIMARY KEY AUTOINCREMENT,
    company      TEXT      NOT NULL,
    job_title    TEXT      NOT NULL,
    date_applied DATE      NOT NULL,
    status       TEXT      NOT NULL,
    source       TEXT      NOT NULL,
    job_url      TEXT      NOT NULL DEFAULT '',
    notes        TEXT      NOT NULL DEFAULT '',
    archived     INTEGER   NOT NULL DEFAULT 0,
    created_at   TIMESTAMP NOT NULL,
    updated_at   TIMESTAMP NOT NULL
)
"""


def _connect(db_path: str) -> sqlite3.Connection:
    """Open a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_application(row: sqlite3.Row) -> Application:
    """Convert a sqlite3.Row to an Application dataclass instance."""
    return Application(
        id=row["id"],
        company=row["company"],
        job_title=row["job_title"],
        date_applied=date.fromisoformat(row["date_applied"]),
        status=Status(row["status"]),
        source=Source(row["source"]),
        job_url=row["job_url"],
        notes=row["notes"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def init_db(db_path: str) -> None:
    """Create the applications table if it does not exist (idempotent)."""
    with _connect(db_path) as conn:
        conn.execute(_CREATE_TABLE_SQL)


def add_application(app: Application, db_path: str) -> int:
    """Insert a new application record and return the new row id."""
    now = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO applications
                (company, job_title, date_applied, status, source,
                 job_url, notes, archived, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                app.company,
                app.job_title,
                app.date_applied.isoformat(),
                app.status.value,
                app.source.value,
                app.job_url,
                app.notes,
                int(app.archived),
                now,
                now,
            ),
        )
        return cursor.lastrowid


def get_all(db_path: str, include_archived: bool = False) -> list[Application]:
    """Return all application records, optionally including archived ones."""
    sql = "SELECT * FROM applications"
    if not include_archived:
        sql += " WHERE archived = 0"
    with _connect(db_path) as conn:
        rows = conn.execute(sql).fetchall()
    return [_row_to_application(r) for r in rows]


def get_by_date_range(
    start: date,
    end: date,
    db_path: str,
    include_archived: bool = False,
) -> list[Application]:
    """Return applications where date_applied falls between start and end inclusive."""
    sql = "SELECT * FROM applications WHERE date_applied BETWEEN ? AND ?"
    params: list = [start.isoformat(), end.isoformat()]
    if not include_archived:
        sql += " AND archived = 0"
    with _connect(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()
    return [_row_to_application(r) for r in rows]


def get_by_status(status: Status, db_path: str) -> list[Application]:
    """Return all applications with the given status, including archived ones."""
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM applications WHERE status = ?",
            (status.value,),
        ).fetchall()
    return [_row_to_application(r) for r in rows]


def update_application(app: Application, db_path: str) -> None:
    """Update all fields of an existing record by id.

    Recomputes archived from the new status value.
    """
    now = datetime.now(timezone.utc).isoformat()
    archived = int(app.status in ARCHIVED_STATUSES)
    with _connect(db_path) as conn:
        conn.execute(
            """
            UPDATE applications SET
                company      = ?,
                job_title    = ?,
                date_applied = ?,
                status       = ?,
                source       = ?,
                job_url      = ?,
                notes        = ?,
                archived     = ?,
                updated_at   = ?
            WHERE id = ?
            """,
            (
                app.company,
                app.job_title,
                app.date_applied.isoformat(),
                app.status.value,
                app.source.value,
                app.job_url,
                app.notes,
                archived,
                now,
                app.id,
            ),
        )


def find_duplicates(db_path: str) -> list[tuple[Application, Application]]:
    """Return pairs of duplicate records sharing the same company and job_title.

    Each pair is (oldest_record, newer_record), ordered by date_applied then created_at.
    """
    with _connect(db_path) as conn:
        groups = conn.execute("""
            SELECT company, job_title FROM applications
            GROUP BY company, job_title
            HAVING COUNT(*) > 1
            """).fetchall()

        pairs: list[tuple[Application, Application]] = []
        for group in groups:
            rows = conn.execute(
                """
                SELECT * FROM applications
                WHERE company = ? AND job_title = ?
                ORDER BY date_applied ASC, created_at ASC
                """,
                (group["company"], group["job_title"]),
            ).fetchall()
            apps = [_row_to_application(r) for r in rows]
            for newer in apps[1:]:
                pairs.append((apps[0], newer))

    return pairs


def delete_application(app_id: int, db_path: str) -> None:
    """Hard delete a record by id."""
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
