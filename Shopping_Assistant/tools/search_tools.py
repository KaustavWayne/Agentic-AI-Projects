"""
tools/search_tools.py
Product search and data extraction tools using Tavily.
"""

import os
import json
import time
import hashlib
import diskcache
from typing import Any
from langchain_core.tools import tool
from tavily import TavilyClient

# ── Cache (avoids repeated API hits on free tier) ──────────────────────────
cache = diskcache.Cache("/tmp/shopping_cache")
CACHE_TTL = 3600  # 1 hour


def _cache_key(prefix: str, payload: str) -> str:
    return prefix + ":" + hashlib.md5(payload.encode()).hexdigest()


def _tavily_search(query: str, max_results: int = 3) -> list[dict]:
    """Rate-limit-aware Tavily wrapper with caching."""
    key = _cache_key("tavily", query + str(max_results))
    if key in cache:
        return cache[key]

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    try:
        time.sleep(0.5)  # gentle throttle for free tier
        results = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_answer=True,
        )
        data = results.get("results", [])
        cache.set(key, data, expire=CACHE_TTL)
        return data
    except Exception as e:
        print(f"[Tavily Error] {e}")
        return []


@tool
def search_products(query: str) -> str:
    """Search for products using Tavily. Returns raw search snippets."""
    results = _tavily_search(query, max_results=5)
    if not results:
        return "No results found."
    snippets = []
    for r in results:
        snippets.append(f"Title: {r.get('title','')}\nURL: {r.get('url','')}\nContent: {r.get('content','')[:400]}")
    return "\n\n---\n\n".join(snippets)


@tool
def search_reviews(product_name: str) -> str:
    """Search for user reviews of a product."""
    query = f"{product_name} user reviews pros cons 2024 2025"
    results = _tavily_search(query, max_results=3)
    if not results:
        return "No review data found."
    snippets = [r.get("content", "")[:500] for r in results]
    return "\n\n".join(snippets)


@tool
def search_price(product_name: str) -> str:
    """Search for current pricing of a product."""
    query = f"{product_name} price buy online India rupees 2024 2025"
    results = _tavily_search(query, max_results=3)
    if not results:
        return "Price info not available."
    snippets = [r.get("content", "")[:300] for r in results]
    return "\n\n".join(snippets)
