"""Unit tests for tools.productivity.task_tools."""
from unittest.mock import MagicMock

import pytest
import pandas as pd

from fixtures.tasks import make_task


class TestCreateTask:
    def test_create_success(self, mock_bq_client):
        from tools.productivity.task_tools import create_task

        pos_row = MagicMock()
        pos_row.__getitem__ = lambda self, k: 1
        mock_bq_client.query.return_value.result.return_value = [pos_row]

        result = create_task(title="Buy milk")
        assert result["status"] == "success"
        assert result["task"]["title"] == "Buy milk"
        assert result["task"]["status"] == "todo"
        mock_bq_client.insert_rows_json.assert_called_once()


class TestCreateTaskWithSteps:
    def test_creates_parent_and_children(self, mock_bq_client):
        from tools.productivity.task_tools import create_task_with_steps

        pos_row = MagicMock()
        pos_row.__getitem__ = lambda self, k: 0
        mock_bq_client.query.return_value.result.return_value = [pos_row]

        result = create_task_with_steps(
            title="Study for exam",
            steps=["Review notes", "Practice problems", "Make flashcards"],
        )
        assert result["status"] == "success"
        assert result["task"]["title"] == "Study for exam"
        assert len(result["steps"]) == 3
        rows = mock_bq_client.insert_rows_json.call_args[0][1]
        assert len(rows) == 4  # 1 parent + 3 steps

        parent_id = result["task"]["task_id"]
        for step in result["steps"]:
            assert step["parent_task_id"] == parent_id


class TestUpdateTaskStatus:
    def test_valid_status_transitions(self, mock_bq_client):
        from tools.productivity.task_tools import update_task_status

        for status in ("todo", "in_progress", "done"):
            result = update_task_status("task-001", status)
            assert result["status"] == "success"
            assert result["new_status"] == status

    def test_invalid_status_returns_error(self):
        from tools.productivity.task_tools import update_task_status

        result = update_task_status("task-001", "archived")
        assert result["status"] == "error"
        assert "Invalid status" in result["error_message"]


class TestDeleteTask:
    def test_delete_cascades_to_children(self, mock_bq_client):
        from tools.productivity.task_tools import delete_task

        result = delete_task("parent-001")
        assert result["status"] == "success"
        sql = mock_bq_client.query.call_args[0][0]
        assert "task_id = @task_id OR parent_task_id = @task_id" in sql


class TestGetAllTasks:
    def test_returns_structured_list(self, mock_bq_client):
        from tools.productivity.task_tools import get_all_tasks

        task_data = make_task()
        df = pd.DataFrame([task_data])
        mock_bq_client.query.return_value.to_dataframe.return_value = df

        result = get_all_tasks()
        assert result["status"] == "success"
        assert result["count"] == 1
        assert result["tasks"][0]["title"] == "Buy groceries"
