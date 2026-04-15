"""
agents/search_agent.py
Searches for products using Tavily and structures results with LLM.
"""

import json
from langchain_core.messages import HumanMessage, SystemMessage
from .llm import get_llm, rate_limited_call
from .schemas import QueryUnderstanding, ProductSearchResult, ProductItem
from tools.search_tools import _tavily_search

SYSTEM_PROMPT = """You are a product search assistant for Indian e-commerce.
Given search results text, extract up to 5 real products.
Respond ONLY with valid JSON (no markdown):
{
  "products": [
    {
      "name": "Full product name",
      "price": 12999,
      "rating": 4.2,
      "features": ["feature1", "feature2", "feature3"],
      "url": "https://... or null"
    }
  ]
}
- Price in INR (integer)
- Rating out of 5 (float). If unknown, use 4.0
- Include only realistic, real products
- If price unknown, estimate realistically for Indian market"""


def run_search_agent(query_info: QueryUnderstanding) -> ProductSearchResult:
    search_text = _tavily_search(query_info.search_query + " price buy India", max_results=5)
    snippets = "\n\n".join(
        f"Title: {r.get('title','')}\nContent: {r.get('content','')[:500]}"
        for r in search_text
    )
    if not snippets:
        snippets = f"Search for: {query_info.search_query} in India"

    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Budget: ₹{query_info.budget}\nSearch results:\n{snippets[:3000]}"),
    ]
    response = rate_limited_call(llm.invoke, messages)
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    data = json.loads(raw)

    # Filter to budget
    products = [
        ProductItem(**p) for p in data.get("products", [])
        if p.get("price", 0) <= query_info.budget * 1.1  # 10% tolerance
    ]
    return ProductSearchResult(products=products[:5])
