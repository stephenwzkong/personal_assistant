"""Unit tests for db.bq_client — calendar query wrapper."""
from datetime import date

import pytest
import pandas as pd


class TestQueryCalendarEvents:
    def test_default_date_range(self, mock_bq_client):
        from db.bq_client import query_calendar_events

        mock_bq_client.query.return_value.to_dataframe.return_value = pd.DataFrame()

        result = query_calendar_events()
        assert result == []
        sql = mock_bq_client.query.call_args[0][0]
        assert "status = 'active'" in sql

    def test_custom_date_range(self, mock_bq_client):
        from db.bq_client import query_calendar_events

        mock_bq_client.query.return_value.to_dataframe.return_value = pd.DataFrame()

        query_calendar_events(start_date="2026-05-01", end_date="2026-05-31")
        sql = mock_bq_client.query.call_args[0][0]
        assert "2026-05-01" in sql
        assert "2026-05-31" in sql

    def test_color_mapping_applied(self, mock_bq_client):
        from db.bq_client import query_calendar_events

        ev = {
            "event_id": "e1",
            "title": "Run",
            "start_datetime": "2026-05-17T07:00:00",
            "end_datetime": "2026-05-17T08:00:00",
            "event_type": "workout",
            "source_agent": None,
            "priority": "medium",
            "status": "active",
            "description": None,
        }
        df = pd.DataFrame([ev])
        mock_bq_client.query.return_value.to_dataframe.return_value = df

        events = query_calendar_events(start_date="2026-05-17", end_date="2026-05-17")
        assert len(events) == 1
        assert events[0]["color"] == "#10B981"
        assert events[0]["date"] == "2026-05-17"
        assert events[0]["time"] == "07:00"

    def test_exception_returns_empty_list(self, mock_bq_client):
        from db.bq_client import query_calendar_events

        mock_bq_client.query.side_effect = Exception("network error")

        result = query_calendar_events()
        assert result == []


class TestGetWeekStart:
    def test_returns_monday(self):
        from db.bq_client import get_week_start

        result = get_week_start("2026-05-17")
        assert result == "2026-05-11"

    def test_monday_returns_itself(self):
        from db.bq_client import get_week_start

        result = get_week_start("2026-05-11")
        assert result == "2026-05-11"

    def test_defaults_to_today(self):
        from db.bq_client import get_week_start

        result = get_week_start()
        parsed = date.fromisoformat(result)
        assert parsed.weekday() == 0
