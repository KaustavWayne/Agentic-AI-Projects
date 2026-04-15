"""
agents/review_agent.py
Summarises user reviews for the top product.
"""

import json
from langchain_core.messages import HumanMessage, SystemMessage
from .llm import get_llm, rate_limited_call
from .schemas import ReviewInsights
from tools.search_tools import _tavily_search

SYSTEM_PROMPT = """You are a review analyst. Summarise product reviews.
Respond ONLY with valid JSON (no markdown):
{
  "product_name": "Name",
  "positives": ["positive1", "positive2", "positive3"],
  "negatives": ["negative1", "negative2"],
  "common_issues": ["issue1", "issue2"],
  "sentiment": "positive"
}
sentiment must be one of: positive, neutral, negative"""


def run_review_agent(product_name: str) -> ReviewInsights:
    results = _tavily_search(f"{product_name} review pros cons India 2024", max_results=3)
    review_text = "\n\n".join(r.get("content", "")[:400] for r in results)
    if not review_text:
        review_text = f"Limited reviews available for {product_name}"

    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Product: {product_name}\nReviews:\n{review_text[:2000]}"),
    ]
    response = rate_limited_call(llm.invoke, messages)
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    data = json.loads(raw)
    return ReviewInsights(**data)
