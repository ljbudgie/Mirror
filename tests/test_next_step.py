"""Tests for core/next_step.py — one step at a time."""

import pytest
from core.next_step import (
    NextStep,
    ResponseAdvice,
    Stage,
    advise_from_response,
    get_next_step,
    outcome_to_stage,
)
from core.burgess import Outcome


class TestGetNextStep:
    def test_returns_next_step_object(self):
        result = get_next_step("housing", Stage.INITIAL)
        assert isinstance(result, NextStep)

    def test_action_is_non_empty_string(self):
        result = get_next_step("employment", Stage.INITIAL)
        assert isinstance(result.action, str)
        assert len(result.action) > 0

    def test_detail_is_non_empty_string(self):
        result = get_next_step("consumer", Stage.INITIAL)
        assert isinstance(result.detail, str)
        assert len(result.detail) > 0

    def test_stage_after_is_stage_enum(self):
        result = get_next_step("benefits", Stage.INITIAL)
        assert isinstance(result.stage_after, Stage)

    def test_initial_stage_is_default(self):
        without_stage = get_next_step("housing")
        with_stage    = get_next_step("housing", Stage.INITIAL)
        assert without_stage.action == with_stage.action

    def test_enforcement_initial(self):
        result = get_next_step("enforcement", Stage.INITIAL)
        assert "Subject Access Request" in result.action

    def test_enforcement_deadline_passed(self):
        result = get_next_step("enforcement", Stage.DEADLINE_PASSED)
        assert result.template_key == "sar_overdue"

    def test_benefits_initial(self):
        result = get_next_step("benefits", Stage.INITIAL)
        assert "Mandatory Reconsideration" in result.action

    def test_employment_initial(self):
        result = get_next_step("employment", Stage.INITIAL)
        assert "grievance" in result.action.lower()

    def test_medical_initial_uses_device_access_template(self):
        result = get_next_step("medical", Stage.INITIAL)
        assert result.template_key == "medical_device_access_request"
        assert "human review" in result.action.lower()

    def test_medical_response_received_challenges_decision(self):
        result = get_next_step("medical", Stage.RESPONSE_RECEIVED)
        assert result.template_key == "audiology_decision_challenge"

    def test_platform_response_received_requests_device_data(self):
        result = get_next_step("platform", Stage.RESPONSE_RECEIVED)
        assert result.template_key == "device_data_access_request"
        assert "data" in result.action.lower()
        assert "moderation" in result.detail.lower()

    def test_employment_response_received_requests_adjustment_review(self):
        result = get_next_step("employment", Stage.RESPONSE_RECEIVED)
        assert result.template_key == "reasonable_adjustment_request"
        assert "reasonable adjustment" in result.action.lower()
        assert "human review" in result.detail.lower()

    def test_unknown_domain_returns_default(self):
        result = get_next_step("totally_unknown_domain", Stage.INITIAL)
        assert isinstance(result, NextStep)
        assert len(result.action) > 0

    def test_immigration_initial_mentions_deadline(self):
        result = get_next_step("immigration", Stage.INITIAL)
        assert "deadline" in result.action.lower() or "appeal" in result.action.lower()

    def test_all_initial_steps_have_template_or_empty_key(self):
        from core.conversation import DOMAINS
        for domain in DOMAINS:
            result = get_next_step(domain, Stage.INITIAL)
            assert isinstance(result.template_key, str)

    def test_stage_after_initial_is_awaiting(self):
        # Most initial steps should move user to awaiting_response
        result = get_next_step("consumer", Stage.INITIAL)
        assert result.stage_after == Stage.AWAITING_RESPONSE


class TestOutcomeToStage:
    def test_sovereign_maps_to_response_received(self):
        assert outcome_to_stage(Outcome.SOVEREIGN) == Stage.RESPONSE_RECEIVED

    def test_null_maps_to_unsatisfied(self):
        assert outcome_to_stage(Outcome.NULL) == Stage.UNSATISFIED

    def test_ambiguous_maps_to_unsatisfied(self):
        assert outcome_to_stage(Outcome.AMBIGUOUS) == Stage.UNSATISFIED

    def test_every_outcome_maps_to_a_stage(self):
        for outcome in Outcome:
            assert isinstance(outcome_to_stage(outcome), Stage)


class TestAdviseFromResponse:
    def test_returns_response_advice(self):
        advice = advise_from_response("enforcement", "anything")
        assert isinstance(advice, ResponseAdvice)
        assert isinstance(advice.next_step, NextStep)
        assert isinstance(advice.stage, Stage)

    def test_sovereign_reply_gives_response_received_step(self):
        text = (
            "Dr Sarah Chen personally reviewed the specific facts of your case "
            "before the decision and had authority to change the outcome."
        )
        advice = advise_from_response("enforcement", text)
        assert advice.result.outcome is Outcome.SOVEREIGN
        assert advice.stage == Stage.RESPONSE_RECEIVED
        assert advice.next_step == get_next_step("enforcement", Stage.RESPONSE_RECEIVED)

    def test_null_reply_escalates(self):
        text = "This was an automated decision generated by our system."
        advice = advise_from_response("platform", text)
        assert advice.result.outcome is Outcome.NULL
        assert advice.stage == Stage.UNSATISFIED
        assert advice.next_step == get_next_step("platform", Stage.UNSATISFIED)

    def test_ambiguous_reply_escalates(self):
        text = "It was reviewed in line with our policy."
        advice = advise_from_response("benefits", text)
        assert advice.result.outcome is Outcome.AMBIGUOUS
        assert advice.stage == Stage.UNSATISFIED
        assert advice.next_step == get_next_step("benefits", Stage.UNSATISFIED)

    def test_empty_reply_is_ambiguous_and_escalates(self):
        advice = advise_from_response("enforcement", "")
        assert advice.result.outcome is Outcome.AMBIGUOUS
        assert advice.stage == Stage.UNSATISFIED

    def test_unknown_domain_falls_back_to_default_step(self):
        advice = advise_from_response("totally_unknown_domain", "automated decision")
        assert isinstance(advice.next_step, NextStep)
        assert len(advice.next_step.action) > 0


class TestPackageExports:
    def test_burgess_and_bridge_exported_from_core(self):
        import core

        for name in (
            "classify_response",
            "guidance_for",
            "Outcome",
            "BurgessResult",
            "advise_from_response",
            "outcome_to_stage",
            "get_next_step",
            "Stage",
        ):
            assert name in core.__all__
            assert hasattr(core, name)
