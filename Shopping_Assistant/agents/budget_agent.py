"""
agents/budget_agent.py
Filters recommendations to fit budget and suggests alternatives.
"""

import json
from langchain_core.messages import HumanMessage, SystemMessage
from .llm import get_llm, rate_limited_call
from .schemas import (
    QueryUnderstanding, ComparisonResult,
    BudgetOptimizationResult, BudgetItem
)

SYSTEM_PROMPT = """You are a budget optimization assistant for Indian shoppers.
Given products and budget, decide which fit and suggest cheaper alternatives.
Respond ONLY with valid JSON (no markdown):
{
  "budget": 30000,
  "items": [
    {"name": "Product", "price": 25000, "within_budget": true, "note": ""}
  ],
  "recommended": ["list of names within budget"],
  "alternatives": [
    {"name": "Budget Alternative", "price": 18000}
  ]
}"""


def run_budget_agent(
    query_info: QueryUnderstanding,
    comparison_result: ComparisonResult,
) -> BudgetOptimizationResult:

    payload = {
        "budget": query_info.budget,
        "products": [
            {"name": c.name, "price": c.price, "value_score": c.value_score}
            for c in comparison_result.comparisons
        ],
    }

    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(payload)),
    ]
    response = rate_limited_call(llm.invoke, messages)
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    data = json.loads(raw)
    items = [BudgetItem(**i) for i in data.get("items", [])]
    return BudgetOptimizationResult(
        budget=data.get("budget", query_info.budget),
        items=items,
        recommended=data.get("recommended", []),
        alternatives=data.get("alternatives", []),
    )
