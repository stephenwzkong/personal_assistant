"""Unit tests for tools.shared.calendar_tools."""
from unittest.mock import MagicMock

import pytest
import pandas as pd

from fixtures.events import make_event


class TestCreateCalendarEvent:
    def test_create_success(self, mock_bq_client):
        from tools.shared.calendar_tools import create_calendar_event

        result = create_calendar_event(
            title="Morning Run",
            start_datetime="2026-05-17T07:00:00",
            end_datetime="2026-05-17T08:00:00",
            event_type="workout",
        )
        assert result["status"] == "success"
        assert "event_id" in result
        assert result["title"] == "Morning Run"
        mock_bq_client.insert_rows_json.assert_called_once()

    def test_create_invalid_type_defaults_to_other(self, mock_bq_client):
        from tools.shared.calendar_tools import create_calendar_event

        result = create_calendar_event(
            title="Mystery",
            start_datetime="2026-05-17T09:00:00",
            end_datetime="2026-05-17T10:00:00",
            event_type="invalid_type",
        )
        assert result["status"] == "success"
        rows = mock_bq_client.insert_rows_json.call_args[0][1]
        assert rows[0]["event_type"] == "other"

    def test_create_bq_insert_error(self, mock_bq_client):
        from tools.shared.calendar_tools import create_calendar_event

        mock_bq_client.insert_rows_json.return_value = [{"errors": "bad row"}]

        result = create_calendar_event(
            title="Bad",
            start_datetime="2026-05-17T09:00:00",
            end_datetime="2026-05-17T10:00:00",
        )
        assert result["status"] == "error"


class TestListCalendarEvents:
    def test_list_with_date_range(self, mock_bq_client):
        from tools.shared.calendar_tools import list_calendar_events

        ev = make_event()
        df = pd.DataFrame([ev])
        mock_bq_client.query.return_value.to_dataframe.return_value = df

        result = list_calendar_events(start_date="2026-05-17", end_date="2026-05-24")
        assert result["status"] == "success"
        assert result["count"] == 1
        sql = mock_bq_client.query.call_args[0][0]
        assert "2026-05-17" in sql
        assert "2026-05-24" in sql

    def test_list_filters_by_event_type(self, mock_bq_client):
        from tools.shared.calendar_tools import list_calendar_events

        mock_bq_client.query.return_value.to_dataframe.return_value = pd.DataFrame()

        list_calendar_events(event_type="workout")
        sql = mock_bq_client.query.call_args[0][0]
        assert "event_type = 'workout'" in sql


class TestUpdateCalendarEvent:
    def test_update_partial_fields(self, mock_bq_client):
        from tools.shared.calendar_tools import update_calendar_event

        result = update_calendar_event(event_id="evt-001", title="New Title")
        assert result["status"] == "success"
        sql = mock_bq_client.query.call_args[0][0]
        assert "title = @title" in sql
        assert "event_id = @event_id" in sql

    def test_update_invalid_status_returns_error(self):
        from tools.shared.calendar_tools import update_calendar_event

        result = update_calendar_event(event_id="evt-001", status="deleted")
        assert result["status"] == "error"
        assert "Invalid status" in result["error_message"]


class TestDeleteCalendarEvent:
    def test_delete_soft_deletes(self, mock_bq_client):
        from tools.shared.calendar_tools import delete_calendar_event

        result = delete_calendar_event(event_id="evt-001")
        assert result["status"] == "success"
        sql = mock_bq_client.query.call_args[0][0]
        assert "UPDATE" in sql
        params = {p.name: p.value for p in mock_bq_client.query.call_args[1]["job_config"].query_parameters}
        assert params["status"] == "cancelled"


class TestEventColors:
    def test_all_event_types_have_colors(self):
        from tools.shared.calendar_tools import EVENT_COLORS, VALID_EVENT_TYPES

        for et in VALID_EVENT_TYPES:
            assert et in EVENT_COLORS
            assert EVENT_COLORS[et].startswith("#")
