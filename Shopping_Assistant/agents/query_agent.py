"""
agents/query_agent.py
Extracts product type, budget, and preferences from natural language.
"""

import json
from langchain_core.messages import HumanMessage, SystemMessage
from .llm import get_llm, rate_limited_call
from .schemas import QueryUnderstanding

SYSTEM_PROMPT = """You are a shopping query parser. Extract structured info from user queries.
Respond ONLY with valid JSON matching this schema (no markdown, no extra text):
{
  "product_type": "string",
  "budget": number,
  "brand_preference": "string or null",
  "key_features": ["list", "of", "strings"],
  "search_query": "optimised search string for product lookup in India"
}
Budget must be in INR. If not mentioned, default to 50000."""


def run_query_agent(user_query: str) -> QueryUnderstanding:
    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_query),
    ]
    response = rate_limited_call(llm.invoke, messages)
    raw = response.content.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    data = json.loads(raw)
    return QueryUnderstanding(**data)
