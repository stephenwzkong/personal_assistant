"""Integration tests — verify agent hierarchy and SkillToolset wiring."""
import pytest
from google.adk.tools.skill_toolset import SkillToolset


class TestRootOrchestrator:
    def test_root_has_6_sub_agents(self):
        from agents.root_orchestrator import root_orchestrator

        assert len(root_orchestrator.sub_agents) == 6
        names = {a.name for a in root_orchestrator.sub_agents}
        assert names == {
            "CalendarAgent",
            "WellnessRouter",
            "ProductivityRouter",
            "SocialRouter",
            "FinanceAgent",
            "TrivialAgent",
        }

    def test_root_has_memory_tools(self):
        from agents.root_orchestrator import root_orchestrator

        tool_names = [getattr(t, "__name__", getattr(t, "name", str(t))) for t in root_orchestrator.tools]
        assert "save_memory" in tool_names
        assert "recall_memory" in tool_names
        assert "forget_memory" in tool_names

    def test_root_has_before_agent_callback(self):
        from agents.root_orchestrator import root_orchestrator
        from memory.callbacks import inject_memory_bundle

        assert root_orchestrator.before_agent_callback == inject_memory_bundle


class TestDomainRouters:
    def test_wellness_router_has_4_specialists(self):
        from agents.wellness.wellness_router import wellness_router

        assert len(wellness_router.sub_agents) == 4
        names = {a.name for a in wellness_router.sub_agents}
        assert "FitnessAgent" in names
        assert "MealAgent" in names
        assert "SleepAgent" in names
        assert "HabitAgent" in names

    def test_productivity_router_has_4_specialists(self):
        from agents.productivity.productivity_router import productivity_router

        assert len(productivity_router.sub_agents) == 4
        names = {a.name for a in productivity_router.sub_agents}
        assert "TaskAgent" in names
        assert "SchoolAgent" in names

    def test_social_router_has_2_specialists(self):
        from agents.social.social_router import social_router

        assert len(social_router.sub_agents) == 2


class TestSkillToolsetWiring:
    def test_all_specialists_have_skill_toolset(self):
        from agents.wellness.wellness_router import wellness_router
        from agents.productivity.productivity_router import productivity_router
        from agents.social.social_router import social_router
        from agents.finance.finance_agent import finance_agent
        from agents.trivial_agent import trivial_agent

        all_specialists = (
            list(wellness_router.sub_agents)
            + list(productivity_router.sub_agents)
            + list(social_router.sub_agents)
            + [finance_agent, trivial_agent]
        )

        for agent in all_specialists:
            has_skillset = any(isinstance(t, SkillToolset) for t in agent.tools)
            assert has_skillset, f"{agent.name} has no SkillToolset"
