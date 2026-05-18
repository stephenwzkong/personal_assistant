"""Integration tests for /api/tasks endpoints."""
import pytest
from unittest.mock import patch

from fixtures.tasks import make_task


@pytest.fixture
def mock_task_tools():
    tasks = [make_task()]
    with patch("tools.productivity.task_tools.get_all_tasks", return_value={"status": "success", "tasks": tasks, "count": 1}) as mock_get, \
         patch("tools.productivity.task_tools.update_task_status", return_value={"status": "success", "task_id": "task-test-001", "new_status": "in_progress"}) as mock_update, \
         patch("tools.productivity.task_tools.delete_task", return_value={"status": "success", "deleted_task_id": "task-test-001"}) as mock_delete:
        yield mock_get, mock_update, mock_delete


class TestTasksEndpoints:
    @pytest.mark.asyncio
    async def test_list_tasks(self, app_client, mock_task_tools):
        resp = await app_client.get("/api/tasks")
        assert resp.status_code == 200
        data = resp.json()
        assert "tasks" in data
        assert "count" in data
        assert data["count"] == 1
        assert data["tasks"][0]["title"] == "Buy groceries"

    @pytest.mark.asyncio
    async def test_task_response_schema(self, app_client, mock_task_tools):
        resp = await app_client.get("/api/tasks")
        task = resp.json()["tasks"][0]
        expected_keys = {"task_id", "parent_task_id", "title", "description", "status",
                         "priority", "category", "due_date", "position", "created_at", "updated_at"}
        assert set(task.keys()) == expected_keys

    @pytest.mark.asyncio
    async def test_move_task(self, app_client, mock_task_tools):
        resp = await app_client.patch("/api/tasks/task-test-001/status", json={"status": "in_progress"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

    @pytest.mark.asyncio
    async def test_delete_task(self, app_client, mock_task_tools):
        resp = await app_client.delete("/api/tasks/task-test-001")
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"
