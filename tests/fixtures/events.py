def make_event(overrides=None):
    base = {
        "event_id": "evt-test-001",
        "title": "Morning Run",
        "start_datetime": "2026-05-17T07:00:00",
        "end_datetime": "2026-05-17T08:00:00",
        "event_type": "workout",
        "status": "active",
        "priority": "medium",
        "description": "",
        "source_agent": "FitnessAgent",
    }
    if overrides:
        base.update(overrides)
    return base


def make_events_list(count=3):
    types = ["workout", "meal_window", "school"]
    return [
        make_event({
            "event_id": f"evt-test-{i:03d}",
            "title": f"Event {i}",
            "event_type": types[i % len(types)],
            "start_datetime": f"2026-05-1{7 + i}T09:00:00",
            "end_datetime": f"2026-05-1{7 + i}T10:00:00",
        })
        for i in range(count)
    ]
