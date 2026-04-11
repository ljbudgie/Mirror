"""Tests for core/template_engine.py — rendering templates."""

import pytest
from pathlib import Path
from core.template_engine import (
    BURGESS_QUESTION,
    render_inline,
    list_templates,
    render,
)


class TestBurgessQuestion:
    def test_burgess_question_present(self):
        assert "Burgess Principle" in BURGESS_QUESTION

    def test_burgess_question_is_string(self):
        assert isinstance(BURGESS_QUESTION, str)
        assert len(BURGESS_QUESTION) > 20


class TestRenderInline:
    def test_substitutes_variables(self):
        tmpl = "Dear $name, your reference is $ref."
        result = render_inline(tmpl, {"name": "Alice", "ref": "ABC123"}, include_burgess=False)
        assert "Alice" in result
        assert "ABC123" in result
        assert "$name" not in result
        assert "$ref" not in result

    def test_unknown_placeholder_preserved(self):
        tmpl = "Hello $known and $unknown."
        result = render_inline(tmpl, {"known": "world"}, include_burgess=False)
        assert "world" in result
        assert "$unknown" in result

    def test_burgess_appended_when_requested(self):
        result = render_inline("Some text.", {}, include_burgess=True)
        assert BURGESS_QUESTION in result

    def test_burgess_not_appended_when_disabled(self):
        result = render_inline("Some text.", {}, include_burgess=False)
        assert BURGESS_QUESTION not in result

    def test_empty_context(self):
        tmpl = "No placeholders here."
        result = render_inline(tmpl, {}, include_burgess=False)
        assert result == tmpl

    def test_curly_brace_syntax(self):
        tmpl = "Hello ${name}."
        result = render_inline(tmpl, {"name": "Bob"}, include_burgess=False)
        assert "Bob" in result


class TestListTemplates:
    def test_returns_list(self):
        result = list_templates()
        assert isinstance(result, list)

    def test_templates_are_strings(self):
        for tmpl in list_templates():
            assert isinstance(tmpl, str)

    def test_core_templates_exist(self):
        templates = list_templates()
        for expected in ["sar_request", "generic_complaint", "foi_request"]:
            assert expected in templates, f"Expected template '{expected}' not found"

    def test_returns_empty_list_when_directory_missing(self, monkeypatch):
        import core.template_engine as te
        monkeypatch.setattr(te, "_TEMPLATES_DIR", Path("/nonexistent/templates"))
        result = te.list_templates()
        assert result == []


class TestRender:
    def test_render_sar_request(self):
        context = {
            "your_name": "Jane Smith",
            "your_address": "1 Example Street",
            "your_email": "jane@example.com",
            "today_date": "11 April 2026",
            "organisation_name": "Test Corp",
            "organisation_address": "2 Corp Lane",
            "your_full_name": "Jane Smith",
            "your_dob": "01/01/1990",
            "reference_number": "REF001",
        }
        result = render("sar_request", context)
        assert "Jane Smith" in result
        assert "UK GDPR" in result
        assert BURGESS_QUESTION in result

    def test_render_includes_burgess_by_default(self):
        context = {"your_name": "Test"}
        result = render("generic_complaint", context)
        assert BURGESS_QUESTION in result

    def test_render_without_burgess(self):
        context = {"your_name": "Test"}
        result = render("generic_complaint", context, include_burgess=False)
        assert BURGESS_QUESTION not in result

    def test_render_missing_template_raises(self):
        with pytest.raises(FileNotFoundError):
            render("this_template_does_not_exist", {})
