"""Tests for core/conversation.py — the intake and classifier."""

import pytest
from core.conversation import classify, greet, prompt_for_detail, DOMAINS


class TestClassify:
    def test_enforcement_keywords(self):
        assert classify("The police stopped and searched me without reason") == "enforcement"

    def test_benefits_keywords(self):
        assert classify("The DWP has sanctioned my Universal Credit") == "benefits"

    def test_housing_keywords(self):
        assert classify("My landlord is trying to evict me with a Section 21 notice") == "housing"

    def test_platform_keywords(self):
        assert classify("Facebook suspended my account without explanation") == "platform"

    def test_medical_keywords(self):
        assert classify("The hospital refused my treatment and the NHS hasn't responded") == "medical"

    @pytest.mark.parametrize(
        "text",
        [
            "Audiology refused my hearing aids without explaining the decision",
            "My cochlear implant device data was used in an eligibility decision",
            "The haptic wristband support was refused by the clinic",
            "They ignored my assistive technology and reasonable adjustment request",
            "A sensory substitution device was denied without human review",
        ],
    )
    def test_medical_sensory_keywords(self, text):
        assert classify(text) == "medical"

    def test_credit_keywords(self):
        assert classify("There is an incorrect entry on my Experian credit file") == "credit"

    def test_employment_keywords(self):
        assert classify("My employer dismissed me unfairly after I raised a grievance") == "employment"

    def test_immigration_keywords(self):
        assert classify("The Home Office refused my visa application") == "immigration"

    def test_consumer_keywords(self):
        assert classify("The product I bought is faulty and they won't give me a refund") == "consumer"

    def test_unknown_text_falls_back_to_consumer(self):
        # An unrecognisable input should fall back to consumer as the broadest domain
        result = classify("something completely unrecognisable xyzzy qwerty")
        assert result == "consumer"

    def test_case_insensitive(self):
        assert classify("POLICE ARRESTED ME") == "enforcement"

    def test_punctuation_stripped(self):
        assert classify("landlord! eviction. notice.") == "housing"

    def test_multi_word_keyword(self):
        assert classify("I got a section 21 notice from my landlord") == "housing"

    def test_returns_valid_domain(self):
        result = classify("They took my money and won't refund it")
        assert result in DOMAINS


class TestGreet:
    def test_greet_returns_string(self):
        message = greet()
        assert isinstance(message, str)
        assert len(message) > 0

    def test_greet_mentions_mirror(self):
        assert "Mirror" in greet()


class TestPromptForDetail:
    def test_all_domains_have_prompt(self):
        for domain in DOMAINS:
            result = prompt_for_detail(domain)
            assert isinstance(result, str)
            assert len(result) > 10

    def test_unknown_domain_returns_fallback(self):
        result = prompt_for_detail("not_a_real_domain")
        assert isinstance(result, str)
        assert len(result) > 0
