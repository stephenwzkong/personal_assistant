def make_fact(overrides=None):
    base = {
        "fact_id": "fact-test-001",
        "user_id": "test_user_001",
        "category": "preference",
        "subject": "workout_time",
        "predicate": "prefers",
        "value": "morning",
        "confidence": 0.9,
        "source_agent": "FitnessAgent",
    }
    if overrides:
        base.update(overrides)
    return base


def make_facts_list(count=5):
    categories = ["preference", "goal", "constraint", "profile", "routine"]
    return [
        make_fact({
            "fact_id": f"fact-test-{i:03d}",
            "category": categories[i % len(categories)],
            "subject": f"subject_{i}",
            "value": f"value_{i}",
        })
        for i in range(count)
    ]
