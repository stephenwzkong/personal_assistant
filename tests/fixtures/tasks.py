def make_task(overrides=None):
    base = {
        "task_id": "task-test-001",
        "parent_task_id": None,
        "title": "Buy groceries",
        "description": "",
        "status": "todo",
        "priority": "medium",
        "category": "personal",
        "due_date": "2026-05-20",
        "position": 0,
        "created_at": "2026-05-17T00:00:00+00:00",
        "updated_at": "2026-05-17T00:00:00+00:00",
    }
    if overrides:
        base.update(overrides)
    return base


def make_task_with_steps():
    parent = make_task({"title": "Prepare for exam", "category": "school"})
    steps = [
        make_task({
            "task_id": f"step-{i}",
            "parent_task_id": parent["task_id"],
            "title": t,
            "position": i,
        })
        for i, t in enumerate(["Review notes", "Practice problems", "Make flashcards"])
    ]
    return parent, steps
