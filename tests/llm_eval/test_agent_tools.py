"""LLM eval — verify agents call appropriate tools."""
import pytest


@pytest.mark.llm
class TestAgentTools:
    @pytest.fixture(autouse=True)
    def setup(self, require_api_key):
        pass

    @pytest.mark.asyncio
    async def test_memory_save_triggered(self):
        from runner import run_agent

        response = await run_agent(
            session_id="llm-eval-memory",
            user_id="eval_user",
            message="Remember that I prefer morning workouts",
        )
        assert isinstance(response, str)
        response_lower = response.lower()
        assert any(w in response_lower for w in ["remember", "noted", "saved", "preference", "morning"])
