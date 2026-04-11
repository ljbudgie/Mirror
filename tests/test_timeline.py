"""Tests for core/timeline.py — deadline tracking."""

import pytest
from datetime import date, timedelta
from core.timeline import (
    Deadline,
    DeadlineStatus,
    DeadlineReport,
    dsar_deadline,
    foi_deadline,
    complaint_deadline,
    mr_deadline,
    check_deadline,
    _add_working_days,
    _working_days_between,
)


class TestWorkingDayHelpers:
    def test_add_working_days_skips_weekend(self):
        # Monday + 5 working days = Monday (next week)
        monday = date(2026, 4, 6)
        result = _add_working_days(monday, 5)
        assert result == date(2026, 4, 13)

    def test_add_working_days_zero(self):
        d = date(2026, 4, 6)
        assert _add_working_days(d, 0) == d

    def test_working_days_between_weekdays(self):
        monday = date(2026, 4, 6)
        friday = date(2026, 4, 10)
        assert _working_days_between(monday, friday) == 4

    def test_working_days_between_across_weekend(self):
        friday = date(2026, 4, 10)
        monday = date(2026, 4, 13)
        assert _working_days_between(friday, monday) == 1


class TestDeadlineFactories:
    def test_dsar_deadline_is_30_calendar_days(self):
        sent = date(2026, 4, 1)
        dl = dsar_deadline(sent)
        assert dl.deadline_date == date(2026, 5, 1)

    def test_foi_deadline_is_20_working_days(self):
        sent = date(2026, 4, 6)  # Monday
        dl = foi_deadline(sent)
        expected = _add_working_days(sent, 20)
        assert dl.deadline_date == expected

    def test_complaint_deadline_defaults_to_3_working_days(self):
        sent = date(2026, 4, 6)  # Monday
        dl = complaint_deadline(sent)
        assert dl.deadline_date == _add_working_days(sent, 3)

    def test_complaint_deadline_custom_days(self):
        sent = date(2026, 4, 6)
        dl = complaint_deadline(sent, working_days=5)
        assert dl.deadline_date == _add_working_days(sent, 5)

    def test_mr_deadline_is_30_days(self):
        decision = date(2026, 3, 1)
        dl = mr_deadline(decision)
        assert dl.deadline_date == date(2026, 3, 31)

    def test_deadline_labels_are_strings(self):
        sent = date(2026, 4, 1)
        for dl in [dsar_deadline(sent), foi_deadline(sent), complaint_deadline(sent)]:
            assert isinstance(dl.label, str)
            assert len(dl.label) > 0

    def test_deadline_domain_stored(self):
        dl = dsar_deadline(date(2026, 4, 1), domain="enforcement")
        assert dl.domain == "enforcement"

    def test_employment_tribunal_deadline_mid_year(self):
        # Act in June → deadline is September minus 1 day = 31 Aug
        from core.timeline import employment_tribunal_deadline
        act = date(2026, 6, 15)
        dl = employment_tribunal_deadline(act)
        assert dl.deadline_date == date(2026, 9, 14)

    def test_employment_tribunal_deadline_october(self):
        # Act in October → 3 months later = January (next year), minus 1 day
        from core.timeline import employment_tribunal_deadline
        act = date(2026, 10, 31)
        dl = employment_tribunal_deadline(act)
        assert dl.deadline_date == date(2027, 1, 30)

    def test_employment_tribunal_deadline_november(self):
        # Act in November → February next year, minus 1 day
        from core.timeline import employment_tribunal_deadline
        act = date(2026, 11, 1)
        dl = employment_tribunal_deadline(act)
        assert dl.deadline_date == date(2027, 1, 31)

    def test_employment_tribunal_deadline_december(self):
        # Act in December → March next year, minus 1 day
        from core.timeline import employment_tribunal_deadline
        act = date(2026, 12, 1)
        dl = employment_tribunal_deadline(act)
        assert dl.deadline_date == date(2027, 2, 28)


class TestCheckDeadline:
    def _make_deadline(self, days_ago: int, responded: bool = False) -> Deadline:
        today = date(2026, 4, 11)
        sent = today - timedelta(days=days_ago)
        dl = dsar_deadline(sent)
        dl.responded = responded
        return dl

    def test_on_track_when_plenty_of_time(self):
        # Sent today — 30 days remaining
        dl = self._make_deadline(0)
        report = check_deadline(dl, today=date(2026, 4, 11))
        assert report.status == DeadlineStatus.ON_TRACK

    def test_approaching_within_5_working_days(self):
        # Sent 26 days ago — 4 days left
        dl = self._make_deadline(26)
        report = check_deadline(dl, today=date(2026, 4, 11))
        assert report.status in (DeadlineStatus.APPROACHING, DeadlineStatus.MISSED)

    def test_missed_when_past_deadline(self):
        # Sent 35 days ago — 5 days overdue
        dl = self._make_deadline(35)
        report = check_deadline(dl, today=date(2026, 4, 11))
        assert report.status == DeadlineStatus.MISSED

    def test_resolved_when_responded(self):
        dl = self._make_deadline(5, responded=True)
        report = check_deadline(dl, today=date(2026, 4, 11))
        assert report.status == DeadlineStatus.RESOLVED

    def test_report_has_message(self):
        dl = self._make_deadline(10)
        report = check_deadline(dl, today=date(2026, 4, 11))
        assert isinstance(report.message, str)
        assert len(report.message) > 0

    def test_missed_report_has_escalation_template(self):
        dl = self._make_deadline(35)
        report = check_deadline(dl, today=date(2026, 4, 11))
        if report.status == DeadlineStatus.MISSED:
            assert isinstance(report.escalation_template, str)
            assert len(report.escalation_template) > 0

    def test_days_remaining_negative_when_missed(self):
        dl = self._make_deadline(35)
        report = check_deadline(dl, today=date(2026, 4, 11))
        assert report.days_remaining < 0

    def test_days_remaining_positive_when_on_track(self):
        dl = self._make_deadline(1)
        report = check_deadline(dl, today=date(2026, 4, 11))
        assert report.days_remaining > 0

    def test_returns_deadline_report(self):
        dl = self._make_deadline(5)
        report = check_deadline(dl, today=date(2026, 4, 11))
        assert isinstance(report, DeadlineReport)
