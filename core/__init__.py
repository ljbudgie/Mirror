# Mirror — see where you stand.
# Core toolkit modules for conversational intake, rights mapping,
# the Burgess three-outcome classification engine, next-step generation,
# template rendering, commitment hashing, timeline tracking, and optional
# local AI integration.
"""Mirror core toolkit.

The Burgess accountability engine is exported at package level so callers can
run the full local-first loop — classify an institution's reply and get the
single next step — straight from ``core``::

    from core import classify_response, advise_from_response, Stage

Heavier, optional integrations (for example the local AI adapter) are kept in
their own submodules and imported on demand.
"""

from core.burgess import (
    BINARY_QUESTION,
    LEGAL_FOUNDATIONS,
    PLAIN_QUESTION,
    SOVEREIGN_EVIDENCE,
    BurgessResult,
    Outcome,
    classify_response,
    guidance_for,
)
from core.next_step import (
    NextStep,
    Stage,
    advise_from_response,
    get_next_step,
    outcome_to_stage,
)

__all__ = [
    # Burgess engine
    "BINARY_QUESTION",
    "PLAIN_QUESTION",
    "LEGAL_FOUNDATIONS",
    "SOVEREIGN_EVIDENCE",
    "Outcome",
    "BurgessResult",
    "classify_response",
    "guidance_for",
    # Next-step engine and the Burgess bridge
    "Stage",
    "NextStep",
    "get_next_step",
    "outcome_to_stage",
    "advise_from_response",
]
