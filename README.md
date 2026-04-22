# Mirror

**Tell it what happened. It maps your rights, drafts the letter, and gives you one clear next step.**

Mirror is a local-first tool built on the [Burgess Principle](https://github.com/ljbudgie/burgess-principle) (UK Certification Mark UK00004343685). It helps ordinary people — especially those facing automated decisions by institutions — understand their rights and act on them without needing a solicitor.

Everything runs on your device. No data leaves. No accounts. No tracking.

MIT licence. Python ≥ 3.11.

---

## The problem Mirror solves

Institutions — energy companies, councils, credit agencies, platforms, government departments — routinely make automated decisions that affect people's lives without individual human review. Most people don't know they have the right to challenge this, or how.

Mirror closes that gap. You describe what happened in plain English. Mirror tells you what rights apply, gives you one thing to do now, and drafts the letter.

---

## What it does

**Classifies your situation** from plain-English input into one of nine domains:

- Enforcement / debt
- Benefits
- Housing
- Platform / content moderation
- Medical devices / health data
- Credit / financial
- Employment
- Immigration
- Consumer

**Maps your rights** — the specific legal rights that apply to your situation, with statutory sources and actions. Not generic advice. Situation-specific.

**Gives you one next step** — not a list of options, one clear action to take right now.

**Drafts the communication** — 27 ready-to-send letter templates including:
- Subject Access Requests (DSARs)
- Freedom of Information requests
- Article 22 automated decision challenges
- ICO complaints
- NHS complaints
- Tribunal appeals
- Mandatory reconsiderations
- Chargeback requests
- Grievance letters

Every template includes the Burgess Principle binary question: *"Was a human member of the team able to personally review the specific facts of my situation?"*

**Tracks deadlines** — statutory timelines for DSARs (30 days), FOIs (20 working days), tribunal claims, and complaint acknowledgements.

**Hashes every outgoing message** — SHA-256 commitment hashing so you can prove a message came from you, on a specific date, without revealing personal data. Tamper-evident by design.

**Optional local AI** — connect Ollama for adaptive classification and context-aware rights mapping. Disabled by default. When enabled, all processing stays on your device.

---

## Quickstart

```bash
pip install -e ".[dev]"
pytest
```

Open `web/index.html` in your browser. No server needed.

---

## Structure

```
/core        Python modules — conversation, rights, next step, templates, commitment, timeline, AI adapter
/prompts     System prompts for local AI integration
/templates   27 ready-to-send letter templates
/web         Local-first chat interface (HTML + CSS, no dependencies)
/docs        User guide, security policy, contributing guide
```

---

## Who this is for

- Anyone who has received an automated decision from an institution and doesn't know how to challenge it
- Disabled people and others who face additional barriers accessing institutional processes
- Advice workers, legal clinics, and advocates who want to help clients act quickly
- Developers building on the Burgess Principle ecosystem

You do not need legal training to use Mirror. You need to be able to describe what happened.

---

## Privacy

Mirror is local-first by design.

- No data leaves your device
- No accounts or registration
- No analytics or tracking
- No cookies
- The web interface makes no network requests
- Your commitment vault is encrypted on your device
- AI features (when enabled) use a local backend — no cloud APIs

---

## Local AI (optional)

Mirror works fully without AI — the deterministic rule-based engine handles classification, rights mapping, and template selection. AI adds adaptive classification and situationally tailored Burgess questions for edge cases.

### Setup

1. Install [Ollama](https://ollama.com/) and pull a model:

```bash
ollama pull mistral
```

2. Enable in `mirror-config.json`:

```json
{
  "ai": {
    "enabled": true,
    "model": "mistral",
    "base_url": "http://localhost:11434",
    "timeout": 120
  }
}
```

3. Install the optional dependency:

```bash
pip install -e ".[ai]"
```

When AI is unavailable or disabled, Mirror falls back to the deterministic engine. Nothing breaks.

---

## Documentation

- [User guide](docs/user_guide.md) — full usage instructions, configuration, and examples
- [Contributing](docs/CONTRIBUTING.md) — how to help, code style, and pull request process
- [Security policy](docs/SECURITY.md) — vulnerability reporting, data handling, and threat model

---

## The Burgess Principle

Mirror is built on the Burgess Principle — a simple accountability standard that asks one binary question of any institution:

> *"Was a human member of the team able to personally review the specific facts of my situation?"*

The answer is either SOVEREIGN (yes, with evidence) or NULL (no, or no evidence provided).

The Burgess Principle is free and MIT-licensed. The certification mark (UK00004343685) is separately governed. [Read more](https://github.com/ljbudgie/burgess-principle).

---

## Contributing

Contributions are welcome — particularly additional domain coverage, new letter templates, and accessibility improvements. See [CONTRIBUTING.md](docs/CONTRIBUTING.md).

The one requirement: every contribution must preserve the local-first, no-data-leaves principle. That is not a feature. It is the foundation.

---

*Mirror — see where you stand.*
