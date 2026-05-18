"""Unit tests for memory.firestore_session_service."""
import pytest
from unittest.mock import MagicMock

from fixtures.users import TEST_USER_ID, TEST_SESSION_ID


class TestFirestoreSessionService:
    @pytest.fixture
    def svc(self, mock_firestore_client):
        from memory.firestore_session_service import FirestoreSessionService
        return FirestoreSessionService(project_id="test-project")

    @pytest.mark.asyncio
    async def test_create_session(self, svc, mock_firestore_client):
        session = await svc.create_session(
            app_name="test_app",
            user_id=TEST_USER_ID,
            session_id=TEST_SESSION_ID,
        )
        assert session.id == TEST_SESSION_ID
        assert session.user_id == TEST_USER_ID
        assert session.app_name == "test_app"
        mock_firestore_client.collection.return_value.document.return_value.set.assert_called()

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, svc, mock_firestore_client):
        session = await svc.get_session(
            app_name="test_app",
            user_id=TEST_USER_ID,
            session_id="nonexistent",
        )
        assert session is None

    @pytest.mark.asyncio
    async def test_get_session_found(self, svc, mock_firestore_client):
        from google.adk.sessions import Session

        stored_session = Session(
            app_name="test_app",
            user_id=TEST_USER_ID,
            id=TEST_SESSION_ID,
            state={},
            last_update_time=1000.0,
        )
        doc_snap = MagicMock()
        doc_snap.exists = True
        doc_snap.to_dict.return_value = {
            "app_name": "test_app",
            "user_id": TEST_USER_ID,
            "session_id": TEST_SESSION_ID,
            "payload": stored_session.model_dump_json(),
        }
        mock_firestore_client.collection.return_value.document.return_value.get.return_value = doc_snap

        session = await svc.get_session(
            app_name="test_app",
            user_id=TEST_USER_ID,
            session_id=TEST_SESSION_ID,
        )
        assert session is not None
        assert session.id == TEST_SESSION_ID

    @pytest.mark.asyncio
    async def test_delete_session(self, svc, mock_firestore_client):
        await svc.delete_session(
            app_name="test_app",
            user_id=TEST_USER_ID,
            session_id=TEST_SESSION_ID,
        )
        mock_firestore_client.collection.return_value.document.return_value.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_sessions(self, svc, mock_firestore_client):
        result = await svc.list_sessions(app_name="test_app", user_id=TEST_USER_ID)
        assert result.sessions == []


class TestStateSplit:
    def test_prefixes_route_correctly(self):
        from memory.firestore_session_service import _split_state

        state = {
            "app:theme": "dark",
            "user:name": "Stephen",
            "temp:draft": "ignore me",
            "session_key": "session_value",
        }
        app_s, user_s, sess_s = _split_state(state)
        assert app_s == {"theme": "dark"}
        assert user_s == {"name": "Stephen"}
        assert sess_s == {"session_key": "session_value"}
        assert "draft" not in sess_s
