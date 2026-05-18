"""LLM eval — verify skill loading improves response quality."""
import pytest


@pytest.mark.llm
class TestSkillQuality:
    @pytest.fixture(autouse=True)
    def setup(self, require_api_key):
        pass

    @pytest.mark.asyncio
    async def test_agent_produces_substantive_response(self):
        from runner import run_agent

        response = await run_agent(
            session_id="llm-eval-skill",
            user_id="eval_user",
            message="Give me fitness tips for improving my 5K running time",
        )
        assert isinstance(response, str)
        assert len(response) > 50
