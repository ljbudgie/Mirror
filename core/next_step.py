"""next_step.py — One step. Just one.

Mirror never overwhelms. Whatever your situation, whatever stage you're at,
it gives you exactly one thing to do next. Not ten. Not a list. One.

When that step is done, come back. Mirror will give you the next one.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Stage(str, Enum):
    """Where the user currently is in the process."""

    INITIAL = "initial"                  # Nothing sent yet
    AWAITING_RESPONSE = "awaiting"       # Communication sent; waiting to hear back
    DEADLINE_APPROACHING = "approaching" # Deadline is within 5 working days
    DEADLINE_PASSED = "passed"           # Statutory deadline has been missed
    RESPONSE_RECEIVED = "received"       # They replied; user needs next action
    UNSATISFIED = "unsatisfied"          # Response received but not acceptable
    ESCALATED = "escalated"              # Complaint raised with regulator/ombudsman


@dataclass
class NextStep:
    """A single, concrete next action for the user."""

    action: str          # What to do — one sentence
    detail: str          # A little more about why and how
    template_key: str    # Which template to use (may be empty string)
    stage_after: Stage   # What stage the user will be in once this is done


# ── Step logic ───────────────────────────────────────────────────────────────

# Maps (domain, stage) → NextStep.
# Each domain has at least an INITIAL step.
_STEP_MAP: dict[tuple[str, Stage], NextStep] = {
    # ── enforcement ──────────────────────────────────────────────────────────
    ("enforcement", Stage.INITIAL): NextStep(
        action="Send a Subject Access Request to the organisation involved.",
        detail=(
            "Before anything else, find out what they know. A Subject Access Request "
            "compels them to show you everything they hold about you. Once you have "
            "that, you can see exactly what happened from their side — and spot any "
            "errors or omissions."
        ),
        template_key="sar_request",
        stage_after=Stage.AWAITING_RESPONSE,
    ),
    ("enforcement", Stage.DEADLINE_PASSED): NextStep(
        action="Send a formal reminder and file a complaint with the ICO.",
        detail=(
            "They had 30 days to respond. That time has passed. Send the reminder "
            "template now and, at the same time, file a complaint with the "
            "Information Commissioner's Office. You do not need to wait."
        ),
        template_key="sar_overdue",
        stage_after=Stage.ESCALATED,
    ),
    ("enforcement", Stage.RESPONSE_RECEIVED): NextStep(
        action="Read the response carefully and note anything that is wrong, missing, or surprising.",
        detail=(
            "Go through what they sent you. If data is missing, inaccurate, or they "
            "have refused to provide something, that is your next thread to pull."
        ),
        template_key="",
        stage_after=Stage.UNSATISFIED,
    ),
    ("enforcement", Stage.UNSATISFIED): NextStep(
        action="Write to the organisation disputing their response.",
        detail=(
            "Set out clearly and calmly what is wrong with their response. "
            "Ask them to correct it within 14 days. Keep a copy of everything."
        ),
        template_key="dispute_response",
        stage_after=Stage.AWAITING_RESPONSE,
    ),

    # ── benefits ─────────────────────────────────────────────────────────────
    ("benefits", Stage.INITIAL): NextStep(
        action="Request a Mandatory Reconsideration of the decision.",
        detail=(
            "This is the first formal step. You must ask the DWP to look at "
            "the decision again before you can appeal. You have one month from "
            "the date of the decision letter. Write to them today."
        ),
        template_key="mandatory_reconsideration",
        stage_after=Stage.AWAITING_RESPONSE,
    ),
    ("benefits", Stage.UNSATISFIED): NextStep(
        action="Appeal the Mandatory Reconsideration outcome to an independent tribunal.",
        detail=(
            "If the MR has not changed the decision, you can now appeal. "
            "Use the HMCTS online appeal service. You have one month from "
            "the date of the MR notice."
        ),
        template_key="tribunal_appeal",
        stage_after=Stage.ESCALATED,
    ),

    # ── housing ──────────────────────────────────────────────────────────────
    ("housing", Stage.INITIAL): NextStep(
        action="Write to your landlord formally setting out the problem.",
        detail=(
            "A written letter or email creates a record. State what is wrong, "
            "when you first raised it, and what you are asking them to do. "
            "Give them a reasonable deadline — 14 days for urgent repairs, "
            "28 days otherwise."
        ),
        template_key="landlord_complaint",
        stage_after=Stage.AWAITING_RESPONSE,
    ),
    ("housing", Stage.DEADLINE_PASSED): NextStep(
        action="Report the problem to your local council's housing department.",
        detail=(
            "Your landlord has not responded. The council has powers to inspect "
            "and enforce repairs. Send them the written evidence of your complaint "
            "and the lack of response."
        ),
        template_key="council_referral",
        stage_after=Stage.ESCALATED,
    ),

    # ── platform ─────────────────────────────────────────────────────────────
    ("platform", Stage.INITIAL): NextStep(
        action="Submit a formal written complaint to the platform.",
        detail=(
            "Before using any external body, you must give the platform a chance "
            "to respond. Write to their complaints or legal team — not just "
            "customer support. Ask for the reasons for the decision in writing, "
            "and state that you believe it was made in error."
        ),
        template_key="platform_complaint",
        stage_after=Stage.AWAITING_RESPONSE,
    ),
    ("platform", Stage.UNSATISFIED): NextStep(
        action="Submit a Subject Access Request to the platform.",
        detail=(
            "Alongside your complaint, ask for all the data they hold on you — "
            "including any internal notes or flags on your account. "
            "This often reveals the real reason for the decision."
        ),
        template_key="sar_request",
        stage_after=Stage.AWAITING_RESPONSE,
    ),
    ("platform", Stage.ESCALATED): NextStep(
        action="File a complaint with the ICO about the platform's data handling.",
        detail=(
            "If the platform has not responded or has refused to provide "
            "adequate reasons, the ICO can investigate. File your complaint "
            "at ico.org.uk/make-a-complaint."
        ),
        template_key="ico_complaint",
        stage_after=Stage.ESCALATED,
    ),

    # ── medical ──────────────────────────────────────────────────────────────
    ("medical", Stage.INITIAL): NextStep(
        action="Ask the healthcare provider for written reasons and a named human review of the decision.",
        detail=(
            "If this involves hearing support, an assistive device, health data, "
            "or clinical access, start by asking the Patient Experience or "
            "Information Governance team to confirm who reviewed your specific "
            "facts, what records or device data were used, and what route you can "
            "use to challenge the decision."
        ),
        template_key="medical_device_access_request",
        stage_after=Stage.AWAITING_RESPONSE,
    ),
    ("medical", Stage.RESPONSE_RECEIVED): NextStep(
        action="Challenge the decision in writing if the reasons do not show specific human review.",
        detail=(
            "Use the response to identify what is missing: named reviewer, records "
            "considered, device or audiology data used, equality adjustments, and "
            "appeal or complaints route. Ask for the decision to be reconsidered "
            "against your specific facts."
        ),
        template_key="audiology_decision_challenge",
        stage_after=Stage.AWAITING_RESPONSE,
    ),
    ("medical", Stage.DEADLINE_PASSED): NextStep(
        action="Send a formal complaint about the lack of response.",
        detail=(
            "If the provider has not acknowledged or answered, escalate through the "
            "local NHS complaints route. Keep the focus on the missing human review, "
            "the records or device data used, and the impact on your access needs."
        ),
        template_key="assistive_technology_complaint",
        stage_after=Stage.ESCALATED,
    ),
    ("medical", Stage.UNSATISFIED): NextStep(
        action="Refer your complaint to the Parliamentary and Health Service Ombudsman.",
        detail=(
            "If the provider's response is unsatisfactory, the PHSO can "
            "investigate. You need to have gone through the local complaints "
            "process first. Go to ombudsman.org.uk."
        ),
        template_key="phso_referral",
        stage_after=Stage.ESCALATED,
    ),

    # ── cross-ecosystem support workflows ────────────────────────────────────
    ("platform", Stage.RESPONSE_RECEIVED): NextStep(
        action="Request the device, account, or moderation data behind the platform decision.",
        detail=(
            "If a platform, app, or connected-device account has restricted access, "
            "ask for the moderation data, flags, scores, and human-review notes "
            "used in the decision. This keeps the next step evidence-based and "
            "local to you."
        ),
        template_key="device_data_access_request",
        stage_after=Stage.AWAITING_RESPONSE,
    ),
    ("employment", Stage.RESPONSE_RECEIVED): NextStep(
        action="Ask for the reasonable adjustment decision to be reviewed in writing.",
        detail=(
            "If your employer, school, or institution refused support connected to "
            "disability, hearing, haptics, or assistive technology, ask for a named "
            "human review of your specific facts and the adjustment you need."
        ),
        template_key="reasonable_adjustment_request",
        stage_after=Stage.AWAITING_RESPONSE,
    ),

    # ── credit ───────────────────────────────────────────────────────────────
    ("credit", Stage.INITIAL): NextStep(
        action="Request your statutory credit report and identify the error.",
        detail=(
            "Get your free statutory credit report from all three Credit Reference "
            "Agencies — Experian, Equifax, and TransUnion. Check each one carefully. "
            "Once you know what is wrong and where, you can dispute it."
        ),
        template_key="credit_report_request",
        stage_after=Stage.AWAITING_RESPONSE,
    ),
    ("credit", Stage.RESPONSE_RECEIVED): NextStep(
        action="Write to the creditor and the Credit Reference Agency disputing the entry.",
        detail=(
            "Set out clearly why the entry is wrong and what evidence you have. "
            "They must investigate and respond. If they do not agree, you can "
            "add a Notice of Correction to your file."
        ),
        template_key="credit_dispute",
        stage_after=Stage.AWAITING_RESPONSE,
    ),
    ("credit", Stage.UNSATISFIED): NextStep(
        action="Escalate your complaint to the Financial Ombudsman Service.",
        detail=(
            "If the firm has not resolved your complaint within 8 weeks, "
            "you can take it to the Financial Ombudsman for free. "
            "They can order the firm to correct records and pay compensation."
        ),
        template_key="fos_complaint",
        stage_after=Stage.ESCALATED,
    ),

    # ── employment ───────────────────────────────────────────────────────────
    ("employment", Stage.INITIAL): NextStep(
        action="Raise a formal grievance with your employer in writing.",
        detail=(
            "Put your complaint in writing and submit it to HR or your line "
            "manager's manager. State what happened, when, and what outcome you "
            "want. Your employer must follow a fair grievance procedure."
        ),
        template_key="grievance_letter",
        stage_after=Stage.AWAITING_RESPONSE,
    ),
    ("employment", Stage.UNSATISFIED): NextStep(
        action="Contact ACAS to start Early Conciliation.",
        detail=(
            "Before you can bring a claim to an Employment Tribunal, you must "
            "notify ACAS. Early Conciliation is free and pauses the tribunal "
            "clock while ACAS tries to help you reach an agreement."
        ),
        template_key="",
        stage_after=Stage.ESCALATED,
    ),

    # ── immigration ──────────────────────────────────────────────────────────
    ("immigration", Stage.INITIAL): NextStep(
        action="Note the date on the refusal letter and check your appeal deadline immediately.",
        detail=(
            "Immigration deadlines are strict and often short — sometimes just "
            "14 days. Do not wait. Check whether you have a right of appeal and, "
            "if so, prepare your appeal documents now."
        ),
        template_key="immigration_appeal_prep",
        stage_after=Stage.AWAITING_RESPONSE,
    ),
    ("immigration", Stage.DEADLINE_APPROACHING): NextStep(
        action="Submit your appeal to the First-tier Tribunal (Immigration and Asylum Chamber).",
        detail=(
            "Your deadline is close. Submit your appeal through the HMCTS portal "
            "now — do not wait for the last day. Include every piece of supporting "
            "evidence you have."
        ),
        template_key="immigration_appeal",
        stage_after=Stage.AWAITING_RESPONSE,
    ),

    # ── consumer ─────────────────────────────────────────────────────────────
    ("consumer", Stage.INITIAL): NextStep(
        action="Write a formal letter of complaint to the company.",
        detail=(
            "Email or letter — both are valid. State what went wrong, what you "
            "bought, when you bought it, and what you want them to do. "
            "Quote the Consumer Rights Act 2015. Give them 14 days to respond."
        ),
        template_key="consumer_complaint",
        stage_after=Stage.AWAITING_RESPONSE,
    ),
    ("consumer", Stage.DEADLINE_PASSED): NextStep(
        action="Escalate to the relevant ombudsman or trading standards.",
        detail=(
            "The company has not responded. Depending on the sector, you can "
            "go to a sector ombudsman (energy, telecoms, financial) or report "
            "to Trading Standards via Citizens Advice."
        ),
        template_key="ombudsman_referral",
        stage_after=Stage.ESCALATED,
    ),
    ("consumer", Stage.UNSATISFIED): NextStep(
        action="Consider a chargeback claim through your bank or credit card provider.",
        detail=(
            "If you paid by credit card, Section 75 of the Consumer Credit Act "
            "makes the card provider jointly liable for purchases over £100. "
            "For debit card payments, a chargeback may still be possible."
        ),
        template_key="chargeback_request",
        stage_after=Stage.AWAITING_RESPONSE,
    ),
}

# Generic fallback for any combination not in the map
_DEFAULT_STEP = NextStep(
    action="Send a formal written complaint to the organisation involved.",
    detail=(
        "Start by putting your complaint in writing. This creates a record, "
        "establishes a timeline, and gives the organisation the chance to resolve "
        "things before you escalate. Be clear, calm, and specific."
    ),
    template_key="generic_complaint",
    stage_after=Stage.AWAITING_RESPONSE,
)


def get_next_step(domain: str, stage: Stage = Stage.INITIAL) -> NextStep:
    """Return exactly one next step for this domain and stage.

    Args:
        domain: One of the DOMAINS from conversation.py.
        stage:  Where the user currently is in the process. Defaults to INITIAL.

    Returns:
        A single :class:`NextStep` — never a list, never a menu.
    """
    return _STEP_MAP.get((domain, stage), _DEFAULT_STEP)
