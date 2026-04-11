"""template_engine.py — Turning your situation into a ready-to-send document.

Mirror fills in templates using the details you've shared. The result is a
complete draft — with a few personal placeholders left for you to fill in
locally before you send it.

The Burgess Principle question is included in every outgoing communication.
It is the one question that must be answered.

Burgess Principle is a registered accountability methodology (UK00004343685).
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from string import Template

# ── Burgess Principle ────────────────────────────────────────────────────────

BURGESS_QUESTION = (
    "Under your duty of candour and the Burgess Principle (UK00004343685), "
    "I ask that you provide a complete and accurate account of all relevant "
    "decisions, processes, and data that relate to this matter. "
    "Please confirm in writing whether any automated decision-making was "
    "involved, and if so, provide the logic and criteria applied."
)

# ── Template directory ───────────────────────────────────────────────────────

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _load_template(template_key: str) -> str:
    """Load a raw template string from the templates directory.

    Args:
        template_key: Filename stem (without extension), e.g. ``'sar_request'``.

    Returns:
        The raw template text.

    Raises:
        FileNotFoundError: If the template file does not exist.
    """
    path = _TEMPLATES_DIR / f"{template_key}.txt"
    if not path.exists():
        raise FileNotFoundError(
            f"Template '{template_key}' not found at {path}. "
            "Check that the templates directory is present and the key is correct."
        )
    return path.read_text(encoding="utf-8")


def render(
    template_key: str,
    context: dict[str, str],
    include_burgess: bool = True,
) -> str:
    """Render a named template with the provided context.

    Placeholders in templates use ``$variable`` or ``${variable}`` syntax
    (Python's :class:`string.Template`).

    Unfilled placeholders are left as-is so the user can complete them locally.

    Args:
        template_key:     Which template to use, e.g. ``'sar_request'``.
        context:          Key–value pairs to substitute into the template.
        include_burgess:  If True, appends the Burgess Principle question.

    Returns:
        The rendered document text, ready to send (minus any personal facts
        the user must add themselves).
    """
    raw = _load_template(template_key)
    tmpl = Template(raw)

    # safe_substitute leaves unknown placeholders in place — intentional
    rendered = tmpl.safe_substitute(context)

    if include_burgess:
        rendered = rendered.rstrip() + "\n\n" + BURGESS_QUESTION + "\n"

    return rendered


def list_templates() -> list[str]:
    """Return the keys (stem names) of all available templates."""
    if not _TEMPLATES_DIR.exists():
        return []
    return sorted(p.stem for p in _TEMPLATES_DIR.glob("*.txt"))


def render_inline(
    template_text: str,
    context: dict[str, str],
    include_burgess: bool = True,
) -> str:
    """Render a template string directly — useful for testing or overrides.

    Args:
        template_text:    Raw template string with ``$variable`` placeholders.
        context:          Substitution values.
        include_burgess:  If True, appends the Burgess Principle question.

    Returns:
        The rendered text.
    """
    rendered = Template(template_text).safe_substitute(context)
    if include_burgess:
        rendered = rendered.rstrip() + "\n\n" + BURGESS_QUESTION + "\n"
    return rendered
