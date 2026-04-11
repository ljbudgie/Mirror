# Mirror — see where you stand.

Tell it what happened. It maps your rights, generates the question, and gives you the next step.

Local-first. No data leaves your device. Built on the [Burgess Principle](https://github.com/ljbudgie/burgess-principle) (UK00004343685).

MIT licence. Python ≥ 3.11.

---

## What Mirror does

- **Classifies your situation** from a plain-English description into one of nine domains: enforcement, benefits, housing, platform, medical, credit, employment, immigration, and consumer.
- **Maps your rights** — shows the specific legal rights that apply, with sources and actions.
- **Gives you one next step** — not a list, just one clear thing to do now.
- **Drafts the communication** — 27 ready-to-send letter templates (SAR requests, FOI requests, grievance letters, NHS complaints, mandatory reconsiderations, tribunal appeals, ICO complaints, chargeback requests, and more), each with the [Burgess Principle](https://github.com/ljbudgie/burgess-principle) question included.
- **Tracks deadlines** — statutory timelines for DSARs, FOIs, tribunal claims, and complaint acknowledgements.
- **Hashes every outgoing message** — SHA-256 commitment hashing so you can prove a message came from you, without revealing personal data.

Everything runs on your device. No server, no accounts, no tracking, no cookies.

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
/core        Python modules — conversation, rights, next step, templates, commitment, timeline
/templates   Ready-to-send letter templates (27 templates)
/web         Local-first chat interface (HTML + CSS, no dependencies)
/docs        User guide, security policy, contributing guide
```

---

## Documentation

- [**User guide**](docs/user_guide.md) — full usage instructions, configuration, and examples
- [**Contributing**](docs/CONTRIBUTING.md) — how to help, code style, and pull request process
- [**Security policy**](docs/SECURITY.md) — vulnerability reporting, data handling, and threat model

---

## Privacy

Mirror is local-first by design.

- No data leaves your device
- No accounts or registration
- No analytics or tracking
- No cookies
- The web interface makes no network requests
- Your commitment vault is encrypted on your device
