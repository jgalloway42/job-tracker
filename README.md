[![CI](https://github.com/jgalloway42/job-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/jgalloway42/job-tracker/actions/workflows/ci.yml)

# job-tracker

A local-first job application tracking tool with a Streamlit frontend and SQLite backend. Designed for personal use during a job search, with unemployment logging as a secondary use case.

## Features

- Log job applications with company, title, status, source, URL, and notes
- Track pipeline progress across 10 status stages
- Auto-archive applications in terminal states (Not Selected, Withdrawn)
- Duplicate detection by company + job title
- Weekly application counts, status breakdown, and source breakdown reports
- Export filtered views to CSV
- CLI dedup resolution (`make dedup`)
- Demo database with seeded fictional data committed to the repo

## Tech Stack

- **Frontend**: Streamlit
- **Database**: SQLite (local file)
- **Data**: pandas, plotly
- **Quality**: black · pylint (10.0/10) · pytest (100% coverage) · GitHub Actions CI

## Setup

```bash
# 1. Create and activate a Python 3.11 environment
conda create -n jobtracker python=3.11
conda activate jobtracker

# 2. Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# 3. Copy and configure .env
cp .env.example .env
# Edit .env — set DB_PATH=demo.db to use the seeded demo database

# 4. Run the app
streamlit run Home.py
```

## Development

```bash
make format   # auto-format with black
make lint     # pylint (must score 10.0/10)
make test     # pytest with 100% coverage gate
make check    # format + lint + test
make seed     # regenerate demo.db with fictional data
make dedup    # interactive duplicate resolution CLI
```

## Build Status

| Phase | Scope | Status |
|---|---|---|
| 1 | Scaffolding, `models.py`, `config.py` | ✅ Complete |
| 2 | `database.py` (all CRUD + dedup functions) | ✅ Complete |
| 3 | `reports.py` (DataFrame transforms) | 🔲 Pending |
| 4 | `scripts/seed_demo.py` | 🔲 Pending |
| 5 | Streamlit pages | 🔲 Pending |
| 6 | Dedup CLI (`resolve_duplicates`) | 🔲 Pending |
