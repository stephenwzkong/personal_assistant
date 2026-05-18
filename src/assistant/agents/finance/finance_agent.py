"""FinanceAgent — tracks expenses, income, and spending patterns."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from skills.loader import load_skill_toolset
from tools.finance.finance_tools import (
    add_expense,
    get_spending_summary,
    list_recent_transactions,
)

finance_toolset = load_skill_toolset("finance", additional_tools=[
    add_expense,
    get_spending_summary,
    list_recent_transactions,
    AgentTool(agent=calendar_agent),
])

finance_agent = LlmAgent(
    name="FinanceAgent",
    model="gemini-2.5-flash",
    description=(
        "Tracks personal finances, expenses, and income. "
        "Use for logging transactions, reviewing spending, or setting budget reminders."
    ),
    tools=[finance_toolset],
    output_key="finance_response",
)
