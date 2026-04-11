"""commitment.py — Every message you send carries a unique mark.

A fresh SHA-256 hash is generated for each outgoing communication. The salt
is stored locally in an encrypted vault so you can prove, at any time, that
a specific message originated from you — without revealing any personal data.

Cryptographic baseline: derived from the Burgess Principle methodology
(UK00004343685), compatible with burgess-principle v0.3.0.

The vault is encrypted using Fernet symmetric encryption. The vault key is
derived from a passphrase you provide — it never leaves your device.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path

# Optional Fernet encryption (install: pip install cryptography)
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64

    _CRYPTO_AVAILABLE = True
except ImportError:  # pragma: no cover
    _CRYPTO_AVAILABLE = False

_DEFAULT_VAULT_PATH = Path.home() / ".mirror" / "vault.enc"
_SALT_ITERATIONS = 480_000  # NIST-recommended minimum as of 2023


# ── Hashing ──────────────────────────────────────────────────────────────────


def generate_commitment(content: str) -> dict[str, str]:
    """Generate a fresh SHA-256 commitment for an outgoing message.

    A random salt is mixed with the content so that two identical messages
    produce different commitments. This protects against correlation attacks.

    Args:
        content: The full text of the message being sent.

    Returns:
        A dict with keys ``'hash'``, ``'salt'``, and ``'timestamp'``.
        The salt must be stored locally (use :func:`save_salt`) so the
        commitment can be verified later.
    """
    salt = secrets.token_hex(32)
    salted = f"{salt}:{content}"
    digest = hashlib.sha256(salted.encode("utf-8")).hexdigest()
    timestamp = datetime.now(timezone.utc).isoformat()

    return {
        "hash": digest,
        "salt": salt,
        "timestamp": timestamp,
    }


def verify_commitment(content: str, salt: str, expected_hash: str) -> bool:
    """Verify that a stored commitment matches a given message.

    Args:
        content:       The original message text.
        salt:          The salt that was used when the commitment was created.
        expected_hash: The hash stored at the time of sending.

    Returns:
        ``True`` if the content and salt produce the expected hash.
    """
    salted = f"{salt}:{content}"
    digest = hashlib.sha256(salted.encode("utf-8")).hexdigest()
    return secrets.compare_digest(digest, expected_hash)


# ── Vault ────────────────────────────────────────────────────────────────────


def _derive_key(passphrase: str, kdf_salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a passphrase.

    Uses PBKDF2-HMAC-SHA256. The kdf_salt is separate from the commitment salt
    and is stored alongside the vault file.
    """
    if not _CRYPTO_AVAILABLE:
        raise RuntimeError(
            "The 'cryptography' package is required for vault operations. "
            "Install it with: pip install cryptography"
        )
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=kdf_salt,
        iterations=_SALT_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode("utf-8")))


def save_salt(
    commitment_id: str,
    salt_data: dict[str, str],
    passphrase: str,
    vault_path: Path | None = None,
) -> None:
    """Encrypt and save a commitment salt to the local vault.

    Args:
        commitment_id: A unique identifier for this commitment (e.g. the hash).
        salt_data:     The dict returned by :func:`generate_commitment`.
        passphrase:    The user's vault passphrase. Never stored, never sent.
        vault_path:    Override the default vault location. Defaults to
                       ``~/.mirror/vault.enc``.
    """
    if not _CRYPTO_AVAILABLE:
        raise RuntimeError(
            "The 'cryptography' package is required for vault operations. "
            "Install it with: pip install cryptography"
        )

    vault_path = vault_path or _DEFAULT_VAULT_PATH
    kdf_salt_path = vault_path.with_suffix(".kdf_salt")

    vault_path.parent.mkdir(parents=True, exist_ok=True)

    # Load or create the KDF salt
    if kdf_salt_path.exists():
        kdf_salt = kdf_salt_path.read_bytes()
    else:
        kdf_salt = os.urandom(16)
        kdf_salt_path.write_bytes(kdf_salt)

    key = _derive_key(passphrase, kdf_salt)
    fernet = Fernet(key)

    # Load existing vault entries
    if vault_path.exists():
        try:
            decrypted = fernet.decrypt(vault_path.read_bytes())
            vault: dict[str, dict[str, str]] = json.loads(decrypted)
        except Exception:
            vault = {}
    else:
        vault = {}

    vault[commitment_id] = salt_data

    encrypted = fernet.encrypt(json.dumps(vault).encode("utf-8"))
    vault_path.write_bytes(encrypted)


def load_salt(
    commitment_id: str,
    passphrase: str,
    vault_path: Path | None = None,
) -> dict[str, str] | None:
    """Load a commitment salt from the local vault.

    Args:
        commitment_id: The identifier used when the salt was saved.
        passphrase:    The user's vault passphrase.
        vault_path:    Override the default vault location.

    Returns:
        The salt data dict, or ``None`` if the commitment ID is not found.
    """
    if not _CRYPTO_AVAILABLE:
        raise RuntimeError(
            "The 'cryptography' package is required for vault operations. "
            "Install it with: pip install cryptography"
        )

    vault_path = vault_path or _DEFAULT_VAULT_PATH
    kdf_salt_path = vault_path.with_suffix(".kdf_salt")

    if not vault_path.exists() or not kdf_salt_path.exists():
        return None

    kdf_salt = kdf_salt_path.read_bytes()
    key = _derive_key(passphrase, kdf_salt)
    fernet = Fernet(key)

    decrypted = fernet.decrypt(vault_path.read_bytes())
    vault: dict[str, dict[str, str]] = json.loads(decrypted)

    return vault.get(commitment_id)
