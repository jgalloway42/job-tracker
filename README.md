[![CI](https://github.com/jgalloway42/job-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/jgalloway42/job-tracker/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![Pylint](https://img.shields.io/badge/pylint-10.0%2F10-brightgreen)

# Job Application Tracker

A local-first job application tracking tool built with Streamlit and SQLite. Designed for personal use during a job search — log applications, monitor pipeline progress, visualize trends, and keep your data off third-party servers.

---

## Features

- **Dashboard** — KPI cards for total applications, active pipeline, offers received, and response rate
- **Add applications** — Form with duplicate detection; warns before inserting a record with the same company and job title
- **View & filter** — Filter by date range, status, source, and archived state; paginated table with CSV export
- **Edit applications** — Update any field; `archived` flag recomputes automatically from status
- **Reports** — Weekly application trend (bar chart), status breakdown (donut), source breakdown (horizontal bar)
- **Dedup CLI** — Interactive command-line tool to find and resolve duplicate records (`make dedup`)
- **Demo database** — Seeded with 40+ fictional applications so the app runs immediately after cloning

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | [Streamlit](https://streamlit.io) |
| Database | SQLite (local file via `sqlite3`) |
| Data / charts | pandas, Plotly |
| Config | python-dotenv |
| Quality | black, pylint (10.0/10), pytest (100% coverage) |
| CI | GitHub Actions |

---

## Project Structure

```
job-tracker/
├── app/
│   ├── config.py        # Typed constants loaded from .env
│   ├── database.py      # All CRUD + dedup functions
│   ├── models.py        # Application dataclass, Status/Source enums
│   └── reports.py       # DataFrame transforms for charts
├── pages/
│   ├── 1_Add_Application.py
│   ├── 2_View_Applications.py
│   ├── 3_Edit_Application.py
│   └── 4_Reports.py
├── scripts/
│   └── seed_demo.py     # Regenerates demo.db with fictional data
├── tests/               # 61 tests, 100% coverage
├── Home.py              # Dashboard entry point
├── demo.db              # Seeded demo database (committed)
└── .github/workflows/
    └── ci.yml           # Format + lint + test on every push
```

---

## Setup

```bash
# 1. Create and activate a Python 3.11 environment
conda create -n jobtracker python=3.11
conda activate jobtracker

# 2. Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# 3. Configure environment
cp .env.example .env
# The default .env.example points to demo.db — no edits needed to run immediately

# 4. Launch the app
streamlit run Home.py
```

The app opens at `http://localhost:8501` with demo data pre-loaded.

To use your own database, set `DB_PATH=jobs.db` in `.env`. `jobs.db` is gitignored and stays on your machine.

---

## Development

```bash
make format   # Auto-format with black
make lint     # Pylint — must score 10.0/10
make test     # pytest with 100% coverage gate
make check    # format + lint + test (full quality gate)
make run      # Launch Streamlit
make seed     # Regenerate demo.db with fresh fictional data
make dedup    # Interactive CLI to find and resolve duplicate records
```

---

## Data Model

Applications move through a 10-stage status pipeline:

```
Applied → Phone Screen → Interview → Final Round → Offer → Offer Accepted
                                                          → Offer Declined
       → Not Selected  (auto-archived)
       → Withdrawn     (auto-archived)
       → No Response
```

The `archived` flag is computed automatically — any application in `Not Selected` or `Withdrawn` status is excluded from active pipeline views by default. Archived records are retained for reporting (unemployment logging use case).

---

## Architecture Notes

- **No ORM** — raw `sqlite3` with a thin `_row_to_application()` helper; keeps the dependency footprint minimal
- **Config isolation** — all env vars flow through `app/config.py`; page files never call `os.getenv()` directly
- **Dedup key** — `company + job_title` only; `date_applied` is excluded to allow legitimate re-applications after time has passed
- **Hard delete only via CLI** — the UI has no delete button; deletion is restricted to the `make dedup` flow to prevent accidental data loss
- **demo.db committed** — treated as a fixture so the app is immediately runnable after cloning, with no setup required beyond `pip install`

---

## Testing

```
61 tests across 4 modules
100% line coverage enforced on every CI run
pylint 10.0/10 on all source and test files
```

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```
