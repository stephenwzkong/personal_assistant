"""Integration tests for /api/session endpoints."""
import pytest


class TestSessionInit:
    @pytest.mark.asyncio
    async def test_init_returns_session(self, app_client):
        resp = await app_client.post("/api/session/init")
        assert resp.status_code == 200
        data = resp.json()
        assert "session_id" in data
        assert "user_id" in data
        assert len(data["session_id"]) == 36

    @pytest.mark.asyncio
    async def test_default_user_id(self, app_client):
        resp = await app_client.post("/api/session/init")
        data = resp.json()
        assert data["user_id"] == "default_user"

    @pytest.mark.asyncio
    async def test_multiple_inits_return_different_sessions(self, app_client):
        r1 = await app_client.post("/api/session/init")
        r2 = await app_client.post("/api/session/init")
        assert r1.json()["session_id"] != r2.json()["session_id"]
