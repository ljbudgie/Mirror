"""Tests for core/commitment.py — SHA-256 commitment generation and verification."""

import pytest
from pathlib import Path
from core.commitment import (
    generate_commitment,
    verify_commitment,
    _derive_key,
    save_salt,
    load_salt,
)


class TestGenerateCommitment:
    def test_returns_dict(self):
        result = generate_commitment("Hello world")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = generate_commitment("Test message")
        assert "hash" in result
        assert "salt" in result
        assert "timestamp" in result

    def test_hash_is_64_char_hex(self):
        result = generate_commitment("Some content")
        assert len(result["hash"]) == 64
        assert all(c in "0123456789abcdef" for c in result["hash"])

    def test_salt_is_hex_string(self):
        result = generate_commitment("Content")
        salt = result["salt"]
        assert isinstance(salt, str)
        assert len(salt) == 64  # 32 bytes = 64 hex chars
        assert all(c in "0123456789abcdef" for c in salt)

    def test_timestamp_is_iso_format(self):
        result = generate_commitment("Content")
        ts = result["timestamp"]
        assert "T" in ts  # ISO 8601 marker
        assert "Z" in ts or "+" in ts  # timezone present

    def test_different_salts_each_call(self):
        r1 = generate_commitment("Same content")
        r2 = generate_commitment("Same content")
        assert r1["salt"] != r2["salt"]

    def test_different_hashes_for_same_content(self):
        # Because salt is random, identical content produces different hashes
        r1 = generate_commitment("Same content")
        r2 = generate_commitment("Same content")
        assert r1["hash"] != r2["hash"]

    def test_different_hashes_for_different_content(self):
        r1 = generate_commitment("Content A")
        r2 = generate_commitment("Content B")
        assert r1["hash"] != r2["hash"]

    def test_empty_string(self):
        result = generate_commitment("")
        assert len(result["hash"]) == 64


class TestVerifyCommitment:
    def test_verify_correct_commitment(self):
        content = "This is my message."
        commitment = generate_commitment(content)
        assert verify_commitment(content, commitment["salt"], commitment["hash"]) is True

    def test_reject_wrong_content(self):
        commitment = generate_commitment("Original message")
        assert verify_commitment("Different message", commitment["salt"], commitment["hash"]) is False

    def test_reject_wrong_salt(self):
        content = "My message"
        commitment = generate_commitment(content)
        assert verify_commitment(content, "wrong_salt_value", commitment["hash"]) is False

    def test_reject_wrong_hash(self):
        content = "My message"
        commitment = generate_commitment(content)
        assert verify_commitment(content, commitment["salt"], "a" * 64) is False

    def test_verify_returns_bool(self):
        result = verify_commitment("text", "salt", "hash")
        assert isinstance(result, bool)


class TestDeriveKey:
    def test_returns_bytes(self):
        key = _derive_key("my passphrase", b"0123456789abcdef")
        assert isinstance(key, bytes)

    def test_key_is_valid_fernet_length(self):
        # Fernet keys are 44 bytes of url-safe base64
        key = _derive_key("passphrase", b"salt_16_bytes!!!")
        assert len(key) == 44

    def test_same_passphrase_same_salt_gives_same_key(self):
        salt = b"deterministic!!!"
        k1 = _derive_key("secret", salt)
        k2 = _derive_key("secret", salt)
        assert k1 == k2

    def test_different_passphrase_gives_different_key(self):
        salt = b"same_salt_value!"
        k1 = _derive_key("passphrase_a", salt)
        k2 = _derive_key("passphrase_b", salt)
        assert k1 != k2

    def test_different_salt_gives_different_key(self):
        k1 = _derive_key("same_pass", b"salt_aaaaaaaaaa!")
        k2 = _derive_key("same_pass", b"salt_bbbbbbbbbb!")
        assert k1 != k2


class TestSaveSalt:
    def test_creates_vault_file(self, tmp_path):
        vault = tmp_path / "vault.enc"
        commitment = generate_commitment("test content")
        save_salt("id1", commitment, "password123", vault_path=vault)
        assert vault.exists()

    def test_creates_kdf_salt_file(self, tmp_path):
        vault = tmp_path / "vault.enc"
        commitment = generate_commitment("content")
        save_salt("id1", commitment, "password", vault_path=vault)
        kdf_salt_path = vault.with_suffix(".kdf_salt")
        assert kdf_salt_path.exists()
        assert len(kdf_salt_path.read_bytes()) == 16

    def test_creates_parent_directories(self, tmp_path):
        vault = tmp_path / "subdir" / "nested" / "vault.enc"
        commitment = generate_commitment("content")
        save_salt("id1", commitment, "pass", vault_path=vault)
        assert vault.exists()

    def test_multiple_entries_stored(self, tmp_path):
        vault = tmp_path / "vault.enc"
        c1 = generate_commitment("first")
        c2 = generate_commitment("second")
        save_salt("id1", c1, "pass", vault_path=vault)
        save_salt("id2", c2, "pass", vault_path=vault)
        # Both should be loadable
        loaded1 = load_salt("id1", "pass", vault_path=vault)
        loaded2 = load_salt("id2", "pass", vault_path=vault)
        assert loaded1 is not None
        assert loaded2 is not None

    def test_overwrites_existing_entry(self, tmp_path):
        vault = tmp_path / "vault.enc"
        c1 = generate_commitment("original")
        c2 = generate_commitment("updated")
        save_salt("same_id", c1, "pass", vault_path=vault)
        save_salt("same_id", c2, "pass", vault_path=vault)
        loaded = load_salt("same_id", "pass", vault_path=vault)
        assert loaded["salt"] == c2["salt"]


class TestLoadSalt:
    def test_roundtrip_save_and_load(self, tmp_path):
        vault = tmp_path / "vault.enc"
        commitment = generate_commitment("my message")
        save_salt("commit1", commitment, "secret", vault_path=vault)
        loaded = load_salt("commit1", "secret", vault_path=vault)
        assert loaded is not None
        assert loaded["hash"] == commitment["hash"]
        assert loaded["salt"] == commitment["salt"]
        assert loaded["timestamp"] == commitment["timestamp"]

    def test_returns_none_for_missing_id(self, tmp_path):
        vault = tmp_path / "vault.enc"
        commitment = generate_commitment("content")
        save_salt("exists", commitment, "pass", vault_path=vault)
        result = load_salt("does_not_exist", "pass", vault_path=vault)
        assert result is None

    def test_returns_none_when_vault_missing(self, tmp_path):
        vault = tmp_path / "nonexistent_vault.enc"
        result = load_salt("any_id", "pass", vault_path=vault)
        assert result is None

    def test_returns_none_when_kdf_salt_missing(self, tmp_path):
        vault = tmp_path / "vault.enc"
        vault.write_bytes(b"some data")
        # kdf_salt file is not created
        result = load_salt("any_id", "pass", vault_path=vault)
        assert result is None

    def test_wrong_passphrase_raises(self, tmp_path):
        vault = tmp_path / "vault.enc"
        commitment = generate_commitment("content")
        save_salt("id1", commitment, "correct_pass", vault_path=vault)
        with pytest.raises(Exception):
            load_salt("id1", "wrong_pass", vault_path=vault)

    def test_corrupted_vault_with_wrong_passphrase_on_save(self, tmp_path):
        """Saving with a different passphrase to existing vault silently resets."""
        vault = tmp_path / "vault.enc"
        c1 = generate_commitment("first")
        save_salt("id1", c1, "pass1", vault_path=vault)
        # Save with different passphrase — existing data can't be decrypted,
        # so vault is reset with the new entry only
        c2 = generate_commitment("second")
        save_salt("id2", c2, "pass2", vault_path=vault)
        # id2 should be loadable with pass2
        loaded = load_salt("id2", "pass2", vault_path=vault)
        assert loaded is not None
        assert loaded["salt"] == c2["salt"]


class TestVaultIntegration:
    def test_full_workflow(self, tmp_path):
        """Generate commitment, save to vault, load from vault, verify."""
        vault = tmp_path / "vault.enc"
        content = "Dear Sir, I am writing to request..."
        passphrase = "my-secret-passphrase"

        commitment = generate_commitment(content)
        commit_id = commitment["hash"]

        save_salt(commit_id, commitment, passphrase, vault_path=vault)
        loaded = load_salt(commit_id, passphrase, vault_path=vault)

        assert loaded is not None
        assert verify_commitment(content, loaded["salt"], loaded["hash"]) is True

    def test_verify_fails_with_tampered_content(self, tmp_path):
        """Ensure tampering with content causes verification to fail."""
        vault = tmp_path / "vault.enc"
        content = "Original message"
        passphrase = "pass"

        commitment = generate_commitment(content)
        save_salt(commitment["hash"], commitment, passphrase, vault_path=vault)
        loaded = load_salt(commitment["hash"], passphrase, vault_path=vault)

        assert loaded is not None
        assert verify_commitment("Tampered message", loaded["salt"], loaded["hash"]) is False
