"""Error-path tests — BQ timeouts, connection errors, malformed inputs."""
from unittest.mock import MagicMock

import pytest


class TestBigQueryErrors:
    def test_bq_timeout_returns_error(self, mock_bq_client):
        from memory.service import save_memory

        mock_bq_client.query.return_value.result.side_effect = TimeoutError("query timed out")

        result = save_memory(user_id="u", category="preference", subject="k", value="v")
        assert result["status"] == "error"
        assert "timed out" in result["error_message"]

    def test_bq_connection_error_in_recall(self, mock_bq_client):
        from memory.service import recall_memory

        mock_bq_client.query.return_value.result.side_effect = ConnectionError("network down")

        result = recall_memory(user_id="u")
        assert result["status"] == "error"
        assert "network" in result["error_message"].lower()

    def test_bq_insert_error_in_calendar(self, mock_bq_client):
        from tools.shared.calendar_tools import create_calendar_event

        mock_bq_client.insert_rows_json.side_effect = Exception("quota exceeded")

        result = create_calendar_event(
            title="Fail",
            start_datetime="2026-05-17T09:00:00",
            end_datetime="2026-05-17T10:00:00",
        )
        assert result["status"] == "error"
        assert "quota" in result["error_message"].lower()

    def test_bq_error_in_get_all_tasks(self, mock_bq_client):
        from tools.productivity.task_tools import get_all_tasks

        mock_bq_client.query.side_effect = Exception("service unavailable")

        result = get_all_tasks()
        assert result["status"] == "error"


class TestCalendarValidation:
    def test_invalid_priority_defaults(self, mock_bq_client):
        from tools.shared.calendar_tools import create_calendar_event

        result = create_calendar_event(
            title="Test",
            start_datetime="2026-05-17T09:00:00",
            end_datetime="2026-05-17T10:00:00",
            priority="urgent",
        )
        assert result["status"] == "success"
        rows = mock_bq_client.insert_rows_json.call_args[0][1]
        assert rows[0]["priority"] == "medium"


class TestTaskValidation:
    def test_update_no_fields_returns_error(self):
        from tools.productivity.task_tools import update_task

        result = update_task(task_id="task-001")
        assert result["status"] == "error"
        assert "No fields" in result["error_message"]
