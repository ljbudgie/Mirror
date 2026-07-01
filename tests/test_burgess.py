"""Tests for core/burgess.py — the three-outcome Burgess classification engine."""

import pytest

from core.burgess import (
    BINARY_QUESTION,
    LEGAL_FOUNDATIONS,
    PLAIN_QUESTION,
    SOVEREIGN_EVIDENCE,
    BurgessResult,
    Outcome,
    classify_response,
    guidance_for,
)


class TestConstants:
    def test_binary_question_is_a_question(self):
        assert BINARY_QUESTION.endswith("?")
        assert len(BINARY_QUESTION) > 20

    def test_plain_question_is_a_question(self):
        assert PLAIN_QUESTION.endswith("?")

    def test_legal_foundations_reference_modern_law(self):
        combined = " ".join(LEGAL_FOUNDATIONS.keys())
        assert "DUAA 2025 s.80" in combined
        assert "22A–22D" in combined
        assert "EU AI Act Article 14" in combined

    def test_legal_foundations_include_void_ab_initio_case_law(self):
        combined = " ".join(LEGAL_FOUNDATIONS.keys())
        assert "Ahmed" in combined
        assert "Majera" in combined

    def test_five_sovereign_evidence_criteria(self):
        assert set(SOVEREIGN_EVIDENCE) == {
            "named_reviewer", "role", "specific_facts", "timing", "authority",
        }


class TestOutcomeEnum:
    def test_three_outcomes(self):
        assert {o.value for o in Outcome} == {"SOVEREIGN", "NULL", "AMBIGUOUS"}


class TestSovereign:
    def test_named_reviewer_with_facts_and_timing(self):
        text = (
            "Yes. Dr Sarah Chen in our clinical review team personally reviewed "
            "the specific facts of your case before the decision was made and "
            "had authority to change the outcome."
        )
        result = classify_response(text)
        assert result.outcome is Outcome.SOVEREIGN

    def test_reviewed_by_named_person_with_authority(self):
        text = (
            "Your application was reviewed by James Patel, a senior caseworker, "
            "who considered your specific circumstances and had the authority to "
            "change the outcome."
        )
        result = classify_response(text)
        assert result.outcome is Outcome.SOVEREIGN

    def test_sovereign_reports_matched_criteria(self):
        text = (
            "Yes, Sarah Chen in our customer review team personally reviewed "
            "your specific case before the decision and could change the outcome."
        )
        result = classify_response(text)
        assert "named_reviewer" in result.matched_criteria
        assert "specific_facts" in result.matched_criteria


class TestNull:
    def test_explicit_automated_decision(self):
        text = (
            "The decision was made automatically by our system. We cannot name "
            "an individual who reviewed your case."
        )
        result = classify_response(text)
        assert result.outcome is Outcome.NULL

    def test_bulk_processed(self):
        text = "Your warrant application was bulk-processed by system logic."
        result = classify_response(text)
        assert result.outcome is Outcome.NULL

    def test_null_guidance_mentions_statute(self):
        text = "This was a fully automated decision with no human review."
        result = classify_response(text)
        assert result.outcome is Outcome.NULL
        assert "Data (Use and Access) Act 2025" in result.guidance


class TestAmbiguous:
    def test_vague_human_oversight(self):
        text = "Your case was subject to human oversight in line with our policy."
        result = classify_response(text)
        assert result.outcome is Outcome.AMBIGUOUS

    def test_human_review_layer_without_name(self):
        text = "We have a human review layer that checks these decisions."
        result = classify_response(text)
        assert result.outcome is Outcome.AMBIGUOUS

    def test_empty_response_is_ambiguous(self):
        result = classify_response("")
        assert result.outcome is Outcome.AMBIGUOUS
        assert len(result.missing_criteria) == 5

    def test_ambiguous_reports_missing_criteria(self):
        result = classify_response("It was reviewed in accordance with policy.")
        assert result.outcome is Outcome.AMBIGUOUS
        assert result.missing_criteria


class TestResultShape:
    def test_returns_burgess_result(self):
        result = classify_response("anything")
        assert isinstance(result, BurgessResult)

    def test_result_has_rationale_and_guidance(self):
        result = classify_response("It was automated.")
        assert result.rationale
        assert result.guidance

    def test_matched_and_missing_partition_all_criteria(self):
        result = classify_response("Dr Sarah Chen reviewed your specific case.")
        assert set(result.matched_criteria) | set(result.missing_criteria) == {
            "named_reviewer", "role", "specific_facts", "timing", "authority",
        }


class TestGuidance:
    def test_guidance_for_each_outcome(self):
        for outcome in Outcome:
            assert guidance_for(outcome)

    def test_sovereign_guidance_distinct_from_null(self):
        assert guidance_for(Outcome.SOVEREIGN) != guidance_for(Outcome.NULL)
