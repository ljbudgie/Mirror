# Security Policy

## Our commitment

Mirror is built for people who are dealing with difficult situations. The
people who use it may be vulnerable. Security is not a feature here — it is
the foundation.

---

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | ✓ |

---

## Reporting a vulnerability

If you discover a security vulnerability, please **do not** open a public
GitHub issue. Instead, email the maintainer directly.

Contact: see the repository's primary account on GitHub.

Please include:
- A description of the vulnerability
- Steps to reproduce it
- What information or systems are at risk
- Any suggested remediation

We will acknowledge your report within 5 working days and aim to release a
fix within 30 days for confirmed vulnerabilities.

---

## Data handling

Mirror stores no personal data on any server. All user data lives on the
user's device. There is no backend.

The only sensitive data Mirror handles locally is:

- **Commitment salts** — stored in `~/.mirror/vault.enc`, encrypted with
  Fernet symmetric encryption using a PBKDF2-derived key. The key is derived
  from the user's passphrase, which is never stored.

- **User messages in the web interface** — stored only in browser memory
  (JavaScript variables). Nothing is written to `localStorage`, cookies, or
  any remote server.

---

## Cryptographic baseline

Mirror's commitment module implements:

- SHA-256 hashing via Python's `hashlib`
- 32-byte random salts via `secrets.token_hex`
- Fernet symmetric encryption via the `cryptography` package
- PBKDF2-HMAC-SHA256 key derivation (480,000 iterations — NIST-recommended)

The cryptographic baseline is derived from the Burgess Principle methodology
(UK00004343685).

---

## Threat model

Mirror is a **local-first** application. The primary threat vectors are:

1. **Physical device compromise** — if your device is seized or accessed by a
   third party, your vault file may be at risk. Use a strong passphrase.

2. **Malicious templates** — do not use templates from untrusted sources.
   Mirror does not execute template code; templates are plain text with
   variable substitution only.

3. **Supply chain** — Mirror depends on the `cryptography` package. We pin to
   a minimum version and recommend keeping dependencies updated.

There is no network component, so there is no remote attack surface.

---

## Responsible disclosure

We follow a coordinated disclosure approach. We will credit researchers who
report vulnerabilities responsibly.
