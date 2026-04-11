"""Memory module for cross-domain intelligence and user profiling."""
from memory.user_profile import (
    get_user_preferences,
    update_user_preference,
    get_user_context,
)
from memory.patterns import (
    analyze_weekly_patterns,
    detect_correlations,
    predict_optimal_time,
)
from memory.cross_domain import (
    get_wellness_context,
    get_productivity_context,
    get_integrated_recommendations,
)

__all__ = [
    "get_user_preferences",
    "update_user_preference",
    "get_user_context",
    "analyze_weekly_patterns",
    "detect_correlations",
    "predict_optimal_time",
    "get_wellness_context",
    "get_productivity_context",
    "get_integrated_recommendations",
]
