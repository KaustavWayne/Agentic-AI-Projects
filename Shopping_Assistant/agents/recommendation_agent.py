"""
agents/recommendation_agent.py
Picks the single best product with reasoning.
"""

import json
from langchain_core.messages import HumanMessage, SystemMessage
from .llm import get_llm, rate_limited_call
from .schemas import (
    QueryUnderstanding, ComparisonResult,
    BudgetOptimizationResult, ReviewInsights, BestChoice
)

SYSTEM_PROMPT = """You are a senior product advisor. Given all analysis, pick ONE best product.
Respond ONLY with valid JSON (no markdown):
{
  "name": "Exact product name",
  "reason": "2-3 sentence explanation why this is the best choice for the user"
}"""


def run_recommendation_agent(
    query_info: QueryUnderstanding,
    comparison: ComparisonResult,
    budget_result: BudgetOptimizationResult,
    review: ReviewInsights | None,
) -> BestChoice:

    context = {
        "user_budget": query_info.budget,
        "product_type": query_info.product_type,
        "key_features_wanted": query_info.key_features,
        "best_value_product": comparison.best_value,
        "budget_approved": budget_result.recommended,
        "review_sentiment": review.sentiment if review else "unknown",
        "top_product_positives": review.positives[:3] if review else [],
    }

    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(context)),
    ]
    response = rate_limited_call(llm.invoke, messages)
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    data = json.loads(raw)
    return BestChoice(**data)
