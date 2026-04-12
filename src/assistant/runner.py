"""ADK Runner singleton and session management for the personal assistant."""
import os
import sys

# Ensure the assistant's src directory is on the path so agent imports work
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

from google.adk.runners import Runner
from google.adk.sessions import BaseSessionService, InMemorySessionService
from google.genai import types as genai_types

from telemetry import init_phoenix

# Lazy-import orchestrator to avoid circular imports at module load time
_runner: Runner | None = None
_session_service: BaseSessionService | None = None
APP_NAME = "personal_assistant"

# Toggle Firestore-backed sessions via env var (default ON in production-like envs)
USE_FIRESTORE = os.environ.get("PA_USE_FIRESTORE_SESSIONS", "1") not in ("0", "false", "False")


def _build_session_service() -> BaseSessionService:
    if USE_FIRESTORE:
        try:
            from memory.firestore_session_service import FirestoreSessionService
            return FirestoreSessionService()
        except Exception as e:
            print(f"[runner] FirestoreSessionService unavailable, falling back to in-memory: {e}")
    return InMemorySessionService()


def _get_runner() -> Runner:
    global _runner, _session_service
    if _runner is None:
        init_phoenix()
        from agents.root_orchestrator import root_orchestrator
        _session_service = _build_session_service()
        _runner = Runner(
            app_name=APP_NAME,
            agent=root_orchestrator,
            session_service=_session_service,
        )
    return _runner


def _get_session_service() -> BaseSessionService:
    _get_runner()  # ensures _session_service is initialized
    return _session_service  # type: ignore[return-value]


async def ensure_session(session_id: str, user_id: str) -> None:
    """Create a session if it doesn't exist yet."""
    svc = _get_session_service()
    existing = await svc.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    if existing is None:
        await svc.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        # Record session start in BigQuery memory_sessions (best-effort)
        try:
            from memory import service as memory_service
            memory_service.record_session_start(session_id=session_id, user_id=user_id)
        except Exception:
            pass


async def run_agent(session_id: str, user_id: str, message: str) -> str:
    """Send a message to the orchestrator and return the final text response.

    Args:
        session_id: Unique session identifier (per browser tab).
        user_id: User identifier.
        message: User's message text.

    Returns:
        The agent's final text response.
    """
    await ensure_session(session_id, user_id)
    runner = _get_runner()

    content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=message)],
    )

    final_response = ""
    event_count = 0
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):
            event_count += 1
            author = getattr(event, "author", "?")
            is_final = event.is_final_response()
            parts_summary = []
            if event.content and event.content.parts:
                for p in event.content.parts:
                    if getattr(p, "text", None):
                        parts_summary.append(f"text[{len(p.text)}]")
                    elif getattr(p, "function_call", None):
                        parts_summary.append(f"fn_call:{p.function_call.name}")
                    elif getattr(p, "function_response", None):
                        parts_summary.append(f"fn_resp:{p.function_response.name}")
                    else:
                        parts_summary.append("other")
            content_none = event.content is None
            actions_info = ""
            if hasattr(event, "actions") and event.actions:
                a = event.actions
                bits = []
                if getattr(a, "transfer_to_agent", None):
                    bits.append(f"transfer={a.transfer_to_agent}")
                if getattr(a, "escalate", None):
                    bits.append("escalate")
                if getattr(a, "state_delta", None):
                    bits.append(f"state_keys={list(a.state_delta.keys())}")
                actions_info = " actions=" + ",".join(bits) if bits else ""
            print(f"[run_agent] evt#{event_count} author={author} final={is_final} content_none={content_none} parts={parts_summary}{actions_info}", flush=True)
            if event_count >= 3 and not parts_summary and not content_none:
                try:
                    print(f"[run_agent]   raw_content={event.content.model_dump_json()[:500]}", flush=True)
                except Exception as _e:
                    print(f"[run_agent]   raw_content_err={_e}", flush=True)
            if event.content and event.content.parts:
                for p in event.content.parts:
                    if getattr(p, "text", None):
                        final_response = p.text
    except Exception as e:
        import traceback
        print(f"[run_agent] EXCEPTION: {e}\n{traceback.format_exc()}", flush=True)
        return f"Error: {e}"

    print(f"[run_agent] done: {event_count} events, response_len={len(final_response)}", flush=True)
    return final_response or "I'm sorry, I couldn't generate a response. Please try again."
