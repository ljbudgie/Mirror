"""timeline.py — Time matters. Let's keep track of it.

Every formal process has a clock. Mirror watches it for you.

DSAR (Subject Access Request): 30 calendar days from receipt.
FOI request:                   20 working days from receipt.
Complaint acknowledgement:     3 working days (NHS), varies elsewhere.
Mandatory Reconsideration:     1 month from decision date.
Employment Tribunal:           3 months minus 1 day from the act complained of.

When a deadline is close, Mirror tells you. When it has passed, Mirror gives
you the escalation step automatically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional


class DeadlineStatus(str, Enum):
    """How close — or how overdue — a deadline is."""

    ON_TRACK = "on_track"          # More than 5 working days remaining
    APPROACHING = "approaching"    # 5 working days or fewer remaining
    MISSED = "missed"              # Deadline has passed with no response
    RESOLVED = "resolved"          # Deadline no longer relevant (response received)


@dataclass
class Deadline:
    """A single tracked deadline."""

    label: str                    # Human-readable name, e.g. "SAR response"
    domain: str                   # Which domain this belongs to
    deadline_date: date           # The date by which a response is due
    sent_date: date               # When the communication was sent
    responded: bool = False       # Has the other party responded?
    notes: str = ""


@dataclass
class DeadlineReport:
    """The current status of a tracked deadline."""

    deadline: Deadline
    status: DeadlineStatus
    days_remaining: int           # Negative if overdue
    message: str                  # A human-readable summary
    escalation_template: str = "" # Template key to use if escalation is needed


# ── Working-day calculator ────────────────────────────────────────────────────

def _add_working_days(start: date, working_days: int) -> date:
    """Add a number of working days (Mon–Fri) to a start date."""
    current = start
    days_added = 0
    while days_added < working_days:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Monday=0, Friday=4
            days_added += 1
    return current


def _working_days_between(start: date, end: date) -> int:
    """Count working days between two dates (exclusive of start, inclusive of end)."""
    count = 0
    current = start + timedelta(days=1)
    while current <= end:
        if current.weekday() < 5:
            count += 1
        current += timedelta(days=1)
    return count


# ── Deadline factories ────────────────────────────────────────────────────────

def dsar_deadline(sent_date: date, domain: str = "general") -> Deadline:
    """Create a DSAR (Subject Access Request) deadline.

    The response must arrive within 30 calendar days of the request being received.
    """
    return Deadline(
        label="Subject Access Request response",
        domain=domain,
        deadline_date=sent_date + timedelta(days=30),
        sent_date=sent_date,
        notes="UK GDPR Article 12(3): response required within one calendar month.",
    )


def foi_deadline(sent_date: date, domain: str = "general") -> Deadline:
    """Create an FOI (Freedom of Information) deadline.

    The response must arrive within 20 working days.
    """
    return Deadline(
        label="FOI request response",
        domain=domain,
        deadline_date=_add_working_days(sent_date, 20),
        sent_date=sent_date,
        notes="Freedom of Information Act 2000 s.10: response within 20 working days.",
    )


def complaint_deadline(sent_date: date, domain: str = "general", working_days: int = 3) -> Deadline:
    """Create a complaint acknowledgement deadline.

    NHS: 3 working days. Other organisations: varies (default 3 working days).
    """
    return Deadline(
        label="Complaint acknowledgement",
        domain=domain,
        deadline_date=_add_working_days(sent_date, working_days),
        sent_date=sent_date,
        notes=f"Acknowledgement expected within {working_days} working days.",
    )


def mr_deadline(decision_date: date) -> Deadline:
    """Create a Mandatory Reconsideration request deadline.

    The MR must be requested within one calendar month of the decision.
    Note: 'One month' is interpreted as the same day the following month;
    for month-end edge cases we use 30 days as a safe approximation.
    """
    return Deadline(
        label="Mandatory Reconsideration request",
        domain="benefits",
        deadline_date=decision_date + timedelta(days=30),
        sent_date=decision_date,
        notes=(
            "Social Security Act 1998 s.9: MR must be requested within one "
            "month of the decision. Acting earlier is strongly advised."
        ),
    )


def employment_tribunal_deadline(act_date: date) -> Deadline:
    """Create an Employment Tribunal claim deadline.

    Claims must generally be brought within 3 months minus 1 day of the act.
    ACAS Early Conciliation pauses this clock — seek advice early.
    """
    # Use modulo arithmetic so the calculation is correct for all months.
    # Adding 3 months in 0-indexed month space, then converting back to 1-indexed.
    zero_indexed_month = act_date.month - 1
    new_month = (zero_indexed_month + 3) % 12 + 1
    year_offset = (zero_indexed_month + 3) // 12
    three_months = act_date.replace(year=act_date.year + year_offset, month=new_month)
    deadline = three_months - timedelta(days=1)
    return Deadline(
        label="Employment Tribunal claim",
        domain="employment",
        deadline_date=deadline,
        sent_date=act_date,
        notes=(
            "Employment Rights Act 1996: claim within 3 months minus 1 day. "
            "ACAS Early Conciliation pauses this clock."
        ),
    )


# ── Status checker ────────────────────────────────────────────────────────────

_ESCALATION_MAP: dict[str, str] = {
    "Subject Access Request response": "sar_overdue",
    "FOI request response":            "foi_overdue",
    "Complaint acknowledgement":       "complaint_overdue",
    "Mandatory Reconsideration request": "mr_deadline_warning",
    "Employment Tribunal claim":       "tribunal_deadline_warning",
}


def check_deadline(deadline: Deadline, today: Optional[date] = None) -> DeadlineReport:
    """Evaluate the current status of a deadline.

    Args:
        deadline: The :class:`Deadline` to check.
        today:    Override today's date (useful for testing).

    Returns:
        A :class:`DeadlineReport` with status, days remaining, and a message.
    """
    today = today or date.today()

    if deadline.responded:
        return DeadlineReport(
            deadline=deadline,
            status=DeadlineStatus.RESOLVED,
            days_remaining=0,
            message=f"'{deadline.label}' — marked as resolved.",
        )

    days_remaining = (deadline.deadline_date - today).days

    if days_remaining < 0:
        status = DeadlineStatus.MISSED
        message = (
            f"The deadline for '{deadline.label}' passed "
            f"{abs(days_remaining)} day(s) ago. "
            "You can escalate now."
        )
        escalation = _ESCALATION_MAP.get(deadline.label, "generic_escalation")
    elif _working_days_between(today, deadline.deadline_date) <= 5:
        status = DeadlineStatus.APPROACHING
        message = (
            f"The deadline for '{deadline.label}' is in "
            f"{days_remaining} day(s) — on {deadline.deadline_date}. "
            "If you haven't heard anything, consider sending a chaser."
        )
        escalation = ""
    else:
        status = DeadlineStatus.ON_TRACK
        message = (
            f"'{deadline.label}' — response due by {deadline.deadline_date} "
            f"({days_remaining} day(s) remaining)."
        )
        escalation = ""

    return DeadlineReport(
        deadline=deadline,
        status=status,
        days_remaining=days_remaining,
        message=message,
        escalation_template=escalation,
    )
