"""Integration tests for /api/calendar endpoints."""
import pytest
from unittest.mock import patch

from fixtures.events import make_event


@pytest.fixture
def mock_bq_events():
    ev = make_event()
    ev["color"] = "#10B981"
    ev["date"] = "2026-05-17"
    ev["time"] = "07:00"
    with patch("db.bq_client.query_calendar_events", return_value=[ev]) as mock:
        yield mock


class TestCalendarGrid:
    @pytest.mark.asyncio
    async def test_grid_structure(self, app_client, mock_bq_events):
        resp = await app_client.get("/api/calendar/grid")
        assert resp.status_code == 200
        data = resp.json()
        assert "grid" in data
        assert len(data["grid"]) == 6
        assert len(data["grid"][0]) == 7
        assert "week_label" in data
        assert "event_count" in data

    @pytest.mark.asyncio
    async def test_grid_day_fields(self, app_client, mock_bq_events):
        resp = await app_client.get("/api/calendar/grid")
        day = resp.json()["grid"][0][0]
        assert "date" in day
        assert "day_num" in day
        assert "is_today" in day
        assert "events" in day

    @pytest.mark.asyncio
    async def test_grid_week_navigation(self, app_client, mock_bq_events):
        resp = await app_client.get("/api/calendar/grid?week_start=2026-05-11")
        assert resp.status_code == 200
        data = resp.json()
        first_day = data["grid"][0][0]
        assert first_day["date"] == "2026-05-11"


class TestCalendarEvents:
    @pytest.mark.asyncio
    async def test_events_with_date_filter(self, app_client, mock_bq_events):
        resp = await app_client.get("/api/calendar/events?start_date=2026-05-17&end_date=2026-05-24")
        assert resp.status_code == 200
        data = resp.json()
        assert "events" in data
        assert "count" in data
        assert data["count"] == len(data["events"])
