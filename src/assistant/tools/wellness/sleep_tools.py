"""Tools for sleep recommendations and tracking."""
from datetime import datetime, date
from typing import Optional


def recommend_sleep_schedule(
    wake_time: str,
    sleep_duration_hours: float = 8.0,
    workout_tomorrow: bool = False,
    school_load: str = "normal",
) -> dict:
    """Recommend a sleep schedule based on wake time and activity load.

    Args:
        wake_time: Target wake time in HH:MM format (e.g. '07:00').
        sleep_duration_hours: Desired sleep duration (default 8.0).
        workout_tomorrow: Whether there's a workout planned tomorrow.
        school_load: 'light', 'normal', or 'heavy' based on school workload.

    Returns:
        dict with recommended bedtime and sleep window.
    """
    try:
        from datetime import timedelta
        # Adjust for load
        if school_load == "heavy":
            sleep_duration_hours = max(sleep_duration_hours, 8.5)
        if workout_tomorrow:
            sleep_duration_hours = max(sleep_duration_hours, 8.0)

        # Parse wake time
        hour, minute = map(int, wake_time.split(":"))
        today = date.today()
        wake_dt = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))

        # Calculate bedtime
        sleep_duration = timedelta(hours=sleep_duration_hours)
        wind_down_buffer = timedelta(minutes=30)
        bedtime = wake_dt - sleep_duration
        wind_down_start = bedtime - wind_down_buffer

        return {
            "status": "success",
            "wake_time": wake_time,
            "recommended_bedtime": bedtime.strftime("%H:%M"),
            "wind_down_start": wind_down_start.strftime("%H:%M"),
            "sleep_duration_hours": sleep_duration_hours,
            "notes": f"School load: {school_load}. Workout tomorrow: {workout_tomorrow}.",
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_sleep_tips(issue: str) -> dict:
    """Get sleep improvement tips for a specific issue.

    Args:
        issue: Sleep issue description (e.g. 'trouble falling asleep', 'waking up tired',
               'oversleeping', 'irregular schedule').

    Returns:
        dict with tips.
    """
    tips_db = {
        "trouble falling asleep": [
            "Avoid screens 1 hour before bed.",
            "Keep the room cool (65-68°F / 18-20°C).",
            "Try 4-7-8 breathing: inhale 4s, hold 7s, exhale 8s.",
            "Avoid caffeine after 2pm.",
        ],
        "waking up tired": [
            "Check if you're completing full 90-minute sleep cycles.",
            "Ensure your sleep environment is dark and quiet.",
            "Consider a consistent wake time even on weekends.",
            "Get morning sunlight within 30 minutes of waking.",
        ],
        "oversleeping": [
            "Set an alarm and get up immediately — no snoozing.",
            "Plan something engaging for the morning.",
            "Ensure you're not sleep-deprived earlier in the week.",
        ],
        "irregular schedule": [
            "Anchor your wake time — keep it consistent 7 days a week.",
            "Use light exposure to reset your circadian rhythm.",
            "Gradually shift bedtime by 15 minutes at a time.",
        ],
    }
    # Fuzzy match
    issue_lower = issue.lower()
    matched_tips = []
    for key, tips in tips_db.items():
        if any(word in issue_lower for word in key.split()):
            matched_tips.extend(tips)

    if not matched_tips:
        matched_tips = [
            "Maintain a consistent sleep schedule.",
            "Create a relaxing pre-sleep routine.",
            "Ensure your environment is optimized for sleep.",
        ]

    return {"status": "success", "issue": issue, "tips": matched_tips}
