"""conversation.py — The first thing Mirror says is: 'Tell me what happened.'

No forms. No tick-boxes. Just plain English.
This module listens, then quietly works out what kind of situation you're in.
"""

from __future__ import annotations

import re

# ── Domain catalogue ────────────────────────────────────────────────────────
DOMAINS = [
    "enforcement",
    "benefits",
    "housing",
    "platform",
    "medical",
    "credit",
    "employment",
    "immigration",
    "consumer",
]

# Keywords that suggest each domain.
# Lists are deliberately broad — the classifier picks the best fit, not a hard rule.
_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "enforcement": [
        "police", "arrest", "detained", "detention", "stopped", "searched",
        "caution", "fine", "penalty", "penalty notice", "court", "criminal",
        "prosecution", "charge", "charged", "bail", "warrant", "enforcement",
        "officer", "constable", "custody", "cpw", "asbo", "injunction",
        "restraining order", "cctv", "bodycam", "use of force",
    ],
    "benefits": [
        "benefit", "universal credit", "uc", "pip", "personal independence",
        "esa", "employment support", "jobseeker", "jsa", "dwp",
        "department for work", "sanction", "sanctioned", "assessment",
        "capita", "maximus", "atos", "work capability", "pip assessment",
        "housing benefit", "council tax support", "tax credit", "child benefit",
        "carer's allowance", "state pension", "overpayment", "debt letter",
    ],
    "housing": [
        "landlord", "tenant", "tenancy", "eviction", "evicted", "section 21",
        "section 8", "notice to quit", "rent", "deposit", "damp", "mould",
        "disrepair", "repairs", "housing association", "council housing",
        "homelessness", "homeless", "local authority", "shelter",
        "housing benefit", "letting agent", "estate agent",
    ],
    "platform": [
        "banned", "suspended", "account", "facebook", "twitter", "x",
        "instagram", "youtube", "tiktok", "snapchat", "linkedin", "google",
        "amazon", "ebay", "paypal", "stripe", "app store", "play store",
        "content removed", "post removed", "flagged", "demonetised",
        "deplatformed", "algorithm", "review removed", "listing removed",
        "marketplace", "seller account",
    ],
    "medical": [
        "hospital", "nhs", "gp", "doctor", "nurse", "consultant",
        "treatment", "refused treatment", "misdiagnosis", "negligence",
        "clinical", "mental health", "sectioned", "medication", "prescription",
        "care plan", "social care", "cqc", "complaint", "patient",
        "ambulance", "a&e", "accident and emergency", "discharge",
        "medical record", "health record", "health data", "medical device",
        "medical-device", "device data", "hearing aid", "hearing aids",
        "cochlear implant", "cochlear implants", "audiology", "audiologist",
        "haptic", "haptic device", "haptic wristband", "assistive device",
        "assistive technology", "sensory substitution", "device eligibility",
        "eligibility decision", "device refused", "hearing support",
        "workplace adjustment", "reasonable adjustment", "disability support",
    ],
    "credit": [
        "credit", "credit file", "credit report", "experian", "equifax",
        "transunion", "creditor", "debt", "debt collector", "bailiff",
        "ccj", "county court judgment", "default", "late payment",
        "credit card", "loan", "overdraft", "bank", "building society",
        "financial ombudsman", "fca", "interest", "charges",
    ],
    "employment": [
        "employer", "employee", "dismissed", "dismissal", "fired",
        "redundancy", "redundant", "unfair dismissal", "constructive dismissal",
        "discrimination", "harassment", "grievance", "disciplinary",
        "contract", "wages", "pay", "unpaid", "tribunal", "acas",
        "workplace", "manager", "hr", "human resources", "sick pay",
        "maternity", "paternity", "flexible working", "zero hours",
    ],
    "immigration": [
        "visa", "leave to remain", "immigration", "home office",
        "asylum", "refugee", "deportation", "removal", "detention centre",
        "biometric", "brp", "settled status", "euss", "indefinite leave",
        "naturalisation", "citizenship", "passport", "travel document",
        "entry clearance", "refusal", "appeal", "tribunal", "ukba", "ukvi",
    ],
    "consumer": [
        "product", "goods", "faulty", "defective", "refund", "return",
        "warranty", "guarantee", "consumer rights", "trading standards",
        "scam", "fraud", "mis-sold", "missold", "contract", "service",
        "subscription", "cancellation", "delivery", "parcel", "courier",
        "retailer", "shop", "online purchase", "chargeback", "section 75",
    ],
}


def classify(text: str) -> str:
    """Classify a plain-English description into a domain.

    Args:
        text: What the user typed — their words, unedited.

    Returns:
        One of the DOMAINS strings. Falls back to ``"consumer"`` when nothing
        else fits, because consumer rights are broad and often applicable.
    """
    normalised = text.lower()
    # Strip punctuation so "police." matches "police"
    normalised = re.sub(r"[^\w\s]", " ", normalised)
    words = set(normalised.split())

    scores: dict[str, int] = {domain: 0 for domain in DOMAINS}
    for domain, keywords in _DOMAIN_KEYWORDS.items():
        for kw in keywords:
            # Multi-word keywords need a substring check
            if " " in kw:
                if kw in normalised:
                    scores[domain] += 2
            elif kw in words:
                scores[domain] += 1

    best_domain = max(scores, key=lambda d: scores[d])
    if scores[best_domain] == 0:
        return "consumer"
    return best_domain


def greet() -> str:
    """Return the opening message Mirror shows every time."""
    return (
        "Hello. I'm Mirror.\n\n"
        "Tell me what happened — in your own words, at your own pace.\n"
        "There's no right way to start. Just say what's on your mind."
    )


def prompt_for_detail(domain: str) -> str:
    """Return a gentle follow-up prompt tailored to the identified domain."""
    follow_ups = {
        "enforcement": (
            "It sounds like this involves the police or a regulatory body. "
            "Can you tell me roughly when it happened, and whether you received "
            "any paperwork — a reference number, a notice, or a letter?"
        ),
        "benefits": (
            "It sounds like this is about your benefits or a decision made "
            "by the DWP or a similar body. Do you know the date of the decision, "
            "and have you received anything in writing?"
        ),
        "housing": (
            "This sounds like a housing matter. Can you tell me whether you rent "
            "or own, and whether you've received any formal notice from your "
            "landlord or local authority?"
        ),
        "platform": (
            "It sounds like a platform has taken action against your account. "
            "Do you know when it happened, and have you received any message "
            "from them explaining why?"
        ),
        "medical": (
            "This sounds like it involves healthcare, health data, or an "
            "assistive device decision. Has anyone given you written reasons, "
            "and has a named person reviewed your specific facts?"
        ),
        "credit": (
            "This sounds like a financial or credit matter. Do you know which "
            "organisation is involved, and have you received any letters or "
            "notices from them?"
        ),
        "employment": (
            "This sounds like a workplace situation. Can you tell me roughly "
            "when it happened and whether you've had any written communication "
            "from your employer — a letter, an email, or a formal notice?"
        ),
        "immigration": (
            "This sounds like it involves the Home Office or your immigration "
            "status. Have you received a decision in writing, and do you know "
            "the date on the letter?"
        ),
        "consumer": (
            "This sounds like a problem with a product, service, or company. "
            "Can you tell me roughly when it happened and whether you've tried "
            "to resolve it with them directly yet?"
        ),
    }
    return follow_ups.get(domain, "Can you tell me a little more?")
