"""FinanceAgent — tracks expenses, income, and spending patterns."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
from prompts.loader import build_instruction
from tools.finance.finance_tools import (
    add_expense,
    get_spending_summary,
    list_recent_transactions,
)

finance_agent = LlmAgent(
    name="FinanceAgent",
    model="gemini-2.5-flash",
    description=(
        "Tracks personal finances, expenses, and income. "
        "Use for logging transactions, reviewing spending, or setting budget reminders."
    ),
    instruction=build_instruction("finance/finance.md", "finance/finance.md"),
    tools=[
        add_expense,
        get_spending_summary,
        list_recent_transactions,
        AgentTool(agent=calendar_agent),
    ],
    output_key="finance_response",
)
