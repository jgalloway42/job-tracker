# Job Application Tracker — Engineering Spec
**Handoff document for Claude Code — build function by function, test as you go.**

---

## Overview

A local-first job application tracking tool with a Streamlit frontend and SQLite backend. Designed for personal use during a job search, with unemployment logging as a secondary use case. A `demo.db` with seeded fictional data is committed to the repo; the real database (`jobs.db`) lives only on the developer's machine.

---

## Repository Structure

```
job-tracker/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   └── reports.py
├── pages/
│   ├── 1_Add_Application.py
│   ├── 2_View_Applications.py
│   ├── 3_Edit_Application.py
│   └── 4_Reports.py
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_models.py
│   └── test_reports.py
├── scripts/
│   └── seed_demo.py
├── Home.py
├── .env.example
├── .gitignore
├── Makefile
├── requirements.txt
├── requirements-dev.txt
├── .pylintrc
└── README.md
```

---

## Configuration

### `.env.example` (committed to repo)
```
DB_PATH=jobs.db
APP_TITLE=Job Application Tracker
APP_ICON=💼
WEEK_ENDING_DAY=SAT
PAGE_SIZE=25
```

### `.env` (gitignored — developer creates locally from example)
- `DB_PATH=jobs.db` for local use
- `DB_PATH=demo.db` for demo/testing

### `app/config.py`
- Loads `.env` via `python-dotenv`
- Exposes typed constants: `DB_PATH`, `APP_TITLE`, `APP_ICON`, `WEEK_ENDING_DAY`, `PAGE_SIZE`
- All other modules import config values from here — never read env vars directly elsewhere

**Test:** `tests/test_config.py`
- Assert all expected keys are present and correctly typed
- Assert defaults are applied when `.env` values are absent

---

## Data Model

### `applications` table

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| `company` | TEXT | NOT NULL | |
| `job_title` | TEXT | NOT NULL | |
| `date_applied` | DATE | NOT NULL | ISO format YYYY-MM-DD |
| `status` | TEXT | NOT NULL | Must be a value from the status enum |
| `source` | TEXT | NOT NULL | Must be a value from the source enum |
| `job_url` | TEXT | | Optional |
| `notes` | TEXT | | Optional |
| `archived` | INTEGER | NOT NULL DEFAULT 0 | 0=active, 1=archived (set automatically when status = "Not Selected" or "Withdrawn") |
| `created_at` | TIMESTAMP | NOT NULL | Auto-set on insert |
| `updated_at` | TIMESTAMP | NOT NULL | Auto-updated on any change |

### Status Enum (ordered, displayed as dropdown in UI)
1. Applied
2. Phone Screen
3. Interview
4. Final Round
5. Offer
6. Offer Accepted
7. Offer Declined
8. Not Selected ← triggers `archived = 1`
9. Withdrawn ← triggers `archived = 1`
10. No Response

### Source Enum
- LinkedIn
- Company Site
- Indeed
- Referral
- Other

---

## Build Order

Work through each section completely — implement, then write and pass all tests — before moving to the next.

---

### Step 1 — Project Scaffolding

**Tasks:**
- Create all directories and empty `__init__.py` files
- Create `.gitignore` with: `.env`, `jobs.db`, `__pycache__/`, `.pytest_cache/`, `*.egg-info/`, `dist/`, `.coverage`
- Create `requirements.txt` (loose pins):
  ```
  streamlit>=1.35
  pandas>=2.0
  plotly>=5.0
  python-dotenv>=1.0
  ```
- Create `requirements-dev.txt`:
  ```
  black>=24.0
  pylint>=3.0
  pytest>=8.0
  pytest-cov>=5.0
  ```
- Create `.env.example` as shown above
- Create `.env` locally pointing to `demo.db` for development
- Create `.pylintrc` with `max-line-length=88`, `good-names=df,id`, score threshold not set here (enforced in Makefile)

**No tests for scaffolding — verify manually that structure matches the repo layout above.**

---

### Step 2 — `app/models.py`

**Tasks:**
- Define `Status` as a `str` enum with all 10 values above
- Define `Source` as a `str` enum with all 5 values above
- Define `ARCHIVED_STATUSES = {Status.NOT_SELECTED, Status.WITHDRAWN}`
- Define `Application` as a `dataclass`:
  - Fields: `company`, `job_title`, `date_applied`, `status`, `source`, `job_url`, `notes`, `archived`, `created_at`, `updated_at`, `id` (optional, None for new records)
  - `archived` should be computed from status via a `__post_init__` method: set `archived = True` if `status in ARCHIVED_STATUSES`

**Test:** `tests/test_models.py`
- Assert all `Status` values are present and correctly named
- Assert all `Source` values are present
- Assert `Application` with status `Not Selected` sets `archived=True`
- Assert `Application` with status `Withdrawn` sets `archived=True`
- Assert `Application` with status `Applied` sets `archived=False`
- Assert `Application` dataclass fields are all present

---

### Step 3 — `app/config.py`

**Tasks:**
- Load `.env` with `python-dotenv`
- Export: `DB_PATH: str`, `APP_TITLE: str`, `APP_ICON: str`, `WEEK_ENDING_DAY: str`, `PAGE_SIZE: int`
- Apply defaults if any value is missing from `.env`

**Test:** `tests/test_config.py`
- Monkeypatch env vars and assert correct values are returned
- Assert `PAGE_SIZE` is cast to `int`
- Assert defaults are applied when env vars are absent

---

### Step 4 — `app/database.py`

Build and test one function at a time in this order:

#### 4a. `init_db(db_path: str) -> None`
- Creates the `applications` table if it does not exist using the schema above
- Safe to call multiple times (idempotent)

**Test:** Call `init_db` twice on a temp DB, assert no error and table exists.

#### 4b. `add_application(app: Application, db_path: str) -> int`
- Inserts a new record, returns the new `id`
- Sets `created_at` and `updated_at` to current UTC timestamp
- Sets `archived` from the model's computed value

**Test:** Insert one record, assert returned `id` is an integer, assert row exists in DB with correct values.

#### 4c. `get_all(db_path: str, include_archived: bool = False) -> list[Application]`
- Returns all applications
- If `include_archived=False`, filters out records where `archived=1`
- Returns an empty list (not an error) if no records exist

**Test:**
- Insert 3 active + 1 archived record, assert `get_all` returns 3
- Assert `get_all(include_archived=True)` returns 4
- Assert empty DB returns empty list

#### 4d. `get_by_date_range(start: date, end: date, db_path: str, include_archived: bool = False) -> list[Application]`
- Returns applications where `date_applied` is between `start` and `end` inclusive

**Test:** Insert records across 3 months, assert correct subset returned for a 1-month window.

#### 4e. `get_by_status(status: Status, db_path: str) -> list[Application]`
- Returns all applications with the given status (including archived)

**Test:** Insert mixed statuses, assert only correct status returned.

#### 4f. `update_application(app: Application, db_path: str) -> None`
- Updates all fields for an existing record by `id`
- Updates `updated_at` to current UTC timestamp
- Recomputes `archived` from the new status

**Test:**
- Insert a record, update its status to `Not Selected`, assert `archived=1` in DB
- Assert `updated_at` changed

#### 4g. `find_duplicates(db_path: str) -> list[tuple[Application, Application]]`
- Scans for records sharing the same `company` + `job_title`
- Groups by `(company, job_title)`, returns pairs where count > 1
- Returns list of tuples: `(oldest_record, newer_record)` — oldest is determined by `date_applied`, then `created_at` as tiebreaker

**Test:**
- Insert 2 records with same company+title, 1 unique record
- Assert `find_duplicates` returns 1 pair
- Assert the tuple order is (oldest, newer)
- Assert unique record is not in results

#### 4h. `delete_application(id: int, db_path: str) -> None`
- Hard deletes a record by `id`
- Used only by the dedup resolution flow — not exposed in the UI directly

**Test:** Insert a record, delete it, assert it no longer exists in DB.

---

### Step 5 — `app/reports.py`

#### 5a. `to_dataframe(applications: list[Application]) -> pd.DataFrame`
- Converts a list of `Application` objects to a pandas DataFrame
- Ensures `date_applied` column is `datetime64` dtype

**Test:** Pass 3 applications, assert DataFrame shape and column dtypes.

#### 5b. `applications_per_week(df: pd.DataFrame) -> pd.DataFrame`
- Groups by week-ending Saturday using `pd.Grouper(key="date_applied", freq="W-SAT")`
- Returns DataFrame with columns: `week_ending`, `count`
- Weeks with zero applications should still appear if within the date range (use `resample` or explicit date range fill)

**Test:**
- Create applications spanning 4 weeks, assert output has 4 rows with correct counts
- Assert `week_ending` values all fall on Saturdays

#### 5c. `status_breakdown(df: pd.DataFrame) -> pd.DataFrame`
- Groups by `status`, returns DataFrame with columns: `status`, `count`
- All statuses from the enum should appear, even with count 0

**Test:** Pass applications with 3 distinct statuses, assert all 10 statuses present in output, correct counts for represented ones.

#### 5d. `source_breakdown(df: pd.DataFrame) -> pd.DataFrame`
- Same pattern as `status_breakdown` but for `source`

**Test:** Same pattern as above.

---

### Step 6 — `scripts/seed_demo.py`

**Tasks:**
- Standalone script (not imported by app), callable via `make seed`
- Creates and seeds `demo.db` (path hardcoded in script, not from config)
- Inserts ~40 fictional applications spanning the last 3 months
- Use fictional companies only — no real company names, no real URLs
- Spread across all statuses, all sources
- At least 2 intentional duplicate pairs (same company + job_title) to demonstrate dedup functionality
- Wipe and recreate `demo.db` each time the script runs (idempotent)

**No pytest tests — verify manually by running `make seed` and inspecting output.**

---

### Step 7 — Streamlit Pages

Build pages in this order. Each page imports only from `app/` — no direct DB or SQL calls in page files.

#### 7a. `Home.py` — Dashboard
- Loads all active applications via `get_all()`
- Displays 4 KPI cards: Total Applications, Active Pipeline (excludes archived), Offers Received, Response Rate (% that moved past Applied)
- No sidebar filters on this page
- Use `st.metric` for KPIs

#### 7b. `pages/1_Add_Application.py` — Add Application
- Form fields: Company (text), Job Title (text), Date Applied (date picker, default today), Status (selectbox from `Status` enum), Source (selectbox from `Source` enum), Job URL (text, optional), Notes (text area, optional)
- On submit:
  - Check for duplicates via `find_duplicates` logic (query for same company+title before insert)
  - If duplicate found: show `st.warning` with the existing record details and two buttons: "Add Anyway" and "Cancel"
  - If no duplicate (or user clicks "Add Anyway"): call `add_application()` and show `st.success`
  - If user clicks "Cancel": clear form, do nothing

#### 7c. `pages/2_View_Applications.py` — View & Query
- Sidebar filters:
  - Date range (start date / end date pickers)
  - Status multiselect (default: all active statuses)
  - Show archived toggle (default: off)
  - Source multiselect (default: all)
- Results displayed in `st.dataframe` with:
  - Sortable columns
  - Pagination via `PAGE_SIZE` from config (use manual slice + `st.selectbox` for page number)
  - Column order: Company, Job Title, Date Applied, Status, Source, Job URL, Notes
- Below table: "Export to CSV" button — downloads current filtered view as CSV via `st.download_button`
- Each row should have an "Edit" button that navigates to `pages/3_Edit_Application.py` with the record `id` passed via `st.session_state`

#### 7d. `pages/3_Edit_Application.py` — Edit Application
- Reads `id` from `st.session_state` — if not set, show "No application selected" and a back button
- Pre-populates all fields from the existing record
- Same field set as Add form
- On save: call `update_application()`, show `st.success`, clear session state
- On cancel: clear session state, return to View page
- No delete button — deletion is only via dedup flow

#### 7e. `pages/4_Reports.py` — Reports
- Section 1: **Applications per Week**
  - Date range pickers (default: last 90 days)
  - Plotly bar chart: x-axis = week ending date (Saturday), y-axis = count
  - X-axis labels formatted as `MM/DD/YYYY`
- Section 2: **Status Breakdown**
  - Plotly pie chart (donut style) of current active applications by status
  - Exclude zero-count statuses from chart (but note total in subtitle)
- Section 3: **Source Breakdown**
  - Plotly horizontal bar chart of all-time applications by source

---

### Step 8 — Dedup CLI Command

**Tasks:**
- Add a function `resolve_duplicates(db_path: str) -> None` in `app/database.py`
- Calls `find_duplicates()`, prints a formatted table of duplicate pairs to stdout
- Prompts: `"Found N duplicate pairs. Delete newer duplicates? [y/N]: "`
- If `y`: calls `delete_application()` on the newer record in each pair, prints confirmation
- If `n` or any other input: prints "No changes made." and exits
- This function is called by `make dedup` — it is not accessible via the Streamlit UI

**Test:** `tests/test_database.py` (add to existing file)
- Mock `input()` returning `"y"`, assert duplicates are deleted and originals remain
- Mock `input()` returning `"n"`, assert no records deleted
- Assert output includes the number of duplicate pairs found

---

### Step 9 — Makefile

```makefile
.PHONY: install format lint test check run seed dedup clean

install:
	pip install -r requirements.txt -r requirements-dev.txt

format:
	black app/ pages/ tests/ scripts/ Home.py

lint:
	pylint app/ pages/ tests/ scripts/ Home.py --fail-under=10.0

test:
	pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=100

check: format lint test

run:
	streamlit run Home.py

seed:
	python scripts/seed_demo.py

dedup:
	python -c "from app.database import resolve_duplicates; from app.config import DB_PATH; resolve_duplicates(DB_PATH)"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name ".coverage" -delete
```

---

### Step 10 — CI Pipeline

**File:** `.github/workflows/ci.yml`

**Trigger:** `on: push` and `on: pull_request` for all branches

**Job: `ci`**
- Runner: `ubuntu-latest`
- Python version: `3.11`

**Steps in order:**
1. Checkout repo
2. Set up Python 3.11
3. Cache pip dependencies (key on `requirements*.txt` hash)
4. `make install`
5. **Format check:** `black --check app/ pages/ tests/ scripts/ Home.py` — fails if any file would be reformatted
6. **Lint:** `make lint` — fails if pylint score < 10.0
7. **Test:** `make test` — fails if any test fails or coverage < 100%
8. Upload coverage report as artifact (optional but recommended)

**Environment variables for CI:**
- Set `DB_PATH=demo.db` in the workflow env block so tests and the app can find a database
- Do NOT store any secrets in the workflow file

**CD pipeline:** Deferred. Will be added as `.github/workflows/cd.yml` when Streamlit Community Cloud is configured. No changes to application code will be required at that time.

---

## Key Constraints & Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Delete vs archive | Archive via status | Unemployment logging requires record retention |
| Terminal statuses | Not Selected, Withdrawn | Distinct reasons for pipeline exit |
| Dedup key | company + job\_title | date_applied excluded to allow legitimate reapplications |
| Dedup resolution | Keep oldest, delete newer | Oldest record has most complete history |
| Hard delete | Only via `make dedup` CLI | Prevents accidental data loss via UI |
| DB migrations | Deferred | Handled ad hoc with a script if schema changes |
| Backup | Developer responsibility | jobs.db is gitignored; manual backup recommended |
| Python version | 3.11 only | Single version matrix keeps CI simple |
| Dependency pins | Loose (`>=`) | Flexibility over strict reproducibility |
| Pylint threshold | 10.0/10 | Greenfield project, no legacy debt |
| Test coverage | 100% | Greenfield project, no exceptions |
| CD target | Streamlit Community Cloud | Zero server config, auto-deploys from main |
| CD timing | Deferred | Add `cd.yml` when Streamlit Cloud is configured |
| Demo data | Fictional companies only | Public repo, employer-safe |
| Public repo | Yes (for Streamlit free tier) | Isolated repo, no cross-contamination with other work |

---

## Notes for Claude Code

- Build and fully test each numbered step before proceeding to the next
- Do not write Streamlit page code until all `app/` modules are complete and tested
- All imports of config values must go through `app/config.py` — never `os.getenv()` directly in page files
- `demo.db` is committed to the repo and regenerated via `make seed` — treat it as a fixture, not production data
- `jobs.db` must never appear in any commit — verify `.gitignore` is the first file created in Step 1
