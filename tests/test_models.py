"""Tests for app/models.py — Status, Source enums and Application dataclass."""

from datetime import date, datetime

from app.models import ARCHIVED_STATUSES, Application, Source, Status


class TestStatus:
    """Tests for the Status enum."""

    def test_all_values_present(self):
        """Assert all 10 expected status values are defined."""
        expected = {
            "Applied",
            "Phone Screen",
            "Interview",
            "Final Round",
            "Offer",
            "Offer Accepted",
            "Offer Declined",
            "Not Selected",
            "Withdrawn",
            "No Response",
        }
        assert {s.value for s in Status} == expected

    def test_count(self):
        """Assert exactly 10 status values exist."""
        assert len(Status) == 10

    def test_is_str(self):
        """Assert Status members are string instances."""
        for status in Status:
            assert isinstance(status, str)

    def test_named_members(self):
        """Assert specific member names resolve to correct values."""
        assert Status.APPLIED == "Applied"
        assert Status.PHONE_SCREEN == "Phone Screen"
        assert Status.INTERVIEW == "Interview"
        assert Status.FINAL_ROUND == "Final Round"
        assert Status.OFFER == "Offer"
        assert Status.OFFER_ACCEPTED == "Offer Accepted"
        assert Status.OFFER_DECLINED == "Offer Declined"
        assert Status.NOT_SELECTED == "Not Selected"
        assert Status.WITHDRAWN == "Withdrawn"
        assert Status.NO_RESPONSE == "No Response"


class TestSource:
    """Tests for the Source enum."""

    def test_all_values_present(self):
        """Assert all 5 expected source values are defined."""
        expected = {"LinkedIn", "Company Site", "Indeed", "Referral", "Other"}
        assert {s.value for s in Source} == expected

    def test_count(self):
        """Assert exactly 5 source values exist."""
        assert len(Source) == 5

    def test_is_str(self):
        """Assert Source members are string instances."""
        for source in Source:
            assert isinstance(source, str)

    def test_named_members(self):
        """Assert specific member names resolve to correct values."""
        assert Source.LINKEDIN == "LinkedIn"
        assert Source.COMPANY_SITE == "Company Site"
        assert Source.INDEED == "Indeed"
        assert Source.REFERRAL == "Referral"
        assert Source.OTHER == "Other"


class TestArchivedStatuses:
    """Tests for the ARCHIVED_STATUSES set."""

    def test_contains_not_selected(self):
        """Assert NOT_SELECTED triggers archiving."""
        assert Status.NOT_SELECTED in ARCHIVED_STATUSES

    def test_contains_withdrawn(self):
        """Assert WITHDRAWN triggers archiving."""
        assert Status.WITHDRAWN in ARCHIVED_STATUSES

    def test_size(self):
        """Assert exactly 2 archived statuses exist."""
        assert len(ARCHIVED_STATUSES) == 2


def _make_application(status: Status) -> Application:
    """Helper to create a minimal Application with a given status."""
    return Application(
        company="Acme Corp",
        job_title="Engineer",
        date_applied=date(2025, 1, 15),
        status=status,
        source=Source.LINKEDIN,
    )


class TestApplication:
    """Tests for the Application dataclass."""

    def test_archived_when_not_selected(self):
        """Application with Not Selected status must set archived=True."""
        app = _make_application(Status.NOT_SELECTED)
        assert app.archived is True

    def test_archived_when_withdrawn(self):
        """Application with Withdrawn status must set archived=True."""
        app = _make_application(Status.WITHDRAWN)
        assert app.archived is True

    def test_not_archived_when_applied(self):
        """Application with Applied status must set archived=False."""
        app = _make_application(Status.APPLIED)
        assert app.archived is False

    def test_not_archived_for_all_active_statuses(self):
        """All statuses outside ARCHIVED_STATUSES must yield archived=False."""
        active_statuses = set(Status) - ARCHIVED_STATUSES
        for status in active_statuses:
            assert _make_application(status).archived is False

    def test_all_fields_present(self):
        """Assert all required fields exist on the Application dataclass."""
        now = datetime.utcnow()
        app = Application(
            company="Acme Corp",
            job_title="Engineer",
            date_applied=date(2025, 1, 15),
            status=Status.APPLIED,
            source=Source.LINKEDIN,
            job_url="https://example.com",
            notes="Great role",
            created_at=now,
            updated_at=now,
            id=42,
        )
        assert app.company == "Acme Corp"
        assert app.job_title == "Engineer"
        assert app.date_applied == date(2025, 1, 15)
        assert app.status == Status.APPLIED
        assert app.source == Source.LINKEDIN
        assert app.job_url == "https://example.com"
        assert app.notes == "Great role"
        assert app.archived is False
        assert app.created_at == now
        assert app.updated_at == now
        assert app.id == 42

    def test_optional_fields_default_to_none_or_empty(self):
        """Optional fields should have sensible defaults when omitted."""
        app = _make_application(Status.APPLIED)
        assert app.job_url == ""
        assert app.notes == ""
        assert app.created_at is None
        assert app.updated_at is None
        assert app.id is None
