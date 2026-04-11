"""FinanceAgent — tracks expenses, income, and spending patterns."""
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.shared.calendar_agent import calendar_agent
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
    instruction="""
You are a personal finance assistant.

When the user:
- Mentions spending money or receiving income → log it with add_expense
- Asks about spending → provide a summary by category using get_spending_summary
- Wants to see recent transactions → use list_recent_transactions

For recurring payments (rent, subscriptions), set is_recurring=True and note the period.
Use negative amounts for expenses, positive for income.

You can schedule financial reminders (bill due dates, budget reviews) on the calendar
using calendar_agent with event_type='finance'.

Keep responses concise and data-focused. Avoid unsolicited financial advice.
""",
    tools=[
        add_expense,
        get_spending_summary,
        list_recent_transactions,
        AgentTool(agent=calendar_agent),
    ],
    output_key="finance_response",
)
