# Web search tool integration 

"""
Tavily Search Tool - Fetches real-world data for hotels, places, and travel info.
Uses caching to minimize API calls and retry logic for reliability.
"""

import os
from typing import List, Dict, Any, Optional
from tavily import TavilyClient
from utils.cache import cached
from utils.retry import with_retry
from utils.logger import logger
from dotenv import load_dotenv

load_dotenv()


class TavilySearchTool:
    """
    Wrapper around Tavily API for travel-specific searches.
    Implements caching and retry logic for production reliability.
    """

    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY environment variable not set")
        self.client = TavilyClient(api_key=api_key)
        logger.info("TavilySearchTool initialized")

    @cached(ttl=7200, prefix="tavily")
    @with_retry(max_attempts=3, min_wait=2.0, max_wait=8.0)
    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "advanced"
    ) -> List[Dict[str, Any]]:
        """
        Perform a Tavily search and return structured results.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_depth: "basic" or "advanced"
            
        Returns:
            List of search result dictionaries
        """
        logger.info(f"Tavily search: '{query[:80]}...' " if len(query) > 80 else f"Tavily search: '{query}'")
        
        response = self.client.search(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_answer=True,
            include_raw_content=False
        )
        
        results = []
        
        # Include the AI-generated answer if available
        if response.get("answer"):
            results.append({
                "type": "answer",
                "content": response["answer"],
                "url": "",
                "title": "Summary"
            })
        
        # Include individual search results
        for item in response.get("results", []):
            results.append({
                "type": "result",
                "title": item.get("title", ""),
                "content": item.get("content", ""),
                "url": item.get("url", ""),
                "score": item.get("score", 0.0)
            })
        
        logger.debug(f"Tavily returned {len(results)} results")
        return results

    def search_hotels(self, destination: str, budget_per_night_inr: float) -> List[Dict[str, Any]]:
        """Search for hotels at a destination within budget."""
        budget_category = self._get_budget_category(budget_per_night_inr)
        query = (
            f"{budget_category} hotels in {destination} "
            f"with good ratings booking.com MakeMyTrip 2024 2025"
        )
        return self.search(query, max_results=5)

    def search_destination_info(self, destination: str, interests: List[str]) -> List[Dict[str, Any]]:
        """Search for destination information and attractions."""
        interests_str = ", ".join(interests) if interests else "general tourism"
        query = (
            f"travel guide {destination} {interests_str} "
            f"best places to visit weather culture food 2024"
        )
        return self.search(query, max_results=5)

    def search_transport(self, origin: str, destination: str) -> List[Dict[str, Any]]:
        """Search for transport options between locations."""
        query = (
            f"flights trains transport from India to {destination} "
            f"cost booking 2024 2025"
        )
        return self.search(query, max_results=4)

    def search_activities(self, destination: str, interests: List[str]) -> List[Dict[str, Any]]:
        """Search for activities and attractions."""
        interests_str = " ".join(interests[:3]) if interests else "tourism"
        query = f"top activities things to do {destination} {interests_str} tourist attractions"
        return self.search(query, max_results=5)

    def _get_budget_category(self, budget_per_night_inr: float) -> str:
        """Categorize budget for search queries."""
        if budget_per_night_inr < 2000:
            return "budget affordable"
        elif budget_per_night_inr < 8000:
            return "mid-range comfortable"
        else:
            return "luxury premium"


# Singleton instance
_tavily_tool = None

def get_tavily_tool() -> TavilySearchTool:
    """Get singleton TavilySearchTool instance."""
    global _tavily_tool
    if _tavily_tool is None:
        _tavily_tool = TavilySearchTool()
    return _tavily_tool