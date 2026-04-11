"""ADK agent callbacks for memory injection.

Phase 1: a `before_agent_callback` that fetches the user's memory bundle and
prepends it to the model's system instructions for this turn only.
"""
from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.genai import types as genai_types

from memory import service as memory_service


# Per-process cache: { (user_id) -> (bundle_text, fetched_at_iso) }
# Trades a tiny bit of staleness for big BQ savings on multi-turn sessions.
_BUNDLE_CACHE: dict[str, tuple[str, float]] = {}
_CACHE_TTL_SECONDS = 300  # 5 min


def _get_bundle(user_id: str) -> str:
    import time
    now = time.time()
    cached = _BUNDLE_CACHE.get(user_id)
    if cached and (now - cached[1] < _CACHE_TTL_SECONDS):
        return cached[0]
    bundle = memory_service.build_bundle(user_id=user_id)
    _BUNDLE_CACHE[user_id] = (bundle, now)
    return bundle


def invalidate_bundle(user_id: str) -> None:
    _BUNDLE_CACHE.pop(user_id, None)


def inject_memory_bundle(callback_context: CallbackContext) -> Optional[genai_types.Content]:
    """Before-agent callback: inject a memory block into session state.

    The block is added to `state['user_memory_block']` which the agent's instruction
    template can reference. Returning None lets the agent run normally.
    """
    try:
        user_id = callback_context._invocation_context.user_id  # type: ignore[attr-defined]
    except Exception:
        user_id = "default_user"

    bundle = _get_bundle(user_id)
    # Stash on session state so instruction templates can reference {user_memory_block}
    try:
        callback_context.state["user_memory_block"] = bundle
    except Exception:
        pass
    return None
