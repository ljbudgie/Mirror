"""burgess.py — The one question, and the three answers.

This module is the accountability core of Mirror. It applies the Burgess
Principle to an institution's response and classifies it as one of three
outcomes:

    SOVEREIGN  — a named human individually reviewed the specific facts
                 before institutional power was exercised.
    NULL       — no individual human review took place. The decision was
                 processed, not considered.
    AMBIGUOUS  — vague process language ("human oversight", "reviewed in line
                 with policy") without confirming a named reviewer looked at
                 the person's specific facts.

The framework is deterministic and local-first: no network, no accounts, no
tracking. It aligns Mirror with the Burgess Principle framework (v2.6.6).

Legal basis: it operationalises the "meaningful human involvement" requirement
in the Data (Use and Access) Act 2025 s.80 / UK GDPR Articles 22A–22D
(in force 5 February 2026) and EU AI Act Article 14. A NULL finding has
statutory weight and a documented administrative-law consequence: an act taken
without required individual human review may be void ab initio
(HM Treasury v Ahmed (No. 2) [2010] UKSC 5; R (Majera) v SSHD [2021] UKSC 46).

Burgess Principle is a registered accountability methodology (UK00004343685).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

# ── The binary question ──────────────────────────────────────────────────────

BINARY_QUESTION = (
    "Was a named human being's mind applied to the specific facts of this "
    "person's case before institutional power was exercised?"
)

# The plain-English form Mirror invites the user to ask an institution.
PLAIN_QUESTION = (
    "Was a human member of the team able to personally review the specific "
    "facts of my specific situation?"
)

# ── Legal foundations ────────────────────────────────────────────────────────

LEGAL_FOUNDATIONS: dict[str, str] = {
    "DUAA 2025 s.80": (
        "Data (Use and Access) Act 2025, s.80 (in force 5 February 2026) — "
        "defines an unlawful automated decision as one made without meaningful "
        "human involvement, and gives the affected person a right to "
        "representations, to a named human reviewer with authority to change "
        "the outcome, and to contest the decision."
    ),
    "UK GDPR Articles 22A–22D": (
        "UK GDPR Articles 22A–22D (as enacted by the Data (Use and Access) "
        "Act 2025) — the statutory requirement for meaningful human "
        "involvement in significant automated decisions."
    ),
    "EU AI Act Article 14": (
        "EU AI Act, Article 14 — mandates effective human oversight of "
        "high-risk AI systems."
    ),
    "HM Treasury v Ahmed (No. 2) [2010] UKSC 5": (
        "Acts taken without required authority are void, not merely voidable."
    ),
    "R (Majera) v SSHD [2021] UKSC 46": (
        "The consequence matters more than the label: an unlawful act cannot "
        "found enforceable rights against the individual."
    ),
}

# The evidence a response must contain to count as SOVEREIGN.
SOVEREIGN_EVIDENCE: dict[str, str] = {
    "named_reviewer": "A named human reviewer.",
    "role": "Their role or professional capacity.",
    "specific_facts": "The specific facts they reviewed about your case.",
    "timing": "Confirmation this happened before the decision affected you.",
    "authority": "Confirmation they had authority to change the outcome.",
}


# ── Outcomes ─────────────────────────────────────────────────────────────────


class Outcome(str, Enum):
    """The three possible answers to the Burgess binary question."""

    SOVEREIGN = "SOVEREIGN"
    NULL = "NULL"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass
class BurgessResult:
    """The outcome of classifying an institution's response."""

    outcome: Outcome
    matched_criteria: list[str] = field(default_factory=list)
    missing_criteria: list[str] = field(default_factory=list)
    rationale: str = ""
    guidance: str = ""


# ── Signal detection ─────────────────────────────────────────────────────────

# Language that positively evidences each SOVEREIGN criterion.
_CRITERION_PATTERNS: dict[str, list[str]] = {
    "role": [
        r"\bteam\b", r"\bofficer\b", r"\bmanager\b", r"\bcaseworker\b",
        r"\bcase worker\b", r"\badviser\b", r"\badvisor\b", r"\bclinician\b",
        r"\bconsultant\b", r"\breviewer\b", r"\bassessor\b", r"\bhandler\b",
        r"\bin our [a-z ]+ team\b", r"\brole\b", r"\bcapacity\b",
    ],
    "specific_facts": [
        r"\byour specific\b", r"\bspecific facts\b", r"\byour case\b",
        r"\byour circumstances\b", r"\byour situation\b", r"\byour application\b",
        r"\bindividually\b", r"\byour individual\b", r"\bthe details of your\b",
        r"\byour particular\b", r"\bpersonally reviewed\b",
        r"\bpersonally considered\b", r"\bpersonally handled\b",
    ],
    "timing": [
        r"\bbefore the decision\b", r"\bbefore this decision\b",
        r"\bbefore we (?:made|reached|took)\b", r"\bprior to the decision\b",
        r"\bprior to (?:making|reaching|any)\b", r"\bbefore any (?:action|decision)\b",
        r"\bbefore the outcome\b", r"\breviewed .* before\b",
    ],
    "authority": [
        r"\bauthority to (?:change|overturn|amend|vary)\b",
        r"\bable to change the outcome\b", r"\bcan change the (?:outcome|decision)\b",
        r"\bpower to (?:change|overturn|amend)\b", r"\bdiscretion to\b",
        r"\bauthorised to (?:change|overturn|amend|decide)\b",
        r"\bempowered to\b",
    ],
}

# Titles + a following capitalised name, e.g. "Dr Sarah Chen", "Ms Patel".
_TITLE_NAME = re.compile(
    r"\b(?:Dr|Mr|Mrs|Ms|Miss|Prof|Professor|Sir|Dame)\.?\s+[A-Z][a-z]+"
)
# Two consecutive capitalised words, e.g. "Sarah Chen" — a heuristic full name.
_FULL_NAME = re.compile(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b")
# Explicit "reviewed/handled by <Name>" phrasing.
_REVIEWED_BY_NAME = re.compile(
    r"\b(?:reviewed|handled|assessed|considered|decided|checked)\s+by\s+"
    r"(?:Dr|Mr|Mrs|Ms|Miss|Prof|Professor)?\.?\s*[A-Z][a-z]+",
)

# Common words that look like names but are not people.
_NAME_STOPWORDS = {
    "Universal Credit", "Home Office", "Subject Access", "Data Protection",
    "Information Commissioner", "Freedom of", "Burgess Principle",
    "Mandatory Reconsideration", "Financial Ombudsman", "Trading Standards",
    "Health Service", "National Health",
}

# Language that indicates NO individual human review (→ NULL).
_NULL_SIGNALS = [
    r"\bautomated\b", r"\bautomatically\b", r"\bsystem[- ]?generated\b",
    r"\bgenerated by (?:our|the) system\b", r"\bno human\b",
    r"\bnot reviewed by a (?:human|person)\b", r"\bcannot name\b",
    r"\bunable to name\b", r"\bcannot identify (?:the|any) (?:reviewer|person)\b",
    r"\bbulk[- ]?processed\b", r"\bbulk processing\b", r"\balgorithm(?:ically)?\b",
    r"\bprocessed by (?:the|our) (?:system|algorithm|computer)\b",
    r"\bno individual (?:human )?review\b", r"\bwithout human\b",
    r"\bfully automated\b", r"\bsolely automated\b",
]

# Vague process language that never names a reviewer or facts (→ AMBIGUOUS).
_VAGUE_SIGNALS = [
    r"\bhuman oversight\b", r"\bin line with (?:our )?policy\b",
    r"\bin accordance with (?:our )?(?:policy|procedures?)\b",
    r"\bhuman review layer\b", r"\bsubject to human review\b",
    r"\bour (?:usual |standard )?process(?:es)?\b", r"\bour procedures?\b",
    r"\breviewed in line\b", r"\bappropriate (?:checks|oversight)\b",
    r"\bquality checks\b",
]


def _matches_any(patterns: list[str], text: str) -> bool:
    return any(re.search(p, text) for p in patterns)


def _has_named_reviewer(original: str) -> bool:
    """Detect a named human reviewer using conservative heuristics."""
    if _TITLE_NAME.search(original) or _REVIEWED_BY_NAME.search(original):
        return True
    for match in _FULL_NAME.finditer(original):
        if match.group(0) not in _NAME_STOPWORDS:
            return True
    return False


def classify_response(text: str) -> BurgessResult:
    """Classify an institution's response under the Burgess Principle.

    Args:
        text: The institution's reply, in its own words. This is the answer to
            the plain-English question Mirror invites the user to ask.

    Returns:
        A :class:`BurgessResult` giving the outcome (SOVEREIGN / NULL /
        AMBIGUOUS), which SOVEREIGN criteria were evidenced, which are missing,
        a short rationale, and the recommended next step.
    """
    original = text or ""
    lowered = original.lower()

    criteria: dict[str, bool] = {
        "named_reviewer": _has_named_reviewer(original),
        "role": _matches_any(_CRITERION_PATTERNS["role"], lowered),
        "specific_facts": _matches_any(_CRITERION_PATTERNS["specific_facts"], lowered),
        "timing": _matches_any(_CRITERION_PATTERNS["timing"], lowered),
        "authority": _matches_any(_CRITERION_PATTERNS["authority"], lowered),
    }
    matched = [k for k, v in criteria.items() if v]
    missing = [k for k, v in criteria.items() if not v]

    null_signal = _matches_any(_NULL_SIGNALS, lowered)
    vague_signal = _matches_any(_VAGUE_SIGNALS, lowered)

    # An explicit statement of automated-only / no individual review is NULL,
    # unless the institution also names a reviewer who looked at the facts.
    if null_signal and not (criteria["named_reviewer"] and criteria["specific_facts"]):
        outcome = Outcome.NULL
        rationale = (
            "The response indicates the decision was processed without an "
            "individual human reviewing the specific facts."
        )
    # SOVEREIGN requires a named reviewer, the specific facts they reviewed,
    # and either the timing (before the decision) or authority to change it.
    elif (
        criteria["named_reviewer"]
        and criteria["specific_facts"]
        and (criteria["timing"] or criteria["authority"])
    ):
        outcome = Outcome.SOVEREIGN
        rationale = (
            "A named human is confirmed to have reviewed the specific facts "
            "with the timing or authority the framework requires."
        )
    else:
        outcome = Outcome.AMBIGUOUS
        if vague_signal:
            rationale = (
                "The response uses vague process language without confirming a "
                "named reviewer looked at the specific facts of the case."
            )
        else:
            rationale = (
                "The response does not evidence all of the criteria needed to "
                "confirm meaningful human review."
            )

    return BurgessResult(
        outcome=outcome,
        matched_criteria=matched,
        missing_criteria=missing,
        rationale=rationale,
        guidance=guidance_for(outcome),
    )


def guidance_for(outcome: Outcome) -> str:
    """Return the recommended next step for a Burgess outcome."""
    if outcome is Outcome.SOVEREIGN:
        return (
            "Record this as SOVEREIGN. Keep the reviewer's name and role, the "
            "facts they considered, and the confirmation they acted before the "
            "decision with authority to change it. If you still disagree with "
            "the outcome, challenge its substance — the process itself is sound."
        )
    if outcome is Outcome.NULL:
        return (
            "Record this as NULL. This is the documented starting point for "
            "escalation, not a final verdict. Request individual human review "
            "by a named person with authority to change the outcome before any "
            "further action is taken. Under the Data (Use and Access) Act 2025 "
            "s.80 / UK GDPR Articles 22A–22D you have a right to representations "
            "and to contest the decision; downstream action founded on a NULL "
            "process may have no lawful basis (void ab initio)."
        )
    return (
        "Record this as AMBIGUOUS. Ask the institution to confirm the "
        "reviewer's name, their role, the specific facts they reviewed, that "
        "this happened before the decision, and that they had authority to "
        "change it. Treat it as NULL until they can confirm all of these."
    )
