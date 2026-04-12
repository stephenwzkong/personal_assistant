"""Load agent instructions from prompts/ and knowledge/ markdown files.

Agents instantiate once at module import time, so file reads happen once
at startup — no caching needed.
"""
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent  # src/assistant
_PROMPTS_DIR = _ROOT / "prompts"
_KNOWLEDGE_DIR = _ROOT / "knowledge"


def load_prompt(rel_path: str) -> str:
    """Read a prompt markdown file relative to prompts/."""
    return (_PROMPTS_DIR / rel_path).read_text(encoding="utf-8").strip()


def load_knowledge(rel_path: str) -> str | None:
    """Read a knowledge markdown file relative to knowledge/. Returns None if missing."""
    path = _KNOWLEDGE_DIR / rel_path
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip()


def build_instruction(prompt_path: str, knowledge_path: str | None = None) -> str:
    """Build an agent instruction from a prompt file plus optional knowledge file.

    The knowledge content is appended under a '## Research Context' section so
    the agent can reference evidence-based domain facts alongside behavior rules.
    """
    prompt = load_prompt(prompt_path)
    if knowledge_path is None:
        return prompt
    knowledge = load_knowledge(knowledge_path)
    if not knowledge:
        return prompt
    return f"{prompt}\n\n## Research Context\n\n{knowledge}"
