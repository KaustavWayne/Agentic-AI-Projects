"""
agents/comparison_agent.py
Compares top products and highlights pros/cons/best value.
"""

import json
from langchain_core.messages import HumanMessage, SystemMessage
from .llm import get_llm, rate_limited_call
from .schemas import ProductSearchResult, ComparisonResult, ProductComparison

SYSTEM_PROMPT = """You are a product comparison expert. Compare the given products and return structured analysis.
Respond ONLY with valid JSON (no markdown):
{
  "comparisons": [
    {
      "name": "Product Name",
      "price": 12999,
      "rating": 4.2,
      "pros": ["pro1", "pro2", "pro3"],
      "cons": ["con1", "con2"],
      "value_score": 8.5
    }
  ],
  "best_value": "Product Name with best price-to-performance"
}
value_score: 0-10 based on price vs features vs rating. Higher is better."""


def run_comparison_agent(search_result: ProductSearchResult) -> ComparisonResult:
    if not search_result.products:
        return ComparisonResult(comparisons=[], best_value="No products found")

    products_text = json.dumps(
        [p.model_dump() for p in search_result.products],
        indent=2
    )

    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Compare these products:\n{products_text[:2500]}"),
    ]
    response = rate_limited_call(llm.invoke, messages)
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    data = json.loads(raw)
    comparisons = [ProductComparison(**c) for c in data.get("comparisons", [])]
    return ComparisonResult(
        comparisons=comparisons,
        best_value=data.get("best_value", comparisons[0].name if comparisons else "")
    )
