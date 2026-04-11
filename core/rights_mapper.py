"""rights_mapper.py — What rights do you actually have here?

This module takes a classified domain and returns the rights that apply to
your situation. It is a map, not legal advice. Think of it as a compass —
it shows you the direction, but you decide how to walk.

Jurisdiction defaults to 'UK'. Non-UK jurisdictions return equivalent
international frameworks where Mirror knows them.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ── Data structures ──────────────────────────────────────────────────────────


@dataclass
class Right:
    """A single applicable right."""

    name: str
    description: str
    source: str       # e.g. "GDPR Article 15"
    action: str       # What this right lets the person do
    url: str = ""     # Official or trusted reference URL


@dataclass
class RightsMap:
    """The full set of rights applicable to a classified domain."""

    domain: str
    jurisdiction: str
    rights: list[Right] = field(default_factory=list)
    notes: str = ""


# ── Rights data ──────────────────────────────────────────────────────────────

# UK rights by domain.
_UK_RIGHTS: dict[str, list[Right]] = {
    "enforcement": [
        Right(
            name="Right to Know What Data Is Held About You",
            description=(
                "You can ask any public authority — including the police — "
                "for all personal data they hold on you."
            ),
            source="UK GDPR Article 15",
            action="Submit a Subject Access Request (SAR).",
            url="https://ico.org.uk/your-data-matters/your-right-to-get-copies-of-your-data/",
        ),
        Right(
            name="Right to Request Information from Public Bodies",
            description=(
                "You can ask public authorities for recorded information they hold."
            ),
            source="Freedom of Information Act 2000",
            action="Submit an FOI request.",
            url="https://www.gov.uk/make-a-freedom-of-information-request",
        ),
        Right(
            name="Right Not to Be Discriminated Against",
            description=(
                "You are protected from discrimination based on protected "
                "characteristics during any enforcement action."
            ),
            source="Equality Act 2010",
            action="Document the interaction and raise a formal complaint.",
            url="https://www.equalityhumanrights.com/equality/equality-act-2010",
        ),
    ],
    "benefits": [
        Right(
            name="Right to a Mandatory Reconsideration",
            description=(
                "Before you can appeal a benefits decision, you must ask the "
                "DWP to look at it again. This is called a Mandatory Reconsideration."
            ),
            source="Social Security Act 1998, s.9",
            action="Request a Mandatory Reconsideration within one month of the decision.",
            url="https://www.gov.uk/mandatory-reconsideration",
        ),
        Right(
            name="Right to Appeal to an Independent Tribunal",
            description=(
                "If the Mandatory Reconsideration does not change the decision, "
                "you can appeal to an independent tribunal."
            ),
            source="Tribunals, Courts and Enforcement Act 2007",
            action="Submit an appeal to HMCTS after receiving the MR outcome.",
            url="https://www.gov.uk/appeal-benefit-decision",
        ),
        Right(
            name="Right to Know What Data Is Held About You",
            description=(
                "The DWP holds a significant amount of data about you. "
                "You can request it all."
            ),
            source="UK GDPR Article 15",
            action="Submit a Subject Access Request to the DWP.",
            url="https://ico.org.uk/your-data-matters/your-right-to-get-copies-of-your-data/",
        ),
        Right(
            name="Right to Reasons for a Decision",
            description=(
                "Any decision about your benefits must be accompanied by reasons. "
                "You are entitled to a written statement of reasons."
            ),
            source="Social Security Act 1998",
            action="Write to the DWP requesting a full written statement of reasons.",
        ),
    ],
    "housing": [
        Right(
            name="Protection Against Unlawful Eviction",
            description=(
                "Your landlord must follow a legal process to end your tenancy. "
                "They cannot evict you without a court order."
            ),
            source="Protection from Eviction Act 1977; Housing Act 1988",
            action=(
                "If you have received a Section 21 or Section 8 notice, "
                "seek advice immediately. The notice starts a clock."
            ),
            url="https://england.shelter.org.uk/housing_advice/eviction",
        ),
        Right(
            name="Right to a Safe and Habitable Home",
            description=(
                "Your landlord has a legal duty to keep your home in repair "
                "and free from hazards."
            ),
            source="Landlord and Tenant Act 1985, s.11; Housing Act 2004",
            action=(
                "Document the disrepair with dated photographs. "
                "Write to your landlord formally requesting repairs."
            ),
            url="https://england.shelter.org.uk/housing_advice/repairs",
        ),
        Right(
            name="Right to Your Deposit Back",
            description=(
                "Your deposit must be held in a government-approved scheme. "
                "Your landlord must return it within 10 days of you agreeing "
                "the amount."
            ),
            source="Housing Act 2004, s.213",
            action=(
                "Check whether your deposit is protected using the "
                "government's deposit protection checker."
            ),
            url="https://www.gov.uk/tenancy-deposit-protection",
        ),
    ],
    "platform": [
        Right(
            name="Right to Explanation for Automated Decisions",
            description=(
                "If a platform has made a significant automated decision about "
                "your account, you have the right to a meaningful explanation."
            ),
            source="UK GDPR Article 22",
            action=(
                "Write to the platform requesting the reasons for the decision "
                "and whether it was made by an automated system."
            ),
            url="https://ico.org.uk/your-data-matters/your-right-to-object-to-automated-decision-making/",
        ),
        Right(
            name="Right to Know What Data Is Held About You",
            description=(
                "Platforms hold personal data on you. You can ask for all of it."
            ),
            source="UK GDPR Article 15",
            action="Submit a Subject Access Request to the platform.",
            url="https://ico.org.uk/your-data-matters/your-right-to-get-copies-of-your-data/",
        ),
        Right(
            name="Right to Complain to the ICO",
            description=(
                "If a platform has mishandled your personal data or breached "
                "your data rights, you can complain to the Information "
                "Commissioner's Office."
            ),
            source="UK GDPR Article 77",
            action="Raise a complaint with the ICO.",
            url="https://ico.org.uk/make-a-complaint/",
        ),
    ],
    "medical": [
        Right(
            name="Right to Access Your Medical Records",
            description=(
                "You are entitled to see all health records held about you "
                "by NHS or private healthcare providers."
            ),
            source="UK GDPR Article 15; Access to Health Records Act 1990",
            action="Submit a Subject Access Request to the healthcare provider.",
            url="https://www.nhs.uk/nhs-services/gps/what-is-the-gp-access-record/",
        ),
        Right(
            name="Right to Make a Formal Complaint",
            description=(
                "Every NHS body must have a complaints procedure. "
                "You can complain and receive a written response."
            ),
            source="NHS Constitution; Local Authority Social Services and NHS Complaints Regulations 2009",
            action=(
                "Submit a formal complaint to the provider in writing. "
                "They must acknowledge within three working days."
            ),
            url="https://www.nhs.uk/using-the-nhs/about-the-nhs/how-to-complain-about-nhs-services/",
        ),
        Right(
            name="Right to Escalate to the Parliamentary and Health Service Ombudsman",
            description=(
                "If you are not satisfied with the NHS's response, "
                "you can take your complaint to the PHSO."
            ),
            source="Health Service Commissioners Act 1993",
            action="Refer your complaint to the PHSO after exhausting local resolution.",
            url="https://www.ombudsman.org.uk/",
        ),
    ],
    "credit": [
        Right(
            name="Right to Know What Is on Your Credit File",
            description=(
                "You are entitled to a free statutory credit report from each "
                "Credit Reference Agency."
            ),
            source="UK GDPR Article 15; Consumer Credit Act 1974",
            action=(
                "Request your statutory credit report from Experian, Equifax, "
                "and TransUnion."
            ),
            url="https://ico.org.uk/your-data-matters/your-right-to-get-copies-of-your-data/",
        ),
        Right(
            name="Right to Challenge Inaccurate Data",
            description=(
                "If your credit file contains inaccurate information, "
                "you have the right to have it corrected."
            ),
            source="UK GDPR Article 16",
            action=(
                "Write to the Credit Reference Agency and the creditor "
                "disputing the entry."
            ),
        ),
        Right(
            name="Right to Complain to the Financial Ombudsman",
            description=(
                "If a financial firm has treated you unfairly, you can complain "
                "to the Financial Ombudsman Service for free."
            ),
            source="Financial Services and Markets Act 2000",
            action=(
                "Submit a complaint to the firm first. If unresolved after "
                "8 weeks, escalate to the Financial Ombudsman."
            ),
            url="https://www.financial-ombudsman.org.uk/",
        ),
    ],
    "employment": [
        Right(
            name="Right Not to Be Unfairly Dismissed",
            description=(
                "After two years of continuous employment, you have the right "
                "not to be unfairly dismissed."
            ),
            source="Employment Rights Act 1996, s.94",
            action=(
                "If you have been dismissed, consider raising a grievance "
                "and contacting ACAS about early conciliation."
            ),
            url="https://www.acas.org.uk/dismissal",
        ),
        Right(
            name="Right Not to Be Discriminated Against",
            description=(
                "You are protected from discrimination based on nine "
                "protected characteristics at work."
            ),
            source="Equality Act 2010",
            action=(
                "Document every instance of discriminatory treatment. "
                "Raise a formal grievance in writing."
            ),
            url="https://www.equalityhumanrights.com/equality/equality-act-2010",
        ),
        Right(
            name="Right to Be Paid What You Are Owed",
            description=(
                "Your employer cannot make unauthorised deductions from your pay."
            ),
            source="Employment Rights Act 1996, Part II",
            action=(
                "Write to your employer formally requesting the money owed. "
                "If unresolved, bring a claim to an Employment Tribunal."
            ),
            url="https://www.gov.uk/employment-tribunals",
        ),
        Right(
            name="Right to Know What Data Is Held About You",
            description=(
                "Your employer holds personal data about you. "
                "You can request all of it."
            ),
            source="UK GDPR Article 15",
            action="Submit a Subject Access Request to your employer.",
        ),
    ],
    "immigration": [
        Right(
            name="Right to Know the Reasons for a Refusal",
            description=(
                "Any refusal from the Home Office must include written reasons "
                "and information about your right of appeal."
            ),
            source="Immigration Rules; Human Rights Act 1998",
            action=(
                "Read the refusal letter carefully and note any appeal deadline. "
                "Deadlines are strict."
            ),
            url="https://www.gov.uk/immigration-asylum-tribunal",
        ),
        Right(
            name="Right to Access Your Immigration File",
            description=(
                "You can request all personal data the Home Office holds on you, "
                "including your immigration history."
            ),
            source="UK GDPR Article 15",
            action="Submit a Subject Access Request to the Home Office.",
            url="https://www.gov.uk/government/organisations/home-office/about/personal-information-charter",
        ),
        Right(
            name="Right to Legal Representation",
            description=(
                "You have the right to be represented by a solicitor or "
                "accredited immigration adviser at any hearing."
            ),
            source="Immigration and Asylum Act 1999",
            action=(
                "Contact an OISC-regulated adviser or a solicitor "
                "who specialises in immigration law."
            ),
            url="https://www.gov.uk/find-an-immigration-adviser",
        ),
    ],
    "consumer": [
        Right(
            name="Right to Goods That Are of Satisfactory Quality",
            description=(
                "Products must be of satisfactory quality, fit for purpose, "
                "and as described."
            ),
            source="Consumer Rights Act 2015, s.9",
            action=(
                "Within 30 days of purchase, you can reject the goods outright "
                "and claim a full refund."
            ),
            url="https://www.which.co.uk/consumer-rights/regulation/consumer-rights-act",
        ),
        Right(
            name="Right to a Repair, Replacement, or Refund",
            description=(
                "After 30 days, if goods are faulty, you are entitled to a "
                "repair or replacement. If that fails, a price reduction or refund."
            ),
            source="Consumer Rights Act 2015, s.23–24",
            action=(
                "Write to the retailer formally setting out the fault and "
                "requesting a remedy under the Consumer Rights Act 2015."
            ),
        ),
        Right(
            name="Right to Complain to a Regulator or Ombudsman",
            description=(
                "Depending on the sector, you may be able to escalate to a "
                "sector regulator or ombudsman."
            ),
            source="Various sector-specific legislation",
            action=(
                "Identify the relevant ombudsman for your sector and raise "
                "a complaint once the company has had 8 weeks to respond."
            ),
            url="https://www.ombudsmanassociation.org/find-an-ombudsman",
        ),
    ],
}

# International fallback — broad principles when jurisdiction is not UK.
_INTERNATIONAL_RIGHTS: dict[str, list[Right]] = {
    "enforcement": [
        Right(
            name="Right of Access to Personal Data",
            description="You may have the right to request data held about you by public authorities.",
            source="EU GDPR Article 15 / equivalent national law",
            action="Submit a data access request to the relevant body.",
        ),
        Right(
            name="Right to Fair Treatment",
            description="International human rights law protects against arbitrary treatment.",
            source="UDHR Article 7; ICCPR Article 26",
            action="Document the incident and seek local legal advice.",
        ),
    ],
    "consumer": [
        Right(
            name="Right to Goods of Satisfactory Quality",
            description="Most jurisdictions have consumer protection laws covering faulty goods.",
            source="Local consumer protection legislation",
            action="Check your country's consumer protection agency for the applicable rules.",
        ),
    ],
}


def map_rights(domain: str, jurisdiction: str = "UK") -> RightsMap:
    """Return the rights applicable to a domain and jurisdiction.

    Args:
        domain:       One of the DOMAINS from conversation.py.
        jurisdiction: ISO-style jurisdiction string. Defaults to ``'UK'``.

    Returns:
        A :class:`RightsMap` containing every applicable right, plus notes.
    """
    jurisdiction_upper = jurisdiction.upper()

    if jurisdiction_upper == "UK":
        rights = list(_UK_RIGHTS.get(domain, []))
        notes = (
            "These rights apply under English and Welsh law. "
            "Scottish and Northern Irish law may differ on some points. "
            "This is a map, not legal advice. "
            "If you are unsure, seek independent legal guidance."
        )
    else:
        # Use any domain-specific international rights we have, or fall back
        # to a generic list from the consumer domain
        rights = list(
            _INTERNATIONAL_RIGHTS.get(domain)
            or _INTERNATIONAL_RIGHTS.get("consumer", [])
        )
        notes = (
            f"Mirror does not yet have detailed rights data for '{jurisdiction}'. "
            "The rights shown are based on widely applicable international frameworks. "
            "Please verify with a local legal adviser."
        )

    return RightsMap(domain=domain, jurisdiction=jurisdiction_upper, rights=rights, notes=notes)
