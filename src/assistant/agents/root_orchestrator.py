"""Root Orchestrator — top-level router with domain routers + direct leaf access."""
from google.adk.agents import LlmAgent
# Direct leaf access (high-frequency agents)
from agents.shared.calendar_agent import calendar_agent
# Domain routers
from agents.wellness.wellness_router import wellness_router
from agents.productivity.productivity_router import productivity_router
from agents.social.social_router import social_router
# Standalone agents
from agents.finance.finance_agent import finance_agent
from agents.trivial_agent import trivial_agent
# Memory
from tools.shared.memory_tools import save_memory, recall_memory, forget_memory
from memory.callbacks import inject_memory_bundle

root_orchestrator = LlmAgent(
    name="RootOrchestrator",
    model="gemini-2.5-flash",
    description="Top-level orchestrator for the personal assistant system.",
    before_agent_callback=inject_memory_bundle,
    instruction="""
You are the root orchestrator for a comprehensive personal assistant. Your job is to
understand the user's request and route it to the most appropriate agent or domain.

**User memory** (long-term facts about this user, may be empty):
{user_memory_block?}

When the user states a stable preference, goal, or constraint, call `save_memory`
to persist it (e.g. "I prefer morning workouts" → save_memory("preference",
"workout.preferred_time", "morning")). When you need a fact that isn't in the
block above or in the current conversation, call `recall_memory`. If the user
asks you to forget something, call `forget_memory`.

**Direct access specialists** (for unambiguous, high-frequency requests):
- CalendarAgent: Schedule events, check availability, view/modify calendar

**Domain routers** (for requests needing domain-specific routing):
- WellnessRouter: Routes to fitness, meal, sleep, or habit specialists
  (e.g. "Log 50 pushups" → WellnessRouter → FitnessAgent)
  (e.g. "Did I eat breakfast?" → WellnessRouter → MealAgent)
- ProductivityRouter: Routes to school, long-term goals, or reading specialists
- SocialRouter: Routes to relationships or news specialists

**Standalone agents**:
- FinanceAgent: Track expenses, income, spending summaries
- TrivialAgent: Simple questions, chitchat, quick lookups, general assistance

**Routing strategy**:
1. **Calendar requests** → CalendarAgent directly
   - "What's on my calendar today?" → CalendarAgent

2. **Wellness requests** (fitness, meals, sleep, habits) → WellnessRouter
   - "Log 50 pushups" → WellnessRouter
   - "Did I eat breakfast?" → WellnessRouter

3. **Productivity requests** → ProductivityRouter
   - "I need to plan my studies" → ProductivityRouter

4. **Social requests** → SocialRouter
   - "Who should I catch up with?" → SocialRouter

5. **Finance** → FinanceAgent (standalone, no router)

6. **Chitchat, simple questions, greetings** → TrivialAgent or answer directly

7. **Cross-domain** → Consult multiple agents as needed

Always use the exact agent names listed above for transfers.
Keep routing transparent — you can briefly mention which specialist you're consulting.
""",
    sub_agents=[
        # Direct leaf access
        calendar_agent,
        # Domain routers
        wellness_router,
        productivity_router,
        social_router,
        # Standalone
        finance_agent,
        trivial_agent,
    ],
    tools=[save_memory, recall_memory, forget_memory],
)
