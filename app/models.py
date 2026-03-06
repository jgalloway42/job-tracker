"""Data models for the Job Application Tracker."""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


class Status(str, Enum):
    """Ordered enumeration of application pipeline statuses."""

    APPLIED = "Applied"
    PHONE_SCREEN = "Phone Screen"
    INTERVIEW = "Interview"
    FINAL_ROUND = "Final Round"
    OFFER = "Offer"
    OFFER_ACCEPTED = "Offer Accepted"
    OFFER_DECLINED = "Offer Declined"
    NOT_SELECTED = "Not Selected"
    WITHDRAWN = "Withdrawn"
    NO_RESPONSE = "No Response"


class Source(str, Enum):
    """Enumeration of job discovery sources."""

    LINKEDIN = "LinkedIn"
    COMPANY_SITE = "Company Site"
    INDEED = "Indeed"
    REFERRAL = "Referral"
    OTHER = "Other"


ARCHIVED_STATUSES = {Status.NOT_SELECTED, Status.WITHDRAWN}


@dataclass
class Application:
    """Represents a single job application record."""

    company: str
    job_title: str
    date_applied: date
    status: Status
    source: Source
    job_url: str = ""
    notes: str = ""
    archived: bool = field(default=False, init=True)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None

    def __post_init__(self) -> None:
        """Compute archived flag from the current status."""
        self.archived = self.status in ARCHIVED_STATUSES
