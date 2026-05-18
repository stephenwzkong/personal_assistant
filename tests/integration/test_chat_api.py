"""Integration tests for /api/chat endpoints — mocked runner."""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
def mock_runner():
    with patch("runner.run_agent", new_callable=AsyncMock) as mock:
        mock.return_value = "I can help with that!"
        yield mock


class TestChatEndpoint:
    @pytest.mark.asyncio
    async def test_chat_returns_response(self, app_client, mock_runner):
        resp = await app_client.post("/api/chat", json={
            "session_id": "sess-001",
            "user_id": "user-001",
            "message": "Hello!",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "assistant"
        assert data["content"] == "I can help with that!"
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_chat_response_schema(self, app_client, mock_runner):
        resp = await app_client.post("/api/chat", json={
            "session_id": "sess-001",
            "user_id": "user-001",
            "message": "What can you do?",
        })
        data = resp.json()
        assert set(data.keys()) == {"role", "content", "timestamp"}

    @pytest.mark.asyncio
    async def test_chat_invalid_body(self, app_client, mock_runner):
        resp = await app_client.post("/api/chat", json={"message": "no session"})
        assert resp.status_code == 422


class TestDomainChatEndpoint:
    @pytest.mark.asyncio
    async def test_domain_chat_prefixes_message(self, app_client, mock_runner):
        resp = await app_client.post("/api/chat/domain", json={
            "session_id": "sess-001",
            "user_id": "user-001",
            "message": "Log a run",
            "domain": "wellness",
        })
        assert resp.status_code == 200
        call_kwargs = mock_runner.call_args[1]
        assert "[Wellness context]" in call_kwargs["message"]
