"""Tests for core/next_step.py — one step at a time."""

import pytest
from core.next_step import get_next_step, NextStep, Stage


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
