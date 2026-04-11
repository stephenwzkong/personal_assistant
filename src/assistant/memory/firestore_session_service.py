"""Firestore-backed ADK session service.

Persists Session snapshots so conversations survive pod restarts. Phase 1 stores
the entire session as a single JSON document per session id. Good enough for
the single-user prototype; revisit subcollections/event sharding if sessions
grow past Firestore's 1 MiB document limit.

Document layout:
  collection: adk_sessions
  doc id:     {app_name}__{user_id}__{session_id}
  fields:
    app_name, user_id, session_id, last_update_time, payload (JSON string)

A separate `adk_user_state/{app_name}__{user_id}` doc holds cross-session
user state.
"""
from __future__ import annotations

import copy
import json
import time
import uuid
from typing import Any, Optional

from google.adk.events import Event
from google.adk.sessions import BaseSessionService, Session
from google.adk.sessions.base_session_service import (
    GetSessionConfig,
    ListSessionsResponse,
)
from google.cloud import firestore


SESSIONS_COLLECTION = "adk_sessions"
USER_STATE_COLLECTION = "adk_user_state"
APP_STATE_COLLECTION = "adk_app_state"

# Prefixes used by ADK to indicate scope of a state key
USER_PREFIX = "user:"
APP_PREFIX = "app:"
TEMP_PREFIX = "temp:"


def _doc_id(app_name: str, user_id: str, session_id: str) -> str:
    return f"{app_name}__{user_id}__{session_id}"


def _user_doc_id(app_name: str, user_id: str) -> str:
    return f"{app_name}__{user_id}"


def _split_state(state: dict[str, Any]) -> tuple[dict, dict, dict]:
    """Split a state dict into (app, user, session) by prefix."""
    app_s, user_s, sess_s = {}, {}, {}
    for k, v in (state or {}).items():
        if k.startswith(APP_PREFIX):
            app_s[k[len(APP_PREFIX):]] = v
        elif k.startswith(USER_PREFIX):
            user_s[k[len(USER_PREFIX):]] = v
        elif k.startswith(TEMP_PREFIX):
            continue
        else:
            sess_s[k] = v
    return app_s, user_s, sess_s


class FirestoreSessionService(BaseSessionService):
    """ADK session service that persists sessions to Cloud Firestore."""

    def __init__(self, project_id: Optional[str] = None):
        pid = project_id or "gen-lang-client-0288149151"
        self._db = firestore.Client(project=pid)

    # ----- helpers -----

    def _session_to_doc(self, session: Session) -> dict:
        return {
            "app_name": session.app_name,
            "user_id": session.user_id,
            "session_id": session.id,
            "last_update_time": session.last_update_time,
            # Use Pydantic JSON to round-trip nested Event objects safely
            "payload": session.model_dump_json(),
        }

    def _doc_to_session(self, doc: dict) -> Session:
        return Session.model_validate_json(doc["payload"])

    def _merge_user_app_state(self, session: Session) -> Session:
        """Overlay user-scoped and app-scoped state into the session copy."""
        app_doc = self._db.collection(APP_STATE_COLLECTION).document(session.app_name).get()
        if app_doc.exists:
            for k, v in (app_doc.to_dict() or {}).items():
                session.state[APP_PREFIX + k] = v

        user_doc = self._db.collection(USER_STATE_COLLECTION).document(
            _user_doc_id(session.app_name, session.user_id)
        ).get()
        if user_doc.exists:
            for k, v in (user_doc.to_dict() or {}).items():
                session.state[USER_PREFIX + k] = v
        return session

    # ----- BaseSessionService API -----

    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        sid = (session_id or "").strip() or str(uuid.uuid4())

        # Check existence
        existing = self._db.collection(SESSIONS_COLLECTION).document(
            _doc_id(app_name, user_id, sid)
        ).get()
        if existing.exists:
            # ADK semantics: raise on duplicate. We'll instead return existing.
            return self._doc_to_session(existing.to_dict())

        app_s, user_s, sess_s = _split_state(state or {})

        # Persist app/user scope deltas
        if app_s:
            self._db.collection(APP_STATE_COLLECTION).document(app_name).set(app_s, merge=True)
        if user_s:
            self._db.collection(USER_STATE_COLLECTION).document(
                _user_doc_id(app_name, user_id)
            ).set(user_s, merge=True)

        session = Session(
            app_name=app_name,
            user_id=user_id,
            id=sid,
            state=sess_s,
            last_update_time=time.time(),
        )

        self._db.collection(SESSIONS_COLLECTION).document(
            _doc_id(app_name, user_id, sid)
        ).set(self._session_to_doc(session))

        return self._merge_user_app_state(copy.deepcopy(session))

    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        snap = self._db.collection(SESSIONS_COLLECTION).document(
            _doc_id(app_name, user_id, session_id)
        ).get()
        if not snap.exists:
            return None
        session = self._doc_to_session(snap.to_dict())

        # Optionally trim events per config
        if config is not None:
            if getattr(config, "num_recent_events", None):
                session.events = session.events[-config.num_recent_events:]
            if getattr(config, "after_timestamp", None):
                session.events = [
                    e for e in session.events if e.timestamp > config.after_timestamp
                ]

        return self._merge_user_app_state(session)

    async def list_sessions(
        self, *, app_name: str, user_id: Optional[str] = None
    ) -> ListSessionsResponse:
        col = self._db.collection(SESSIONS_COLLECTION)
        query = col.where("app_name", "==", app_name)
        if user_id:
            query = query.where("user_id", "==", user_id)
        sessions: list[Session] = []
        for snap in query.stream():
            s = self._doc_to_session(snap.to_dict())
            s.events = []  # match InMemory behavior
            sessions.append(self._merge_user_app_state(s))
        return ListSessionsResponse(sessions=sessions)

    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        self._db.collection(SESSIONS_COLLECTION).document(
            _doc_id(app_name, user_id, session_id)
        ).delete()

    async def append_event(self, session: Session, event: Event) -> Event:
        # Let the base class apply the event to the in-memory session object first
        event = await super().append_event(session=session, event=event)
        if event.partial:
            return event

        session.last_update_time = event.timestamp

        # Apply scoped state deltas to Firestore (separate docs)
        if event.actions and event.actions.state_delta:
            app_s, user_s, sess_s = _split_state(event.actions.state_delta)
            if app_s:
                self._db.collection(APP_STATE_COLLECTION).document(
                    session.app_name
                ).set(app_s, merge=True)
            if user_s:
                self._db.collection(USER_STATE_COLLECTION).document(
                    _user_doc_id(session.app_name, session.user_id)
                ).set(user_s, merge=True)
            # session-scoped deltas are already in session.state via base class

        # Persist the full updated session snapshot
        # (We strip user/app-scope keys before saving so they don't get duplicated.)
        to_save = copy.deepcopy(session)
        to_save.state = {
            k: v for k, v in to_save.state.items()
            if not k.startswith(USER_PREFIX) and not k.startswith(APP_PREFIX)
        }
        self._db.collection(SESSIONS_COLLECTION).document(
            _doc_id(session.app_name, session.user_id, session.id)
        ).set(self._session_to_doc(to_save))

        return event
