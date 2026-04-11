"""ai_adapter.py — Local AI integration for Mirror.

Mirror can optionally connect to a local AI backend (Ollama or any
OpenAI-compatible local server) to provide adaptive classification,
context-aware rights mapping, and situationally tailored Burgess questions.

When no AI backend is available, Mirror falls back silently to its
deterministic rule-based engine. Nothing changes, nothing breaks.

All communication stays on your device. No data leaves your machine.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Any

# Optional HTTP client — only needed when AI features are used.
try:
    import httpx

    _HTTPX_AVAILABLE = True
except ImportError:  # pragma: no cover
    _HTTPX_AVAILABLE = False


# ── Configuration ────────────────────────────────────────────────────────────

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
_DEFAULT_MODEL = "mistral"
_DEFAULT_BASE_URL = "http://localhost:11434"
_REQUEST_TIMEOUT = 120.0


@dataclass
class AIConfig:
    """Configuration for the local AI backend."""

    enabled: bool = False
    model: str = _DEFAULT_MODEL
    base_url: str = _DEFAULT_BASE_URL
    timeout: float = _REQUEST_TIMEOUT


def load_config(config_path: Path | None = None) -> AIConfig:
    """Load AI configuration from mirror-config.json.

    Args:
        config_path: Path to the config file. Defaults to the project root
                     ``mirror-config.json``.

    Returns:
        An :class:`AIConfig` populated from the config file, or defaults.
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "mirror-config.json"

    if not config_path.exists():
        return AIConfig()

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return AIConfig()

    ai_section = data.get("ai", {})
    return AIConfig(
        enabled=bool(ai_section.get("enabled", False)),
        model=str(ai_section.get("model", _DEFAULT_MODEL)),
        base_url=str(ai_section.get("base_url", _DEFAULT_BASE_URL)),
        timeout=float(ai_section.get("timeout", _REQUEST_TIMEOUT)),
    )


# ── System prompt ────────────────────────────────────────────────────────────


def load_system_prompt(prompt_name: str = "master-system") -> str:
    """Load a system prompt from the prompts directory.

    Args:
        prompt_name: The filename stem (without extension) of the prompt.

    Returns:
        The system prompt text.

    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """
    path = _PROMPTS_DIR / f"{prompt_name}.md"
    if not path.exists():
        raise FileNotFoundError(
            f"System prompt '{prompt_name}' not found at {path}."
        )
    return path.read_text(encoding="utf-8")


def list_prompts() -> list[str]:
    """Return the names (stem) of all available system prompts."""
    if not _PROMPTS_DIR.exists():
        return []
    return sorted(p.stem for p in _PROMPTS_DIR.glob("*.md"))


# ── AI backend communication ────────────────────────────────────────────────


def _check_httpx() -> None:
    """Raise a clear error if httpx is not installed."""
    if not _HTTPX_AVAILABLE:
        raise RuntimeError(
            "The 'httpx' package is required for AI features. "
            "Install it with: pip install httpx"
        )


def is_backend_available(config: AIConfig | None = None) -> bool:
    """Check whether the local AI backend is reachable.

    Args:
        config: AI configuration. If None, loads from config file.

    Returns:
        True if the backend responds, False otherwise.
    """
    if not _HTTPX_AVAILABLE:
        return False

    if config is None:
        config = load_config()

    try:
        response = httpx.get(
            f"{config.base_url}/api/tags",
            timeout=5.0,
        )
        return response.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException, OSError):
        return False


def generate(
    user_message: str,
    system_prompt: str | None = None,
    config: AIConfig | None = None,
) -> dict[str, Any]:
    """Send a message to the local AI backend and return structured output.

    Uses the Ollama ``/api/generate`` endpoint with JSON mode.

    Args:
        user_message:  The user's situation description.
        system_prompt: The system prompt to use. If None, loads the master
                       system prompt from the prompts directory.
        config:        AI configuration. If None, loads from config file.

    Returns:
        A dict parsed from the AI's JSON response. Keys match the
        master system prompt schema: ``classification``, ``rights_mapping``,
        ``burgess_question``, ``next_step``, ``deadlines``,
        ``recommended_template``, ``calm_message``.

    Raises:
        RuntimeError: If httpx is not installed or the backend is unreachable.
        AIBackendError: If the backend returns an error or invalid JSON.
    """
    _check_httpx()

    if config is None:
        config = load_config()

    if system_prompt is None:
        system_prompt = load_system_prompt()

    full_prompt = system_prompt + user_message

    try:
        response = httpx.post(
            f"{config.base_url}/api/generate",
            json={
                "model": config.model,
                "prompt": full_prompt,
                "stream": False,
                "format": "json",
            },
            timeout=config.timeout,
        )
        response.raise_for_status()
    except httpx.ConnectError as exc:
        raise AIBackendError(
            f"Cannot connect to AI backend at {config.base_url}. "
            "Is Ollama running? Start it with: ollama serve"
        ) from exc
    except httpx.TimeoutException as exc:
        raise AIBackendError(
            "AI backend timed out. The model may still be loading. "
            "Try again in a moment."
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise AIBackendError(
            f"AI backend returned HTTP {exc.response.status_code}."
        ) from exc

    try:
        body = response.json()
    except (json.JSONDecodeError, ValueError) as exc:
        raise AIBackendError(
            "AI backend returned invalid JSON in the response envelope."
        ) from exc

    # Ollama wraps the model output in a "response" field.
    raw_text = body.get("response", "")

    try:
        result = json.loads(raw_text)
    except (json.JSONDecodeError, ValueError) as exc:
        raise AIBackendError(
            "AI model returned text that is not valid JSON. "
            f"Raw output: {raw_text[:200]}"
        ) from exc

    return result


class AIBackendError(Exception):
    """Raised when the AI backend returns an error or unexpected response."""


# ── High-level adaptive helpers ──────────────────────────────────────────────


def adaptive_classify(
    text: str,
    config: AIConfig | None = None,
) -> dict[str, Any] | None:
    """Attempt AI-powered classification of a user's situation.

    Falls back to None if AI is not available or fails, allowing the caller
    to use the deterministic classifier instead.

    Args:
        text:   The user's plain-English description.
        config: AI configuration. If None, loads from config file.

    Returns:
        A dict with at least ``classification``, or None on failure.
    """
    if config is None:
        config = load_config()

    if not config.enabled:
        return None

    try:
        return generate(text, config=config)
    except (AIBackendError, RuntimeError, FileNotFoundError):
        return None


def adaptive_burgess_question(
    text: str,
    domain: str,
    config: AIConfig | None = None,
) -> str | None:
    """Generate a situation-specific Burgess Principle question using AI.

    Falls back to None if AI is not available, allowing the caller to
    use the static Burgess question from template_engine.py.

    Args:
        text:   The user's situation description.
        domain: The classified domain.
        config: AI configuration. If None, loads from config file.

    Returns:
        A tailored Burgess question string, or None on failure.
    """
    if config is None:
        config = load_config()

    if not config.enabled:
        return None

    burgess_prompt = (
        "You are Mirror, applying the Burgess Principle (UK00004343685). "
        f"The user's situation has been classified as '{domain}'. "
        "Generate exactly one pointed question that demands human "
        "accountability for the user's specific situation. "
        "The question should be calm, precise, and empowering. "
        "Respond with valid JSON only: "
        '{"burgess_question": "your question here"}\n\n'
        "User situation:\n"
    )

    try:
        result = generate(text, system_prompt=burgess_prompt, config=config)
        question = result.get("burgess_question")
        return question if isinstance(question, str) and question else None
    except (AIBackendError, RuntimeError):
        return None
