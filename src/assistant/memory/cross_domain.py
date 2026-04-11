"""Cross-domain intelligence — integrates insights across life areas."""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


def get_wellness_context(user_id: str = "default_user") -> Dict[str, Any]:
    """Get comprehensive wellness context for smart recommendations.

    Aggregates data from fitness, meals, sleep, and habits to provide holistic view.

    Returns:
        Dictionary with wellness context:
        {
            'recent_workout_load': 'moderate',  # 'light', 'moderate', 'heavy'
            'eating_consistency': 0.85,  # 0-1 score for IF adherence
            'sleep_debt': -2.5,  # hours (negative = deficit)
            'habit_streak_count': 14,
            'wellness_score': 72,  # 0-100 composite score
            'recommendations': ['Consider lighter workout today due to sleep debt'],
        }
    """
    from google.cloud import bigquery

    PROJECT_ID = "gen-lang-client-0288149151"
    DATASET = "personal_assistant"

    try:
        client = bigquery.Client(project=PROJECT_ID)

        # 1. Calculate recent workout load (last 7 days)
        workout_query = f"""
            SELECT
                COUNT(*) as workout_count,
                SUM(calories_burned) as total_calories,
                AVG(duration_hours + duration_minutes/60.0) as avg_duration
            FROM `{PROJECT_ID}.{DATASET}.fitness_tracker`
            WHERE workout_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        """
        workout_df = client.query(workout_query).to_dataframe()
        workout_count = int(workout_df['workout_count'].iloc[0]) if not workout_df.empty else 0
        total_calories = int(workout_df['total_calories'].iloc[0]) if not workout_df.empty and workout_df['total_calories'].iloc[0] else 0

        # Classify workout load
        if workout_count == 0:
            workout_load = "none"
        elif workout_count <= 2:
            workout_load = "light"
        elif workout_count <= 4:
            workout_load = "moderate"
        else:
            workout_load = "heavy"

        # 2. Calculate eating consistency (IF adherence - meals within 8-hour windows)
        meal_query = f"""
            SELECT
                DATE(current_time) as meal_date,
                MIN(current_time) as first_meal,
                MAX(current_time) as last_meal,
                COUNT(*) as meal_count
            FROM `{PROJECT_ID}.{DATASET}.meal_hour`
            WHERE current_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
            GROUP BY DATE(current_time)
        """
        meal_df = client.query(meal_query).to_dataframe()

        if not meal_df.empty:
            # Calculate hours between first and last meal for each day
            meal_df['eating_window_hours'] = (
                (meal_df['last_meal'] - meal_df['first_meal']).dt.total_seconds() / 3600
            )
            # Count days where eating window <= 8 hours
            compliant_days = (meal_df['eating_window_hours'] <= 8).sum()
            eating_consistency = compliant_days / len(meal_df) if len(meal_df) > 0 else 0.0
        else:
            eating_consistency = 0.0

        # 3. Get active habit streaks
        habit_query = f"""
            WITH recent_logs AS (
                SELECT
                    h.habit_id,
                    h.name,
                    h.frequency,
                    DATE(hl.logged_date) as log_date,
                    ROW_NUMBER() OVER (PARTITION BY h.habit_id ORDER BY hl.logged_date DESC) as day_rank
                FROM `{PROJECT_ID}.{DATASET}.habits` h
                LEFT JOIN `{PROJECT_ID}.{DATASET}.habit_logs` hl ON h.habit_id = hl.habit_id
                WHERE h.active = TRUE
                  AND hl.logged_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
            )
            SELECT
                habit_id,
                name,
                COUNT(DISTINCT log_date) as streak_days
            FROM recent_logs
            WHERE day_rank <= 30
            GROUP BY habit_id, name
            ORDER BY streak_days DESC
            LIMIT 1
        """
        habit_df = client.query(habit_query).to_dataframe()
        habit_streak_count = int(habit_df['streak_days'].iloc[0]) if not habit_df.empty else 0

        # 4. Calculate composite wellness score (0-100)
        # Weighted components:
        # - Workout consistency: 30 points (7 workouts/week = 30)
        # - Eating consistency: 30 points (IF adherence)
        # - Habit streak: 20 points (30-day streak = 20)
        # - Activity: 20 points (total calories burned / 2500 * 20)

        workout_score = min(30, (workout_count / 7) * 30)
        eating_score = eating_consistency * 30
        habit_score = min(20, (habit_streak_count / 30) * 20)
        activity_score = min(20, (total_calories / 2500) * 20) if total_calories > 0 else 0

        wellness_score = int(workout_score + eating_score + habit_score + activity_score)

        # 5. Generate recommendations
        recommendations = []
        if workout_count == 0:
            recommendations.append("No workouts logged this week - consider scheduling exercise")
        elif workout_count >= 6:
            recommendations.append("High workout frequency detected - ensure adequate recovery")

        if eating_consistency < 0.5:
            recommendations.append(f"Eating window adherence is {eating_consistency:.0%} - aim for 8-hour windows")
        elif eating_consistency >= 0.85:
            recommendations.append(f"Excellent IF adherence at {eating_consistency:.0%}")

        if habit_streak_count >= 14:
            recommendations.append(f"Great habit momentum - {habit_streak_count} day streak!")
        elif habit_streak_count == 0:
            recommendations.append("No active habit streaks - consider starting a new habit")

        return {
            "recent_workout_load": workout_load,
            "eating_consistency": round(eating_consistency, 2),
            "sleep_debt": 0.0,  # TODO: Implement once sleep tracking is added
            "habit_streak_count": habit_streak_count,
            "wellness_score": wellness_score,
            "recommendations": recommendations,
        }

    except Exception as e:
        # Return safe defaults on error
        return {
            "recent_workout_load": "unknown",
            "eating_consistency": 0.0,
            "sleep_debt": 0.0,
            "habit_streak_count": 0,
            "wellness_score": 0,
            "recommendations": [f"Error fetching wellness context: {str(e)}"],
        }


def get_productivity_context(user_id: str = "default_user") -> Dict[str, Any]:
    """Get comprehensive productivity context for smart scheduling.

    Aggregates data from school, reading, and long-term goals.

    Returns:
        Dictionary with productivity context:
        {
            'upcoming_deadlines': [
                {'type': 'assignment', 'title': 'CS midterm', 'days_until': 3},
            ],
            'workload_level': 'high',  # 'low', 'moderate', 'high'
            'reading_progress': 0.42,  # 0-1, current book completion
            'active_goal_count': 3,
            'focus_capacity': 'reduced',  # based on wellness data
            'recommendations': ['Block focus time for CS midterm prep'],
        }
    """
    from google.cloud import bigquery

    PROJECT_ID = "gen-lang-client-0288149151"
    DATASET = "personal_assistant"

    try:
        client = bigquery.Client(project=PROJECT_ID)

        # 1. Get upcoming deadlines (next 14 days)
        deadline_query = f"""
            SELECT
                'assignment' as type,
                title,
                due_date,
                priority,
                DATE_DIFF(DATE(due_date), CURRENT_DATE(), DAY) as days_until
            FROM `{PROJECT_ID}.{DATASET}.school_assignments`
            WHERE status IN ('pending', 'in_progress')
              AND due_date >= CURRENT_TIMESTAMP()
              AND due_date <= TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 14 DAY)
            ORDER BY due_date ASC
            LIMIT 10
        """
        deadline_df = client.query(deadline_query).to_dataframe()
        upcoming_deadlines = []
        if not deadline_df.empty:
            for _, row in deadline_df.iterrows():
                upcoming_deadlines.append({
                    "type": row["type"],
                    "title": row["title"],
                    "days_until": int(row["days_until"]),
                    "priority": row["priority"] if "priority" in row else "medium",
                })

        # 2. Calculate workload level (count pending + in_progress assignments)
        workload_query = f"""
            SELECT
                COUNT(*) as pending_count,
                COUNTIF(priority = 'high') as high_priority_count
            FROM `{PROJECT_ID}.{DATASET}.school_assignments`
            WHERE status IN ('pending', 'in_progress')
              AND due_date >= CURRENT_TIMESTAMP()
        """
        workload_df = client.query(workload_query).to_dataframe()
        pending_count = int(workload_df['pending_count'].iloc[0]) if not workload_df.empty else 0
        high_priority_count = int(workload_df['high_priority_count'].iloc[0]) if not workload_df.empty else 0

        if pending_count == 0:
            workload_level = "low"
        elif pending_count <= 3 and high_priority_count == 0:
            workload_level = "moderate"
        else:
            workload_level = "high"

        # 3. Get current reading progress
        reading_query = f"""
            SELECT
                current_page,
                total_pages
            FROM `{PROJECT_ID}.{DATASET}.reading_list`
            WHERE status = 'reading'
            ORDER BY current_page DESC
            LIMIT 1
        """
        reading_df = client.query(reading_query).to_dataframe()
        if not reading_df.empty and reading_df['total_pages'].iloc[0] > 0:
            reading_progress = reading_df['current_page'].iloc[0] / reading_df['total_pages'].iloc[0]
        else:
            reading_progress = 0.0

        # 4. Count active long-term goals
        goals_query = f"""
            SELECT COUNT(*) as active_goal_count
            FROM `{PROJECT_ID}.{DATASET}.long_term_goals`
            WHERE status IN ('active', 'in_progress')
        """
        goals_df = client.query(goals_query).to_dataframe()
        active_goal_count = int(goals_df['active_goal_count'].iloc[0]) if not goals_df.empty else 0

        # 5. Determine focus capacity based on wellness data
        wellness = get_wellness_context(user_id)
        if wellness["wellness_score"] < 40:
            focus_capacity = "reduced"
        elif wellness["wellness_score"] >= 70:
            focus_capacity = "high"
        else:
            focus_capacity = "normal"

        # 6. Generate recommendations
        recommendations = []
        for deadline in upcoming_deadlines:
            if deadline["days_until"] <= 2:
                recommendations.append(
                    f"URGENT: {deadline['title']} due in {deadline['days_until']} days - prioritize today"
                )
            elif deadline["days_until"] <= 5:
                recommendations.append(
                    f"Block focus time for {deadline['title']} (due in {deadline['days_until']} days)"
                )

        if workload_level == "high" and focus_capacity == "reduced":
            recommendations.append(
                "High workload + reduced focus capacity - consider rescheduling non-urgent tasks"
            )

        if reading_progress > 0 and reading_progress < 1.0:
            recommendations.append(
                f"Current book is {reading_progress:.0%} complete - schedule reading time this week"
            )

        if active_goal_count > 5:
            recommendations.append(
                f"{active_goal_count} active goals - consider focusing on fewer priorities"
            )

        return {
            "upcoming_deadlines": upcoming_deadlines,
            "workload_level": workload_level,
            "reading_progress": round(reading_progress, 2),
            "active_goal_count": active_goal_count,
            "focus_capacity": focus_capacity,
            "recommendations": recommendations,
        }

    except Exception as e:
        return {
            "upcoming_deadlines": [],
            "workload_level": "unknown",
            "reading_progress": 0.0,
            "active_goal_count": 0,
            "focus_capacity": "normal",
            "recommendations": [f"Error fetching productivity context: {str(e)}"],
        }


def get_integrated_recommendations(
    user_id: str = "default_user",
    context: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Generate integrated recommendations across all life domains.

    Args:
        user_id: User identifier.
        context: Optional context for recommendations (e.g., 'plan_week', 'optimize_schedule').

    Returns:
        List of recommendation dicts with priority, category, and action:
        [
            {
                'priority': 'high',
                'category': 'wellness',
                'action': 'Schedule recovery day - high workout load + sleep debt',
                'affected_domains': ['fitness', 'sleep'],
            },
            {
                'priority': 'medium',
                'category': 'productivity',
                'action': 'Block 3-hour study session for CS midterm (due in 3 days)',
                'affected_domains': ['school', 'calendar'],
            },
        ]
    """
    wellness = get_wellness_context(user_id)
    productivity = get_productivity_context(user_id)

    recommendations = []

    # 1. HIGH PRIORITY: Urgent deadlines always come first
    for deadline in productivity["upcoming_deadlines"]:
        if deadline["days_until"] <= 2:
            recommendations.append({
                "priority": "high",
                "category": "productivity",
                "action": f"URGENT: Complete {deadline['title']} (due in {deadline['days_until']} days)",
                "affected_domains": ["school", "calendar"],
            })

    # 2. HIGH PRIORITY: Wellness alerts (overtraining or inactivity)
    if wellness["recent_workout_load"] == "heavy" and wellness["wellness_score"] < 60:
        recommendations.append({
            "priority": "high",
            "category": "wellness",
            "action": "Schedule rest day - high workout load with low wellness score indicates overtraining",
            "affected_domains": ["fitness", "recovery"],
        })

    if wellness["recent_workout_load"] == "none":
        recommendations.append({
            "priority": "high",
            "category": "wellness",
            "action": "No workouts this week - schedule at least 2-3 sessions",
            "affected_domains": ["fitness", "calendar"],
        })

    # 3. MEDIUM PRIORITY: Cross-domain workload/capacity conflicts
    if productivity["workload_level"] == "high" and productivity["focus_capacity"] == "reduced":
        recommendations.append({
            "priority": "medium",
            "category": "cross-domain",
            "action": f"High workload with reduced focus capacity (wellness score: {wellness['wellness_score']}) - prioritize sleep and recovery",
            "affected_domains": ["wellness", "productivity", "sleep"],
        })

    # 4. MEDIUM PRIORITY: Upcoming deadlines (3-7 days out)
    for deadline in productivity["upcoming_deadlines"]:
        if 3 <= deadline["days_until"] <= 7:
            recommendations.append({
                "priority": "medium",
                "category": "productivity",
                "action": f"Schedule study blocks for {deadline['title']} (due in {deadline['days_until']} days)",
                "affected_domains": ["school", "calendar"],
            })

    # 5. MEDIUM PRIORITY: Eating consistency
    if wellness["eating_consistency"] < 0.6:
        recommendations.append({
            "priority": "medium",
            "category": "wellness",
            "action": f"Eating window adherence at {wellness['eating_consistency']:.0%} - aim for consistent 8-hour windows",
            "affected_domains": ["nutrition", "habits"],
        })

    # 6. LOW PRIORITY: Habit streaks and goals
    if wellness["habit_streak_count"] >= 14:
        recommendations.append({
            "priority": "low",
            "category": "wellness",
            "action": f"Maintain {wellness['habit_streak_count']}-day habit streak - great momentum!",
            "affected_domains": ["habits"],
        })

    if productivity["reading_progress"] > 0.7:
        recommendations.append({
            "priority": "low",
            "category": "productivity",
            "action": f"Current book is {productivity['reading_progress']:.0%} complete - finish this week",
            "affected_domains": ["reading"],
        })

    # 7. Context-specific recommendations
    if context == "plan_week":
        # Add weekly planning recommendations
        if wellness["wellness_score"] >= 70 and productivity["workload_level"] in ["low", "moderate"]:
            recommendations.append({
                "priority": "low",
                "category": "cross-domain",
                "action": "High wellness + manageable workload - good week to start a new goal or habit",
                "affected_domains": ["habits", "goals"],
            })

    # Sort by priority: high → medium → low
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

    return recommendations


def detect_stress_indicators(user_id: str = "default_user") -> Dict[str, Any]:
    """Detect potential stress indicators from behavioral patterns.

    Looks for:
    - Sleep disruption
    - Skipped workouts/habits
    - Irregular eating patterns
    - High deadline density
    - Low social activity

    Returns:
        Dictionary with stress assessment:
        {
            'stress_level': 'moderate',  # 'low', 'moderate', 'high'
            'indicators': [
                'Sleep duration down 15% this week',
                '3 assignments due within 5 days',
            ],
            'recommendations': [
                'Consider scheduling buffer time for assignments',
                'Prioritize sleep consistency this week',
            ],
        }
    """
    from google.cloud import bigquery

    PROJECT_ID = "gen-lang-client-0288149151"
    DATASET = "personal_assistant"

    wellness = get_wellness_context(user_id)
    productivity = get_productivity_context(user_id)

    indicators = []
    stress_score = 0  # 0-100, higher = more stress

    try:
        client = bigquery.Client(project=PROJECT_ID)

        # 1. Check for workout disruption (comparing last 7 days to previous 7-14 days)
        workout_trend_query = f"""
            SELECT
                COUNTIF(workout_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)) as recent_workouts,
                COUNTIF(
                    workout_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 14 DAY)
                    AND workout_timestamp < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
                ) as previous_workouts
            FROM `{PROJECT_ID}.{DATASET}.fitness_tracker`
            WHERE workout_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 14 DAY)
        """
        workout_trend_df = client.query(workout_trend_query).to_dataframe()
        if not workout_trend_df.empty:
            recent = int(workout_trend_df['recent_workouts'].iloc[0])
            previous = int(workout_trend_df['previous_workouts'].iloc[0])
            if previous > 0 and recent < previous * 0.5:
                indicators.append(f"Workout frequency down {int((1 - recent/previous) * 100)}% this week")
                stress_score += 15

        # 2. Check eating pattern irregularity (high variance in meal times)
        meal_variance_query = f"""
            SELECT
                STDDEV(EXTRACT(HOUR FROM current_time)) as meal_time_variance,
                COUNT(*) as meal_count
            FROM `{PROJECT_ID}.{DATASET}.meal_hour`
            WHERE current_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        """
        meal_variance_df = client.query(meal_variance_query).to_dataframe()
        if not meal_variance_df.empty and meal_variance_df['meal_count'].iloc[0] >= 3:
            variance = meal_variance_df['meal_time_variance'].iloc[0]
            if variance and variance > 3.0:  # More than 3 hours std dev
                indicators.append(f"Irregular meal timing detected (variance: {variance:.1f} hours)")
                stress_score += 10

        # 3. Check habit compliance (active habits with no recent logs)
        habit_compliance_query = f"""
            SELECT
                COUNT(DISTINCT h.habit_id) as total_active_habits,
                COUNT(DISTINCT hl.habit_id) as logged_habits
            FROM `{PROJECT_ID}.{DATASET}.habits` h
            LEFT JOIN `{PROJECT_ID}.{DATASET}.habit_logs` hl
                ON h.habit_id = hl.habit_id
                AND hl.logged_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)
            WHERE h.active = TRUE
        """
        habit_df = client.query(habit_compliance_query).to_dataframe()
        if not habit_df.empty:
            total = int(habit_df['total_active_habits'].iloc[0])
            logged = int(habit_df['logged_habits'].iloc[0]) if habit_df['logged_habits'].iloc[0] else 0
            if total > 0 and logged < total * 0.5:
                indicators.append(f"Habit compliance low: {logged}/{total} habits logged in last 3 days")
                stress_score += 15

        # 4. Check deadline density (multiple deadlines in short window)
        urgent_deadlines = [d for d in productivity["upcoming_deadlines"] if d["days_until"] <= 5]
        if len(urgent_deadlines) >= 3:
            indicators.append(f"{len(urgent_deadlines)} deadlines within 5 days")
            stress_score += 20 + (len(urgent_deadlines) - 3) * 5  # Extra 5 points per deadline over 3

        # 5. Check social activity (contacts not contacted recently)
        social_query = f"""
            SELECT
                COUNT(*) as overdue_contacts
            FROM `{PROJECT_ID}.{DATASET}.social_contacts`
            WHERE next_reminder < CURRENT_DATE()
              AND next_reminder IS NOT NULL
        """
        social_df = client.query(social_query).to_dataframe()
        if not social_df.empty:
            overdue = int(social_df['overdue_contacts'].iloc[0])
            if overdue >= 3:
                indicators.append(f"{overdue} social contacts overdue for check-in")
                stress_score += 10

    except Exception as e:
        indicators.append(f"Error analyzing patterns: {str(e)}")

    # 6. Factor in wellness score
    if wellness["wellness_score"] < 50:
        indicators.append(f"Low overall wellness score ({wellness['wellness_score']}/100)")
        stress_score += 15

    # 7. Factor in workload + focus capacity mismatch
    if productivity["workload_level"] == "high" and productivity["focus_capacity"] == "reduced":
        indicators.append("High workload with reduced focus capacity")
        stress_score += 20

    # Determine stress level
    if stress_score >= 60:
        stress_level = "high"
    elif stress_score >= 30:
        stress_level = "moderate"
    else:
        stress_level = "low"

    # Generate recommendations
    recommendations = []
    if stress_level in ["high", "moderate"]:
        recommendations.append("Consider scheduling downtime or buffer days this week")

        if wellness["wellness_score"] < 50:
            recommendations.append("Prioritize sleep, nutrition, and light movement")

        if len(urgent_deadlines) >= 3:
            recommendations.append("High deadline density - delegate or defer non-critical tasks if possible")

        if wellness["recent_workout_load"] in ["none", "light"]:
            recommendations.append("Light exercise can reduce stress - schedule short walks or yoga")

    return {
        "stress_level": stress_level,
        "indicators": indicators,
        "recommendations": recommendations,
    }


def get_energy_forecast(
    user_id: str = "default_user",
    date: Optional[str] = None,
) -> Dict[str, Any]:
    """Forecast energy levels for a given day based on patterns.

    Args:
        user_id: User identifier.
        date: Target date YYYY-MM-DD (defaults to tomorrow).

    Returns:
        Dictionary with hourly energy forecast:
        {
            'date': '2025-03-10',
            'hourly_forecast': {
                '06:00': 0.7,  # 0-1 energy score
                '09:00': 0.9,
                '12:00': 0.75,
                '15:00': 0.6,
                '18:00': 0.8,
                '21:00': 0.4,
            },
            'peak_hours': ['09:00', '18:00'],
            'low_energy_hours': ['15:00', '21:00'],
        }
    """
    from google.cloud import bigquery

    PROJECT_ID = "gen-lang-client-0288149151"
    DATASET = "personal_assistant"

    target_date = date or (datetime.utcnow() + timedelta(days=1)).date().isoformat()
    wellness = get_wellness_context(user_id)

    # Base energy curve (typical circadian rhythm)
    # Time: 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22
    base_curve = {
        "06:00": 0.5, "07:00": 0.6, "08:00": 0.7, "09:00": 0.85,
        "10:00": 0.9, "11:00": 0.85, "12:00": 0.75, "13:00": 0.7,
        "14:00": 0.65, "15:00": 0.6, "16:00": 0.65, "17:00": 0.7,
        "18:00": 0.75, "19:00": 0.7, "20:00": 0.6, "21:00": 0.5, "22:00": 0.4,
    }

    try:
        client = bigquery.Client(project=PROJECT_ID)

        # 1. Adjust for recent workout recovery (lower energy if heavy workout yesterday)
        recent_workout_query = f"""
            SELECT
                EXTRACT(HOUR FROM workout_timestamp) as workout_hour,
                calories_burned
            FROM `{PROJECT_ID}.{DATASET}.fitness_tracker`
            WHERE DATE(workout_timestamp) = DATE_SUB(DATE('{target_date}'), INTERVAL 1 DAY)
            ORDER BY workout_timestamp DESC
            LIMIT 1
        """
        workout_df = client.query(recent_workout_query).to_dataframe()

        recovery_penalty = 0.0
        if not workout_df.empty:
            calories = workout_df['calories_burned'].iloc[0]
            if calories > 400:  # High-intensity workout
                recovery_penalty = 0.15
            elif calories > 250:  # Moderate workout
                recovery_penalty = 0.05

        # 2. Adjust for meal timing patterns (energy dip if irregular eating)
        meal_timing_query = f"""
            SELECT
                AVG(EXTRACT(HOUR FROM current_time)) as avg_first_meal_hour,
                STDDEV(EXTRACT(HOUR FROM current_time)) as meal_variance
            FROM (
                SELECT
                    DATE(current_time) as meal_date,
                    MIN(current_time) as current_time
                FROM `{PROJECT_ID}.{DATASET}.meal_hour`
                WHERE current_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
                GROUP BY DATE(current_time)
            )
        """
        meal_df = client.query(meal_timing_query).to_dataframe()

        meal_adjustment = 0.0
        if not meal_df.empty and meal_df['meal_variance'].iloc[0]:
            variance = meal_df['meal_variance'].iloc[0]
            if variance > 2.0:  # Irregular meal timing
                meal_adjustment = -0.1

    except Exception:
        recovery_penalty = 0.0
        meal_adjustment = 0.0

    # 3. Adjust based on overall wellness score
    wellness_multiplier = 1.0
    if wellness["wellness_score"] >= 70:
        wellness_multiplier = 1.1  # 10% boost
    elif wellness["wellness_score"] < 50:
        wellness_multiplier = 0.85  # 15% reduction

    # 4. Apply adjustments to base curve
    hourly_forecast = {}
    for hour, base_energy in base_curve.items():
        adjusted_energy = base_energy * wellness_multiplier - recovery_penalty + meal_adjustment
        # Clamp to 0-1 range
        hourly_forecast[hour] = max(0.1, min(1.0, adjusted_energy))

    # 5. Identify peak and low energy hours
    sorted_hours = sorted(hourly_forecast.items(), key=lambda x: x[1], reverse=True)
    peak_hours = [hour for hour, energy in sorted_hours[:3]]  # Top 3 hours
    low_energy_hours = [hour for hour, energy in sorted_hours[-3:]]  # Bottom 3 hours

    return {
        "date": target_date,
        "hourly_forecast": {k: round(v, 2) for k, v in hourly_forecast.items()},
        "peak_hours": peak_hours,
        "low_energy_hours": low_energy_hours,
    }