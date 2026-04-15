"""
graph/shopping_graph.py
LangGraph multi-agent graph for the Shopping Assistant.
"""

from __future__ import annotations
from typing import TypedDict, Optional, Any
import json

from langgraph.graph import StateGraph, END

from agents.schemas import (
    QueryUnderstanding, ProductSearchResult, ComparisonResult,
    BudgetOptimizationResult, ReviewInsights, BestChoice,
    ShoppingAssistantOutput,
)
from agents.query_agent import run_query_agent
from agents.search_agent import run_search_agent
from agents.comparison_agent import run_comparison_agent
from agents.budget_agent import run_budget_agent
from agents.review_agent import run_review_agent
from agents.recommendation_agent import run_recommendation_agent
from agents.aggregator_agent import run_aggregator_agent


# ── Shared state ──────────────────────────────────────────────────────────

class ShoppingState(TypedDict, total=False):
    user_query: str
    query_info: Optional[QueryUnderstanding]
    search_result: Optional[ProductSearchResult]
    comparison: Optional[ComparisonResult]
    budget_result: Optional[BudgetOptimizationResult]
    review: Optional[ReviewInsights]
    best_choice: Optional[BestChoice]
    final_output: Optional[ShoppingAssistantOutput]
    error: Optional[str]
    status_updates: list[str]


# ── Node functions ────────────────────────────────────────────────────────

def node_query_understanding(state: ShoppingState) -> ShoppingState:
    updates: list[str] = state.get("status_updates", [])
    try:
        updates.append("🔍 Understanding your query...")
        result = run_query_agent(state["user_query"])
        return {**state, "query_info": result, "status_updates": updates}
    except Exception as e:
        return {**state, "error": f"Query agent failed: {e}", "status_updates": updates}


def node_product_search(state: ShoppingState) -> ShoppingState:
    updates: list[str] = state.get("status_updates", [])
    if state.get("error"):
        return state
    try:
        updates.append("🛒 Searching for products...")
        result = run_search_agent(state["query_info"])
        return {**state, "search_result": result, "status_updates": updates}
    except Exception as e:
        return {**state, "error": f"Search agent failed: {e}", "status_updates": updates}


def node_comparison(state: ShoppingState) -> ShoppingState:
    updates: list[str] = state.get("status_updates", [])
    if state.get("error"):
        return state
    try:
        updates.append("⚖️ Comparing products...")
        result = run_comparison_agent(state["search_result"])
        return {**state, "comparison": result, "status_updates": updates}
    except Exception as e:
        return {**state, "error": f"Comparison agent failed: {e}", "status_updates": updates}


def node_budget_optimization(state: ShoppingState) -> ShoppingState:
    updates: list[str] = state.get("status_updates", [])
    if state.get("error"):
        return state
    try:
        updates.append("💰 Optimizing for your budget...")
        result = run_budget_agent(state["query_info"], state["comparison"])
        return {**state, "budget_result": result, "status_updates": updates}
    except Exception as e:
        return {**state, "error": f"Budget agent failed: {e}", "status_updates": updates}


def node_review_insights(state: ShoppingState) -> ShoppingState:
    updates: list[str] = state.get("status_updates", [])
    if state.get("error"):
        return state
    try:
        updates.append("📝 Analysing reviews...")
        best = state["comparison"].best_value
        result = run_review_agent(best)
        return {**state, "review": result, "status_updates": updates}
    except Exception as e:
        # Non-fatal: continue without reviews
        updates.append("⚠️ Could not fetch reviews, continuing...")
        return {**state, "review": None, "status_updates": updates}


def node_final_recommendation(state: ShoppingState) -> ShoppingState:
    updates: list[str] = state.get("status_updates", [])
    if state.get("error"):
        return state
    try:
        updates.append("🏆 Generating final recommendation...")
        result = run_recommendation_agent(
            state["query_info"],
            state["comparison"],
            state["budget_result"],
            state.get("review"),
        )
        return {**state, "best_choice": result, "status_updates": updates}
    except Exception as e:
        return {**state, "error": f"Recommendation agent failed: {e}", "status_updates": updates}


def node_aggregator(state: ShoppingState) -> ShoppingState:
    updates: list[str] = state.get("status_updates", [])
    if state.get("error"):
        return state
    try:
        updates.append("📦 Assembling final output...")
        result = run_aggregator_agent(
            state["query_info"],
            state["search_result"],
            state["comparison"],
            state["budget_result"],
            state.get("review"),
            state["best_choice"],
        )
        return {**state, "final_output": result, "status_updates": updates}
    except Exception as e:
        return {**state, "error": f"Aggregator failed: {e}", "status_updates": updates}


def should_continue(state: ShoppingState) -> str:
    return "end" if state.get("error") else "continue"


# ── Build graph ───────────────────────────────────────────────────────────

def build_shopping_graph() -> StateGraph:
    graph = StateGraph(ShoppingState)

    graph.add_node("query_understanding", node_query_understanding)
    graph.add_node("product_search", node_product_search)
    graph.add_node("comparison", node_comparison)
    graph.add_node("budget_optimization", node_budget_optimization)
    graph.add_node("review_insights", node_review_insights)
    graph.add_node("final_recommendation", node_final_recommendation)
    graph.add_node("aggregator", node_aggregator)

    graph.set_entry_point("query_understanding")

    graph.add_edge("query_understanding", "product_search")
    graph.add_edge("product_search", "comparison")
    graph.add_edge("comparison", "budget_optimization")
    graph.add_edge("budget_optimization", "review_insights")
    graph.add_edge("review_insights", "final_recommendation")
    graph.add_edge("final_recommendation", "aggregator")
    graph.add_edge("aggregator", END)

    return graph.compile()


_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_shopping_graph()
    return _compiled_graph


def run_shopping_assistant(user_query: str) -> dict[str, Any]:
    """Entry point: run the full graph and return JSON-serialisable output."""
    graph = get_graph()
    initial_state: ShoppingState = {
        "user_query": user_query,
        "status_updates": [],
    }
    final_state = graph.invoke(initial_state)

    if final_state.get("error"):
        return {"error": final_state["error"]}

    output: ShoppingAssistantOutput = final_state["final_output"]
    return json.loads(output.model_dump_json())
