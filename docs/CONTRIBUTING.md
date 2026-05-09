# Contributing to Mirror

Thank you for wanting to help. Mirror exists for people who feel unseen.
Every contribution — however small — matters.

---

## Before you start

Please read the [user guide](user_guide.md) and understand what Mirror is
trying to do. Mirror is not a legal service. It is a tool that helps people
help themselves. Every change should make it clearer, calmer, and more
useful for the people who need it most.

---

## Ways to contribute

- **Improve the classifier** — better keyword coverage for any domain
- **Add or refine rights data** — particularly for non-UK jurisdictions
- **Write templates** — letters for domains or situations we haven't covered
- **Improve the web interface** — accessibility, clarity, mobile experience
- **Fix bugs** — especially anything that produces incorrect or unclear output
- **Improve documentation** — plain English, please

---

## Guardrails

- Cloud AI, remote inference, analytics, or tracking
- Server-side components or databases
- User accounts or authentication
- New dependencies without a compelling reason

Optional local AI is allowed only where it preserves Mirror's local-first design:
disabled by default, user-controlled, dependency-light, and with deterministic
fallbacks that keep the toolkit useful without AI.

Mirror must remain local-first and minimal.

---

## Development setup

```bash
# Clone the repository
git clone https://github.com/ljbudgie/Mirror-

# Install in development mode
pip install -e ".[dev]"

# Run the tests
pytest
```

---

## Code style

- Python: follow PEP 8. Use type hints. Keep functions small.
- JavaScript: vanilla JS only. No frameworks. No build tools.
- HTML/CSS: semantic HTML. Accessible by default. Mobile-first.
- Comments: plain English. If it needs explaining, explain it gently.

The tone throughout should be calm, respectful, and human-first.
Mirror should never feel like software — it should feel like someone listening.

---

## Tests

Every new feature or change to existing behaviour should have a corresponding
test. We use `pytest`. Tests live in `/tests/`, one file per module.

Run tests before submitting a pull request:

```bash
pytest
```

---

## Pull request process

1. Fork the repository and create a new branch from `main`
2. Make your changes
3. Add or update tests as needed
4. Run the full test suite and confirm it passes
5. Submit a pull request with a clear description of what changed and why

Keep pull requests focused. One change at a time.

---

## Licence

By contributing, you agree that your contributions will be licensed under the
MIT licence.

---

## Code of conduct

Be kind. Mirror is built for people in difficult situations. The same
humanity that the project is designed to extend to users should extend to
contributors too.
