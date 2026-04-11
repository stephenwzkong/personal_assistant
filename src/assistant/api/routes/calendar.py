"""Calendar endpoints — events and grid data."""
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(tags=["calendar"])


class CalendarEventOut(BaseModel):
    event_id: str = ""
    title: str = ""
    time: str = ""
    color: str = "#94A3B8"
    event_type: str = "other"
    date: str = ""
    start_datetime: str = ""
    end_datetime: str = ""
    description: Optional[str] = None


class CalendarDayOut(BaseModel):
    date: str = ""
    day_num: str = ""
    is_today: bool = False
    events: list[CalendarEventOut] = []


class CalendarGridResponse(BaseModel):
    grid: list[list[CalendarDayOut]]
    week_label: str
    event_count: int


class CalendarEventsResponse(BaseModel):
    events: list[CalendarEventOut]
    count: int


def _get_week_start(reference: Optional[str] = None) -> date:
    if reference:
        d = date.fromisoformat(reference)
    else:
        d = date.today()
    return d - timedelta(days=d.weekday())


def _build_grid(events: list[dict], week_start: date) -> list[list[CalendarDayOut]]:
    today_str = date.today().isoformat()

    by_date: dict[str, list[CalendarEventOut]] = {}
    for ev in events:
        d = ev.get("date", "")
        if not d:
            continue
        ce = CalendarEventOut(
            event_id=ev.get("event_id", ""),
            title=ev.get("title", ""),
            time=ev.get("time", ""),
            color=ev.get("color", "#94A3B8"),
            event_type=ev.get("event_type", "other"),
            date=d,
            start_datetime=ev.get("start_datetime", ""),
            end_datetime=ev.get("end_datetime", ""),
            description=ev.get("description"),
        )
        by_date.setdefault(d, []).append(ce)

    weeks: list[list[CalendarDayOut]] = []
    for week_idx in range(6):
        week: list[CalendarDayOut] = []
        for day_idx in range(7):
            d = week_start + timedelta(weeks=week_idx, days=day_idx)
            ds = d.isoformat()
            week.append(CalendarDayOut(
                date=ds,
                day_num=str(d.day),
                is_today=(ds == today_str),
                events=by_date.get(ds, []),
            ))
        weeks.append(week)
    return weeks


def _week_label(start: date) -> str:
    end = start + timedelta(days=41)
    if start.year == end.year:
        return f"{start.strftime('%B')} – {end.strftime('%B %Y')}"
    return f"{start.strftime('%B %Y')} – {end.strftime('%B %Y')}"


@router.get("/calendar/grid")
async def get_calendar_grid(
    week_start: Optional[str] = Query(None, description="ISO date YYYY-MM-DD for the Monday to start from"),
) -> CalendarGridResponse:
    from db.bq_client import query_calendar_events

    ws = _get_week_start(week_start)
    end = ws + timedelta(days=41)

    raw_events = query_calendar_events(
        start_date=ws.isoformat(),
        end_date=end.isoformat(),
    )

    grid = _build_grid(raw_events, ws)
    return CalendarGridResponse(
        grid=grid,
        week_label=_week_label(ws),
        event_count=len(raw_events),
    )


@router.get("/calendar/events")
async def get_calendar_events(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
) -> CalendarEventsResponse:
    from db.bq_client import query_calendar_events

    raw_events = query_calendar_events(
        start_date=start_date,
        end_date=end_date,
    )

    events = [
        CalendarEventOut(
            event_id=ev.get("event_id", ""),
            title=ev.get("title", ""),
            time=ev.get("time", ""),
            color=ev.get("color", "#94A3B8"),
            event_type=ev.get("event_type", "other"),
            date=ev.get("date", ""),
            start_datetime=ev.get("start_datetime", ""),
            end_datetime=ev.get("end_datetime", ""),
            description=ev.get("description"),
        )
        for ev in raw_events
    ]
    return CalendarEventsResponse(events=events, count=len(events))
