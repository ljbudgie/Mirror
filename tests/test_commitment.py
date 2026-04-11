"""Tests for core/commitment.py — SHA-256 commitment generation and verification."""

import pytest
from core.commitment import generate_commitment, verify_commitment


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
