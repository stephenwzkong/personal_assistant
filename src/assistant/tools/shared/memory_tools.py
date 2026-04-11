"""ADK function tools exposing the memory service to agents.

These tools rely on the user_id being available in the ADK ToolContext (set by the
runner). We accept it explicitly so the LLM doesn't have to thread it through.
"""
from typing import Optional
from google.adk.tools import ToolContext
from memory import service as memory_service


def _resolve_user_id(tool_context: Optional[ToolContext]) -> str:
    """Pull user_id from the ADK ToolContext, defaulting to 'default_user'."""
    if tool_context is not None:
        try:
            invocation = getattr(tool_context, "_invocation_context", None)
            if invocation is not None and getattr(invocation, "user_id", None):
                return invocation.user_id
        except Exception:
            pass
    return "default_user"


def _resolve_session_id(tool_context: Optional[ToolContext]) -> Optional[str]:
    if tool_context is not None:
        try:
            invocation = getattr(tool_context, "_invocation_context", None)
            if invocation is not None:
                sess = getattr(invocation, "session", None)
                if sess is not None:
                    return getattr(sess, "id", None)
        except Exception:
            pass
    return None


def save_memory(
    category: str,
    subject: str,
    value: str,
    confidence: float = 0.9,
    tool_context: ToolContext = None,
) -> dict:
    """Persist a stable fact about the user (preference, goal, constraint, etc.).

    Use this when the user states something durable about themselves that future
    sessions should remember. Examples:
      - User says "I prefer morning workouts" → save_memory("preference", "workout.preferred_time", "morning")
      - User says "I'm vegetarian" → save_memory("constraint", "diet.type", "vegetarian")
      - User says "I want to read 24 books this year" → save_memory("goal", "reading.books_per_year", "24")

    Args:
        category: One of preference|profile|relationship|goal|constraint|location|routine.
        subject: A short dotted-path identifier (e.g. "workout.preferred_time").
        value: The fact value as plain text.
        confidence: 0.0–1.0 confidence in this fact (default 0.9).

    Returns:
        dict with status and the saved subject/value.
    """
    user_id = _resolve_user_id(tool_context)
    session_id = _resolve_session_id(tool_context)
    return memory_service.save_memory(
        user_id=user_id,
        category=category,
        subject=subject,
        value=value,
        confidence=confidence,
        source_session=session_id,
    )


def recall_memory(
    query: str = "",
    category: str = "",
    limit: int = 10,
    tool_context: ToolContext = None,
) -> dict:
    """Retrieve facts about the user from long-term memory.

    Use this when you need to know something about the user that wasn't in the
    current conversation. Examples:
      - Before recommending a workout time → recall_memory(category="preference")
      - Before suggesting a meal → recall_memory(query="diet")

    Args:
        query: Optional keyword to filter on (matches subject and value).
        category: Optional category filter (preference|goal|constraint|...).
        limit: Maximum number of facts to return (default 10).

    Returns:
        dict with 'facts' list, each {category, subject, value, confidence}.
    """
    user_id = _resolve_user_id(tool_context)
    return memory_service.recall_memory(
        user_id=user_id,
        query=query or None,
        category=category or None,
        limit=limit,
    )


def forget_memory(subject: str, tool_context: ToolContext = None) -> dict:
    """Delete a previously saved fact when the user asks you to forget it.

    Args:
        subject: The dotted-path subject to delete (e.g. "workout.preferred_time").
    """
    user_id = _resolve_user_id(tool_context)
    return memory_service.forget_memory(user_id=user_id, subject=subject)
