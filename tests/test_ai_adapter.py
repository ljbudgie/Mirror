"""Tests for core.ai_adapter — local AI integration.

These tests verify prompt loading, config handling, and the adapter's
fallback behaviour. Actual AI backend calls are mocked — no Ollama
instance is required.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

import pytest

from core import ai_adapter
from core.ai_adapter import (
    AIBackendError,
    AIConfig,
    adaptive_burgess_question,
    adaptive_classify,
    generate,
    is_backend_available,
    list_prompts,
    load_config,
    load_system_prompt,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture()
def sample_config():
    """Return a sample AIConfig for testing."""
    return AIConfig(
        enabled=True,
        model="mistral",
        base_url="http://localhost:11434",
        timeout=30.0,
    )


@pytest.fixture()
def disabled_config():
    """Return a disabled AIConfig."""
    return AIConfig(enabled=False)


@pytest.fixture()
def config_file(tmp_path):
    """Write a temporary mirror-config.json and return its path."""
    data = {
        "jurisdiction": "UK",
        "ai": {
            "enabled": True,
            "model": "llama3",
            "base_url": "http://localhost:11434",
            "timeout": 60,
        },
    }
    path = tmp_path / "mirror-config.json"
    path.write_text(json.dumps(data))
    return path


@pytest.fixture()
def config_file_no_ai(tmp_path):
    """Write a config file without AI section."""
    data = {"jurisdiction": "UK"}
    path = tmp_path / "mirror-config.json"
    path.write_text(json.dumps(data))
    return path


# ── load_config ──────────────────────────────────────────────────────────────


class TestLoadConfig:
    def test_loads_from_file(self, config_file):
        config = load_config(config_file)
        assert config.enabled is True
        assert config.model == "llama3"
        assert config.base_url == "http://localhost:11434"
        assert config.timeout == 60.0

    def test_defaults_when_no_ai_section(self, config_file_no_ai):
        config = load_config(config_file_no_ai)
        assert config.enabled is False
        assert config.model == "mistral"

    def test_defaults_when_file_missing(self, tmp_path):
        config = load_config(tmp_path / "nonexistent.json")
        assert config.enabled is False
        assert config.model == "mistral"

    def test_defaults_on_invalid_json(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("not json")
        config = load_config(path)
        assert config.enabled is False

    def test_returns_ai_config_type(self, config_file):
        config = load_config(config_file)
        assert isinstance(config, AIConfig)


# ── load_system_prompt ───────────────────────────────────────────────────────


class TestLoadSystemPrompt:
    def test_loads_master_system(self):
        prompt = load_system_prompt("master-system")
        assert "Mirror" in prompt
        assert "Burgess Principle" in prompt

    def test_prompt_is_string(self):
        prompt = load_system_prompt("master-system")
        assert isinstance(prompt, str)

    def test_prompt_not_empty(self):
        prompt = load_system_prompt("master-system")
        assert len(prompt) > 100

    def test_missing_prompt_raises(self):
        with pytest.raises(FileNotFoundError, match="not found"):
            load_system_prompt("nonexistent-prompt")

    def test_prompt_contains_workflow(self):
        prompt = load_system_prompt("master-system")
        assert "Classify" in prompt

    def test_prompt_contains_json_format(self):
        prompt = load_system_prompt("master-system")
        assert "classification" in prompt
        assert "burgess_question" in prompt


# ── list_prompts ─────────────────────────────────────────────────────────────


class TestListPrompts:
    def test_returns_list(self):
        prompts = list_prompts()
        assert isinstance(prompts, list)

    def test_master_system_present(self):
        prompts = list_prompts()
        assert "master-system" in prompts

    def test_returns_strings(self):
        for name in list_prompts():
            assert isinstance(name, str)


# ── is_backend_available ─────────────────────────────────────────────────────


class TestIsBackendAvailable:
    def test_returns_false_when_unreachable(self, sample_config):
        # No Ollama server running in CI
        assert is_backend_available(sample_config) is False

    def test_returns_false_with_default_config(self):
        assert is_backend_available() is False

    @mock.patch("core.ai_adapter.httpx")
    def test_returns_true_when_reachable(self, mock_httpx, sample_config):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_httpx.get.return_value = mock_response
        mock_httpx.ConnectError = Exception
        mock_httpx.TimeoutException = Exception
        assert is_backend_available(sample_config) is True

    @mock.patch("core.ai_adapter.httpx")
    def test_returns_false_on_connection_error(self, mock_httpx, sample_config):
        mock_httpx.ConnectError = type("ConnectError", (Exception,), {})
        mock_httpx.TimeoutException = type("TimeoutException", (Exception,), {})
        mock_httpx.get.side_effect = mock_httpx.ConnectError("refused")
        assert is_backend_available(sample_config) is False

    def test_returns_false_when_httpx_missing(self, sample_config):
        with mock.patch.object(ai_adapter, "_HTTPX_AVAILABLE", False):
            assert is_backend_available(sample_config) is False


# ── generate ─────────────────────────────────────────────────────────────────


class TestGenerate:
    def _mock_ollama_response(self, result_dict):
        """Create a mock httpx response wrapping a JSON result."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": json.dumps(result_dict),
        }
        mock_response.raise_for_status = mock.Mock()
        return mock_response

    @mock.patch("core.ai_adapter.httpx")
    def test_returns_parsed_json(self, mock_httpx, sample_config):
        expected = {
            "classification": {"main_category": "Benefits / Welfare", "sub_type": "PIP"},
            "burgess_question": "Was a human able to review my case?",
        }
        mock_httpx.post.return_value = self._mock_ollama_response(expected)
        mock_httpx.ConnectError = Exception
        mock_httpx.TimeoutException = Exception
        mock_httpx.HTTPStatusError = Exception

        result = generate("My PIP was refused", config=sample_config)
        assert result["classification"]["main_category"] == "Benefits / Welfare"

    @mock.patch("core.ai_adapter.httpx")
    def test_raises_on_connect_error(self, mock_httpx, sample_config):
        mock_httpx.ConnectError = type("ConnectError", (Exception,), {})
        mock_httpx.TimeoutException = type("TimeoutException", (Exception,), {})
        mock_httpx.HTTPStatusError = type("HTTPStatusError", (Exception,), {})
        mock_httpx.post.side_effect = mock_httpx.ConnectError("refused")

        with pytest.raises(AIBackendError, match="Cannot connect"):
            generate("test", config=sample_config)

    @mock.patch("core.ai_adapter.httpx")
    def test_raises_on_timeout(self, mock_httpx, sample_config):
        mock_httpx.ConnectError = type("ConnectError", (Exception,), {})
        mock_httpx.TimeoutException = type("TimeoutException", (Exception,), {})
        mock_httpx.HTTPStatusError = type("HTTPStatusError", (Exception,), {})
        mock_httpx.post.side_effect = mock_httpx.TimeoutException("timeout")

        with pytest.raises(AIBackendError, match="timed out"):
            generate("test", config=sample_config)

    @mock.patch("core.ai_adapter.httpx")
    def test_raises_on_invalid_model_json(self, mock_httpx, sample_config):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "not valid json"}
        mock_response.raise_for_status = mock.Mock()
        mock_httpx.post.return_value = mock_response
        mock_httpx.ConnectError = Exception
        mock_httpx.TimeoutException = Exception
        mock_httpx.HTTPStatusError = Exception

        with pytest.raises(AIBackendError, match="not valid JSON"):
            generate("test", config=sample_config)

    @mock.patch("core.ai_adapter.httpx")
    def test_uses_system_prompt(self, mock_httpx, sample_config):
        expected = {"classification": {"main_category": "Other"}}
        mock_httpx.post.return_value = self._mock_ollama_response(expected)
        mock_httpx.ConnectError = Exception
        mock_httpx.TimeoutException = Exception
        mock_httpx.HTTPStatusError = Exception

        generate("test", system_prompt="Custom prompt: ", config=sample_config)

        call_kwargs = mock_httpx.post.call_args
        sent_json = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert "Custom prompt: test" in sent_json["prompt"]

    @mock.patch("core.ai_adapter.httpx")
    def test_loads_master_prompt_by_default(self, mock_httpx, sample_config):
        expected = {"classification": {"main_category": "Other"}}
        mock_httpx.post.return_value = self._mock_ollama_response(expected)
        mock_httpx.ConnectError = Exception
        mock_httpx.TimeoutException = Exception
        mock_httpx.HTTPStatusError = Exception

        generate("test", config=sample_config)

        call_kwargs = mock_httpx.post.call_args
        sent_json = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert "Burgess Principle" in sent_json["prompt"]

    def test_raises_without_httpx(self, sample_config):
        with mock.patch.object(ai_adapter, "_HTTPX_AVAILABLE", False):
            with pytest.raises(RuntimeError, match="httpx"):
                generate("test", config=sample_config)


# ── adaptive_classify ────────────────────────────────────────────────────────


class TestAdaptiveClassify:
    def test_returns_none_when_disabled(self, disabled_config):
        result = adaptive_classify("My PIP was refused", config=disabled_config)
        assert result is None

    @mock.patch("core.ai_adapter.generate")
    def test_returns_result_when_enabled(self, mock_generate, sample_config):
        expected = {
            "classification": {"main_category": "Benefits / Welfare"},
            "burgess_question": "Was a human able to review?",
        }
        mock_generate.return_value = expected
        result = adaptive_classify("My PIP was refused", config=sample_config)
        assert result is not None
        assert result["classification"]["main_category"] == "Benefits / Welfare"

    @mock.patch("core.ai_adapter.generate")
    def test_returns_none_on_error(self, mock_generate, sample_config):
        mock_generate.side_effect = AIBackendError("fail")
        result = adaptive_classify("test", config=sample_config)
        assert result is None

    @mock.patch("core.ai_adapter.generate")
    def test_returns_none_on_runtime_error(self, mock_generate, sample_config):
        mock_generate.side_effect = RuntimeError("no httpx")
        result = adaptive_classify("test", config=sample_config)
        assert result is None


# ── adaptive_burgess_question ────────────────────────────────────────────────


class TestAdaptiveBurgessQuestion:
    def test_returns_none_when_disabled(self, disabled_config):
        result = adaptive_burgess_question(
            "My PIP was refused", "benefits", config=disabled_config
        )
        assert result is None

    @mock.patch("core.ai_adapter.generate")
    def test_returns_question_when_available(self, mock_generate, sample_config):
        mock_generate.return_value = {
            "burgess_question": "Did a human review my specific PIP assessment?"
        }
        result = adaptive_burgess_question(
            "My PIP was refused", "benefits", config=sample_config
        )
        assert result is not None
        assert "PIP" in result

    @mock.patch("core.ai_adapter.generate")
    def test_returns_none_on_error(self, mock_generate, sample_config):
        mock_generate.side_effect = AIBackendError("fail")
        result = adaptive_burgess_question("test", "benefits", config=sample_config)
        assert result is None

    @mock.patch("core.ai_adapter.generate")
    def test_returns_none_on_empty_question(self, mock_generate, sample_config):
        mock_generate.return_value = {"burgess_question": ""}
        result = adaptive_burgess_question("test", "benefits", config=sample_config)
        assert result is None

    @mock.patch("core.ai_adapter.generate")
    def test_returns_none_on_missing_key(self, mock_generate, sample_config):
        mock_generate.return_value = {"other": "value"}
        result = adaptive_burgess_question("test", "benefits", config=sample_config)
        assert result is None


# ── AIBackendError ───────────────────────────────────────────────────────────


class TestAIBackendError:
    def test_is_exception(self):
        assert issubclass(AIBackendError, Exception)

    def test_message_preserved(self):
        err = AIBackendError("something went wrong")
        assert str(err) == "something went wrong"
