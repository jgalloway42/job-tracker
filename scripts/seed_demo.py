"""Seed script — populates demo.db with fictional job application data.

Run via:  python scripts/seed_demo.py
Or:       make seed

Wipes and recreates demo.db each time (idempotent).
All company names and URLs are entirely fictional.
"""

import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pylint: disable=wrong-import-position
from app.database import add_application, init_db
from app.models import Application, Source, Status

# pylint: enable=wrong-import-position

DB_PATH = "demo.db"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _days_ago(n: int) -> date:
    return date(2026, 3, 6) - timedelta(days=n)


# ---------------------------------------------------------------------------
# Seed data — ~42 records, all statuses, all sources, 3 duplicate pairs
# ---------------------------------------------------------------------------

RECORDS = [
    # ---- Applied (8) -------------------------------------------------------
    ("Nexovate", "Backend Engineer", _days_ago(3), "Applied", "LinkedIn", "", ""),
    ("Quantora", "Platform Engineer", _days_ago(5), "Applied", "Indeed", "", ""),
    ("Synaptiq", "DevOps Engineer", _days_ago(7), "Applied", "Company Site", "", ""),
    (
        "Veltrix",
        "Site Reliability Engineer",
        _days_ago(8),
        "Applied",
        "LinkedIn",
        "",
        "",
    ),
    (
        "Aeronex",
        "Cloud Architect",
        _days_ago(10),
        "Applied",
        "Referral",
        "",
        "Applied via Jane Smith referral",
    ),
    ("Pinnacle AI", "ML Engineer", _days_ago(11), "Applied", "Other", "", ""),
    ("Heliux", "Software Engineer", _days_ago(12), "Applied", "LinkedIn", "", ""),
    ("Crestwave", "Data Engineer", _days_ago(14), "Applied", "Indeed", "", ""),
    # ---- Phone Screen (4) --------------------------------------------------
    (
        "Orbix",
        "Backend Developer",
        _days_ago(15),
        "Phone Screen",
        "LinkedIn",
        "",
        "Call with recruiter scheduled",
    ),
    (
        "Luminary Tech",
        "Full Stack Engineer",
        _days_ago(18),
        "Phone Screen",
        "Company Site",
        "",
        "",
    ),
    (
        "Stratus Systems",
        "Software Engineer II",
        _days_ago(20),
        "Phone Screen",
        "Referral",
        "",
        "",
    ),
    ("Neurovex", "Systems Engineer", _days_ago(22), "Phone Screen", "Indeed", "", ""),
    # ---- Interview (4) -----------------------------------------------------
    (
        "Axionix",
        "Senior Backend Engineer",
        _days_ago(25),
        "Interview",
        "LinkedIn",
        "",
        "Two rounds completed",
    ),
    (
        "Prismia",
        "Engineering Lead",
        _days_ago(28),
        "Interview",
        "Referral",
        "",
        "Panel interview next week",
    ),
    (
        "Cloudara",
        "Infrastructure Engineer",
        _days_ago(30),
        "Interview",
        "Company Site",
        "",
        "",
    ),
    ("Zenovo", "Platform Developer", _days_ago(33), "Interview", "Other", "", ""),
    # ---- Final Round (3) ---------------------------------------------------
    (
        "Brightforge",
        "Principal Engineer",
        _days_ago(36),
        "Final Round",
        "LinkedIn",
        "",
        "Onsite next Tuesday",
    ),
    (
        "DataNova",
        "Data Platform Lead",
        _days_ago(40),
        "Final Round",
        "Referral",
        "",
        "",
    ),
    (
        "Opticore",
        "Software Architect",
        _days_ago(42),
        "Final Round",
        "Company Site",
        "",
        "",
    ),
    # ---- Offer (2) ---------------------------------------------------------
    (
        "Nexovate",
        "Staff Engineer",
        _days_ago(45),
        "Offer",
        "LinkedIn",
        "",
        "Offer received — reviewing",
    ),
    (
        "Blueshift Labs",
        "Senior Software Engineer",
        _days_ago(48),
        "Offer",
        "Indeed",
        "",
        "",
    ),
    # ---- Offer Accepted (1) ------------------------------------------------
    (
        "Veltrix",
        "Engineering Manager",
        _days_ago(55),
        "Offer Accepted",
        "Referral",
        "",
        "Start date: 2026-04-01",
    ),
    # ---- Offer Declined (1) ------------------------------------------------
    (
        "Synaptiq",
        "Principal Architect",
        _days_ago(58),
        "Offer Declined",
        "Company Site",
        "",
        "Comp below target",
    ),
    # ---- Not Selected (6) --------------------------------------------------
    ("Aeronex", "DevOps Lead", _days_ago(62), "Not Selected", "LinkedIn", "", ""),
    (
        "Pinnacle AI",
        "Research Engineer",
        _days_ago(65),
        "Not Selected",
        "Indeed",
        "",
        "",
    ),
    ("Heliux", "Backend Lead", _days_ago(68), "Not Selected", "Referral", "", ""),
    ("Crestwave", "Platform Engineer", _days_ago(72), "Not Selected", "Other", "", ""),
    (
        "Orbix",
        "Senior DevOps Engineer",
        _days_ago(75),
        "Not Selected",
        "LinkedIn",
        "",
        "",
    ),
    (
        "Luminary Tech",
        "Infrastructure Lead",
        _days_ago(78),
        "Not Selected",
        "Company Site",
        "",
        "",
    ),
    # ---- Withdrawn (4) -----------------------------------------------------
    (
        "Stratus Systems",
        "Cloud Engineer",
        _days_ago(80),
        "Withdrawn",
        "Indeed",
        "",
        "Accepted other offer",
    ),
    (
        "Neurovex",
        "Site Reliability Lead",
        _days_ago(83),
        "Withdrawn",
        "Referral",
        "",
        "",
    ),
    (
        "Axionix",
        "Platform Architect",
        _days_ago(86),
        "Withdrawn",
        "LinkedIn",
        "",
        "Role eliminated",
    ),
    (
        "Prismia",
        "VP of Engineering",
        _days_ago(88),
        "Withdrawn",
        "Other",
        "",
        "Over-leveled for this role",
    ),
    # ---- No Response (7) ---------------------------------------------------
    (
        "Cloudara",
        "Staff Backend Engineer",
        _days_ago(50),
        "No Response",
        "Indeed",
        "",
        "",
    ),
    ("Zenovo", "Senior Engineer", _days_ago(53), "No Response", "LinkedIn", "", ""),
    (
        "Brightforge",
        "Backend Engineer",
        _days_ago(56),
        "No Response",
        "Company Site",
        "",
        "",
    ),
    ("DataNova", "Analytics Engineer", _days_ago(60), "No Response", "Other", "", ""),
    (
        "Opticore",
        "Full Stack Developer",
        _days_ago(63),
        "No Response",
        "Referral",
        "",
        "",
    ),
    (
        "Quantora",
        "Cloud Platform Engineer",
        _days_ago(67),
        "No Response",
        "LinkedIn",
        "",
        "",
    ),
    ("Nexovate", "Data Scientist", _days_ago(70), "No Response", "Indeed", "", ""),
    # ---- Duplicate pair 1: Nexovate / Backend Engineer ---------------------
    # Intentional duplicate of record[0] (same company + job_title, different date)
    (
        "Nexovate",
        "Backend Engineer",
        _days_ago(1),
        "Applied",
        "LinkedIn",
        "",
        "Reapplied after role reopened",
    ),
    # ---- Duplicate pair 2: Blueshift Labs / Data Analyst -------------------
    ("Blueshift Labs", "Data Analyst", _days_ago(30), "Applied", "Indeed", "", ""),
    (
        "Blueshift Labs",
        "Data Analyst",
        _days_ago(10),
        "Phone Screen",
        "LinkedIn",
        "",
        "Recruiter reached out separately",
    ),
    # ---- Duplicate pair 3: Cloudara / Infrastructure Engineer --------------
    # Intentional duplicate of record[14] (same company + job_title, different date)
    (
        "Cloudara",
        "Infrastructure Engineer",
        _days_ago(15),
        "Applied",
        "Company Site",
        "",
        "Second attempt after first ghosted",
    ),
]


def seed() -> None:
    """Wipe demo.db and repopulate with fictional seed data."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    init_db(DB_PATH)

    for company, job_title, date_applied, status, source, job_url, notes in RECORDS:
        add_application(
            Application(
                company=company,
                job_title=job_title,
                date_applied=date_applied,
                status=Status(status),
                source=Source(source),
                job_url=job_url,
                notes=notes,
            ),
            DB_PATH,
        )

    print(f"demo.db seeded with {len(RECORDS)} records.")


if __name__ == "__main__":
    seed()
