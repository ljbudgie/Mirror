# Mirror — Ecosystem Stack v2

**Mirror is the institutional accountability arm of the Burgess Principle ecosystem: a local-first personal sovereignty toolkit for challenging automated decisions, surfacing human accountability, and turning rights into action.**

Mirror sits alongside **OpenHear** (a local hearing, haptic, and sensory processing toolkit), the sensory sovereignty arm of the same ecosystem. Together they form a practical stack for defending human agency where institutions automate judgment and where bodies, senses, and assistive technologies become sites of control.

Everything in Mirror is designed around one non-negotiable question:

> **Was a human able to personally review the specific facts of my situation?**

If yes, the decision can be treated as **SOVEREIGN** only when that human review is real, evidenced, and specific. If no — or if the institution cannot prove it — the decision is **NULL** under the Burgess Principle.

MIT licence. Python ≥ 3.11.

---

## 1. Ecosystem Identity

### What Mirror is

Mirror is a local-first toolkit for ordinary people facing automated, bureaucratic, or opaque institutional decisions. It helps a person describe what happened in plain English, identifies the relevant rights and routes of challenge, generates a clear next step, and drafts practical communications such as data requests, complaints, appeals, reconsiderations, and escalation letters.

Mirror is not a legal advice marketplace, chatbot solicitor, or cloud case-management product. It is a sovereignty tool: it keeps the user's story on their own device and converts institutional confusion into structured, accountable action.

### Relationship to OpenHear and the Burgess Principle

The **Burgess Principle** is the foundation: a binary accountability test for whether a decision affecting a person was actually reviewed by a human who could consider the specific facts of that person's situation.

**Mirror** applies that test to institutional power: councils, employers, platforms, banks, health systems, government departments, landlords, debt collectors, insurers, and other decision-making bodies.

**OpenHear** applies the same sovereignty ethos to perception itself: local, privacy-preserving hearing and sensory systems that reduce dependence on corporate hearing infrastructure, proprietary assistive devices, and cloud pipelines that extract value from user data. Its **Universal Friend** work extends that idea into trusted-contact support that can remain local, consent-based, and privacy-preserving.

### Two complementary arms

The Burgess Principle ecosystem now has two complementary arms:

1. **Institutional Accountability — Mirror**  
   Helps people challenge automated or opaque decisions and demand evidence of meaningful human review.

2. **Sensory Sovereignty — OpenHear**  
   Helps people control how sound, haptics, trusted contacts, and future sensory substitution systems support their body without surrendering perception to corporate infrastructure.

Together, they address the same problem at two levels: who controls the decisions made about your life, and who controls the sensory channels through which you experience that life.

---

## 2. Core Philosophy

The Burgess Principle is the non-negotiable foundation of Mirror:

> **A decision that affects a person must be reviewable by a human who can personally consider the specific facts of that person's situation.**

Mirror turns that principle into a workflow. It asks whether automated decision-making was involved, whether meaningful human review occurred, what evidence exists, what deadlines apply, and what action the user can take next.

The wider ecosystem extends the same principle beyond digital rights into bodily senses. Sovereignty is not only about data protection, appeals, or complaints. It is also about whether a person can hear, perceive, communicate, adapt, and receive support without becoming dependent on systems they cannot inspect, control, or leave.

The core commitments are:

- **Local first:** personal facts stay on the user's device by default.
- **Human review:** institutions must show real, specific, accountable review.
- **User control:** the person decides what to share, export, send, or escalate.
- **Practical action:** every workflow should produce a usable next step.
- **Accessibility as power:** disabled people, patients, carers, and advocates should not need specialist legal or technical knowledge to challenge automated systems.
- **SOVEREIGN/NULL clarity:** vague process language is not enough; either the institution can evidence meaningful human review or it cannot.

---

## 3. Current Mirror Stack

Mirror currently provides a working local-first stack for institutional accountability.

### Domains

Mirror classifies plain-English user situations across nine domains:

- **Enforcement / debt** — police, fines, bailiffs, regulators, debt collectors
- **Benefits** — DWP, Universal Credit, PIP, ESA, mandatory reconsiderations
- **Housing** — landlords, councils, eviction, repairs, deposits, homelessness duties
- **Platform / content moderation** — account bans, content removal, automated moderation
- **Medical devices / health data** — one integrated domain covering NHS complaints, medical records, device-related decisions, health data access, and clinical escalation
- **Credit / financial** — credit files, affordability decisions, chargebacks, ombudsman routes
- **Employment** — dismissal, discrimination, unpaid wages, grievance routes
- **Immigration** — Home Office decisions, visa refusals, appeals, evidence gathering
- **Consumer** — faulty goods, services, subscriptions, refunds, unfair processes

The **Medical devices / health data** domain is strategically central because it is where Mirror's institutional accountability stack naturally meets OpenHear's sensory sovereignty work. Hearing aids, cochlear implants, audiology decisions, haptic systems, health records, algorithmic triage, device eligibility, and future sensory substitution technologies all create decisions that may need to be challenged.

### Local-first architecture

Mirror is designed to run without accounts, servers, analytics, or tracking.

```text
/core        Python modules — conversation, rights, next step, templates, commitment, timeline, AI adapter
/prompts     System prompts for optional local AI integration
/templates   27 ready-to-send letter templates
/web         Local-first chat interface (HTML + CSS, no dependencies)
/docs        User guide, security policy, contributing guide
```

Quickstart:

```bash
pip install -e ".[dev]"
pytest
```

Then open `web/index.html` in a browser. No server is required.

### Templates and actions

Mirror includes 27 ready-to-send templates, including:

- Subject Access Requests (DSARs)
- Freedom of Information requests
- Article 22 automated decision challenges
- ICO complaints
- NHS complaints
- Parliamentary and Health Service Ombudsman referrals
- Mandatory reconsiderations
- Tribunal appeals
- Credit disputes
- Financial Ombudsman complaints
- Chargeback requests
- Housing and landlord complaints
- Platform complaints
- Grievance letters
- Generic escalation letters

Every template is intended to convert confusion into a concrete action and to preserve the Burgess Principle question at the point of contact with the institution.

### AI integration

Mirror works without AI through deterministic classification, rights mapping, next-step selection, timeline logic, and template generation.

Optional local AI can be enabled through Ollama for adaptive classification and context-aware rights mapping. AI is disabled by default, uses a local backend when enabled, and falls back to the deterministic engine when unavailable.

### Commitment hashing and evidence discipline

Mirror generates SHA-256 commitment hashes for outgoing communications. This allows a user to prove that a message existed at a specific point in time without revealing the message contents publicly.

The goal is not just to send letters. The goal is to create an evidence trail that strengthens the user's position while preserving privacy.

---

## 4. Positioning in the Wider Landscape

### Compared with traditional legal tools and advice services

Most legal tools begin with procedure: forms, categories, jurisdiction, eligibility, or referral pathways. Mirror begins with the user's lived event and asks whether power was exercised accountably.

Traditional advice services often depend on scarce expert capacity. Corporate legal-tech tools often depend on accounts, cloud processing, monetised data, or platform lock-in. Mirror is different because it gives the user a private, local, repeatable way to structure their situation before deciding whether to seek advice, escalate, or send a formal request.

Mirror does not replace lawyers, advice workers, or advocates. It makes the first move easier, clearer, and more accountable.

### Synergy with OpenHear

OpenHear explores hearing sovereignty, trusted local contact systems, and future haptic or multisensory interfaces. Mirror provides the accountability layer when institutions make decisions about those technologies.

Examples include:

- A health service refuses or delays hearing support without explaining the decision.
- An insurer, employer, school, or benefits body relies on device data or audiology records.
- A proprietary hearing platform changes access, features, or support through automated policy.
- A future haptic wristband, sensory substitution device, or BrainPort-style system becomes part of a clinical, workplace, educational, or benefits decision.
- A trusted contact workflow, such as Universal Friend, needs user-controlled evidence and consent boundaries when institutions are involved.

OpenHear protects the sensory channel. Mirror challenges the institution when that channel is governed, denied, scored, or misunderstood.

### Patient-led innovation and biohacking context

Mirror and OpenHear belong in the lineage of patient-led innovation and responsible biohacking: people refusing to wait passively for institutions to understand their bodies, devices, or daily realities.

The parallels are clear:

- **Dana Lewis** — creator of OpenAPS, an open-source artificial pancreas system pioneered in the 2010s and still influential in diabetes technology — showed that patients can build safer, more responsive systems when official pathways move too slowly.
- **Hugo Campos** — a continuing advocate for patient access to implanted cardiac-device data — showed that people need access to the information produced by devices implanted in or used on their own bodies.
- Hearing hackers, disabled technologists, quantified-self communities, and assistive-tech tinkerers continue to show that lived expertise is not a secondary input — it is often the source of the breakthrough.

The Burgess Principle ecosystem gives that movement an accountability language: if an institution makes a decision about your body, data, device, support, or sensory access, it must be able to show that a real human reviewed the specific facts.

---

## 5. Ecosystem Architecture

The Burgess Principle ecosystem can be understood as a complete sovereignty stack:

```text
Burgess Principle
└── The accountability standard: SOVEREIGN or NULL

Mirror
└── Institutional accountability: rights mapping, templates, evidence, deadlines, escalation

OpenHear
└── Sensory sovereignty: local hearing pipeline, haptics, trusted contacts, perceptual augmentation

Universal Friend
└── Consent-based trusted-contact layer: human support without surrendering privacy

Future integrations
└── Shared evidence, sensory-device decisions, local identity, accessibility workflows, user-controlled exports
```

### Shared principles

Across Mirror and OpenHear, the architecture follows the same rules:

- **Local-first by default** — the user's facts, audio, sensory signals, and support relationships should not require cloud extraction.
- **SOVEREIGN/NULL test** — decisions either have evidenced, specific human review or they do not.
- **Privacy as architecture, not policy** — privacy should be enforced by design rather than promised in a terms page.
- **User-controlled disclosure** — users choose when to export, share, escalate, or involve a trusted person.
- **Assistive autonomy** — tools should increase the user's agency, not create a new dependency they cannot inspect or leave.
- **Institutional legibility** — outputs must be clear enough for councils, NHS bodies, ombudsmen, employers, courts, platforms, and regulators to understand.

Mirror is the paper trail and challenge engine. OpenHear is the perceptual and trusted-support engine. The Burgess Principle is the test that makes both coherent.

---

## 6. Future Evolution Roadmap

### Short term: next 3–6 months

- Strengthen the Medical devices / health data domain with clearer pathways for audiology, device eligibility, health records, NHS complaints, and data access.
- Expand template coverage for automated decision challenges, medical-device disputes, disability-related institutional decisions, and sensory-technology access.
- Improve the local web interface so users can move from plain-English description to rights, next step, template, deadline, and commitment hash with less friction.
- Refine optional local AI prompts while preserving deterministic fallbacks and no-cloud defaults.
- Improve accessibility output modes for screen readers, large text, simplified wording, and email-only workflows.

### Medium term: integrations and expanded domains

- Connect Mirror workflows to OpenHear scenarios where hearing technology, trusted contacts, haptic alerts, or sensory substitution systems are involved in institutional decisions.
- Create structured pathways for challenging decisions about hearing aids, cochlear implants, haptic wristbands, assistive devices, audiology records, workplace adjustments, education support, benefits assessments, and health-data reuse.
- Support user-controlled exports that can package a situation summary, Burgess Principle question, evidence checklist, deadline timeline, and template into a single local bundle.
- Build stronger advocate and trusted-contact workflows inspired by Universal Friend, allowing a user to involve another human without surrendering the whole case file.
- Extend international framework guidance while preserving UK-first statutory precision where it already exists.

### Long term: 5–15 years

The long-term ambition is not only better complaint letters. It is a shift in the balance of power between people and institutions.

Over the next 5–15 years, automated systems will increasingly decide access to benefits, housing, credit, work, education, healthcare, insurance, assistive technology, and sensory augmentation. At the same time, hearing, vision, touch, balance, and attention may become mediated by devices that are adaptive, networked, and algorithmic.

The Burgess Principle ecosystem should become a public-interest counterweight to that future:

- A person should be able to challenge any consequential decision and demand proof of specific human review.
- A disabled person should not lose agency because an institution cannot understand their assistive technology, sensory profile, or device data.
- A patient should be able to access, interpret, and contest decisions made from data generated by their own body.
- A sensory device should extend perception without becoming a corporate gatekeeper over reality.
- A trusted support network should strengthen autonomy without creating surveillance.

At humanity level, the goal is to make human agency non-optional in systems that govern human lives.

---

## 7. Sensory & Perceptual Layer

Mirror can evolve into the accountability layer for decisions about sensory technologies.

This matters because hearing aids, cochlear implants, haptic wristbands, BrainPort-style sensory substitution devices, visual-to-tactile systems, and future perceptual augmentation tools will not exist only as personal gadgets. BrainPort-style systems translate visual information into tactile sensations. Similar technologies will intersect with institutions through healthcare eligibility, insurance coverage, school support, employment adjustments, benefits assessments, clinical records, device procurement, data access, and platform policies.

OpenHear's work points toward a deeper frontier: changing not only how sound is processed, but how sensory information is translated across the body. Haptic signals may support hearing. Audio may influence spatial awareness. Sensory substitution may affect visual perception, attention, orientation, and the felt frequency of the world.

When those systems become part of institutional life, Mirror should help users ask:

- Who made the decision about my access to this technology?
- Was the decision based on a generic pathway, automated score, procurement rule, or actual human review?
- Did anyone consider the specific facts of my hearing, vision, sensory profile, disability, work, family, communication needs, and daily life?
- What data from my device or body was used?
- Can I access it, correct it, challenge it, or refuse secondary use?
- Can I involve a trusted person through a Universal Friend-style workflow without giving the institution unnecessary access?

The sensory and perceptual layer makes the ecosystem future-ready. It recognises that sovereignty will not stop at screens, forms, or databases. It will include the right to shape, protect, and contest the mediated senses through which people meet the world.

---

## 8. Strategic Differentiators

### Different from corporate tools

Corporate tools usually optimise for scale, capture, retention, analytics, compliance theatre, or proprietary advantage. Even well-designed products often ask users to trade privacy for convenience.

The Burgess Principle ecosystem starts from the opposite premise:

- The user is not the product.
- The user's story does not need to leave their device to become useful.
- AI is optional, local, and subordinate to the user's agency.
- Assistive technology should not become another surveillance surface.
- Institutions should not be allowed to hide behind automation, triage, policy scripts, or vendor systems.

### Different from traditional activism

Traditional activism often works at the level of campaigns, public pressure, policy reform, or collective mobilisation. Those are necessary, but they do not always help the person who has a deadline tomorrow, a benefit stopped today, a device refused last week, or an account banned without explanation.

Mirror and OpenHear bring activism down to the level of usable infrastructure:

- A question anyone can ask.
- A letter anyone can send.
- A hash anyone can keep.
- A sensory tool anyone can run locally.
- A trusted-contact pathway that does not require surrendering privacy.
- A framework that connects individual cases to systemic accountability.

This is not corporate convenience and it is not symbolic resistance. It is practical sovereignty.

### North Star as an ecosystem differentiator

The North Star of the Burgess Principle ecosystem is a world where no person is made powerless by an automated decision, an opaque institution, a locked medical device, an inaccessible sensory system, or a platform that refuses to recognise the facts of their life.

Mirror helps people see where they stand and act. OpenHear helps people control how they hear, sense, and connect. The Burgess Principle binds both into one standard:

> **If a system affects a human life, a human must be able to review the specific facts — and the person affected must have the tools to prove what happened, challenge the decision, and choose their next action.**
