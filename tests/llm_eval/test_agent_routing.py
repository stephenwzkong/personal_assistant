"""LLM eval — verify agent routing with live Gemini calls."""
import pytest


@pytest.mark.llm
class TestAgentRouting:
    @pytest.fixture(autouse=True)
    def setup(self, require_api_key):
        pass

    @pytest.mark.asyncio
    async def test_fitness_query_routes(self):
        from runner import run_agent

        response = await run_agent(
            session_id="llm-eval-fitness",
            user_id="eval_user",
            message="What workouts did I do this week?",
        )
        assert isinstance(response, str)
        assert len(response) > 10

    @pytest.mark.asyncio
    async def test_calendar_query_routes(self):
        from runner import run_agent

        response = await run_agent(
            session_id="llm-eval-calendar",
            user_id="eval_user",
            message="What's on my calendar today?",
        )
        assert isinstance(response, str)
        assert len(response) > 10

    @pytest.mark.asyncio
    async def test_trivial_query_routes(self):
        from runner import run_agent

        response = await run_agent(
            session_id="llm-eval-trivial",
            user_id="eval_user",
            message="Hello, how are you?",
        )
        assert isinstance(response, str)
        assert len(response) > 5
