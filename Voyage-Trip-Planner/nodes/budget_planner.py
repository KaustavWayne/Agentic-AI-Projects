"""
Budget Planner Node - rule-based primary, LLM enhancement secondary.
Guarantees non-zero budget breakdown always.
"""

from typing import Dict, Any
from models.trip_models import BudgetBreakdown, MultiCurrencyAmount
from tools.currency_converter import get_currency_converter
from utils.logger import logger


def _rule_based_split(budget_inr: float, is_domestic: bool,
                      travel_style: str, duration_days: int) -> Dict[str, float]:
    """Always returns valid non-zero split. Primary calculation method."""
    if is_domestic:
        ratios = {
            "budget":    {"flights": 0.20, "hotels": 0.28, "food": 0.22, "activities": 0.18, "transport": 0.12},
            "mid-range": {"flights": 0.25, "hotels": 0.32, "food": 0.20, "activities": 0.14, "transport": 0.09},
            "luxury":    {"flights": 0.22, "hotels": 0.40, "food": 0.20, "activities": 0.12, "transport": 0.06},
        }
    else:
        ratios = {
            "budget":    {"flights": 0.40, "hotels": 0.25, "food": 0.15, "activities": 0.12, "transport": 0.08},
            "mid-range": {"flights": 0.38, "hotels": 0.28, "food": 0.14, "activities": 0.12, "transport": 0.08},
            "luxury":    {"flights": 0.35, "hotels": 0.35, "food": 0.13, "activities": 0.11, "transport": 0.06},
        }
    style = travel_style if travel_style in ratios else "mid-range"
    r = ratios[style]
    return {
        "flights_inr":    round(budget_inr * r["flights"],    2),
        "hotels_inr":     round(budget_inr * r["hotels"],     2),
        "food_inr":       round(budget_inr * r["food"],       2),
        "activities_inr": round(budget_inr * r["activities"], 2),
        "transport_inr":  round(budget_inr * r["transport"],  2),
    }


def budget_planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Budget Planner - guaranteed non-zero output."""
    logger.info("[Node: Budget Planner] Starting")

    budget_inr    = float(state.get("budget_inr", 50000))
    duration_days = int(state.get("duration_days", 5))
    destination_info = state.get("destination_info")
    currency_info    = state.get("currency_info")
    travel_style     = state.get("travel_style", "mid-range")

    is_domestic    = destination_info.is_domestic if destination_info else True
    local_currency = currency_info.local if currency_info else "INR"
    converter      = get_currency_converter()

    # ── Always compute rule-based split first ───────────────────────
    split = _rule_based_split(budget_inr, is_domestic, travel_style, duration_days)

    # ── Optionally try LLM to refine (don't fail if it errors) ──────
    try:
        from llm.groq_client import get_groq_client
        groq = get_groq_client()
        dest_name = destination_info.destination if destination_info else "destination"

        SYSTEM = """Return ONLY JSON budget split (no markdown):
{
  "flights_inr": 0,
  "hotels_inr": 0,
  "food_inr": 0,
  "activities_inr": 0,
  "transport_inr": 0
}
All values must be numbers. Total must equal budget_inr exactly."""

        result = groq.invoke_json(SYSTEM,
            f"Destination: {dest_name}\n"
            f"Budget: {budget_inr}\n"
            f"Days: {duration_days}\n"
            f"Style: {travel_style}\n"
            f"Domestic: {is_domestic}\n"
            f"Split the {budget_inr} INR budget into the 5 categories.")

        if result:
            llm_flights    = float(result.get("flights_inr", 0) or 0)
            llm_hotels     = float(result.get("hotels_inr", 0) or 0)
            llm_food       = float(result.get("food_inr", 0) or 0)
            llm_activities = float(result.get("activities_inr", 0) or 0)
            llm_transport  = float(result.get("transport_inr", 0) or 0)
            llm_total      = llm_flights + llm_hotels + llm_food + llm_activities + llm_transport

            # Only use LLM split if all values are positive and total is reasonable
            if (llm_total > 0 and
                all(v > 0 for v in [llm_flights, llm_hotels, llm_food, llm_activities, llm_transport])):
                # Normalise to exact budget
                scale = budget_inr / llm_total
                split = {
                    "flights_inr":    round(llm_flights    * scale, 2),
                    "hotels_inr":     round(llm_hotels     * scale, 2),
                    "food_inr":       round(llm_food       * scale, 2),
                    "activities_inr": round(llm_activities * scale, 2),
                    "transport_inr":  round(llm_transport  * scale, 2),
                }
                logger.info("[Node: Budget Planner] Using LLM split")
            else:
                logger.warning("[Node: Budget Planner] LLM split invalid, using rule-based")
    except Exception as e:
        logger.warning(f"[Node: Budget Planner] LLM failed (using rule-based): {e}")

    # ── Build MultiCurrencyAmount for each category ──────────────────
    def mc(amount_inr: float) -> MultiCurrencyAmount:
        conv = converter.get_full_conversion(amount_inr, local_currency, is_domestic)
        return MultiCurrencyAmount(**conv)

    budget_breakdown = BudgetBreakdown(
        flights    = mc(split["flights_inr"]),
        hotels     = mc(split["hotels_inr"]),
        food       = mc(split["food_inr"]),
        activities = mc(split["activities_inr"]),
        transport  = mc(split["transport_inr"]),
    )

    logger.info(
        f"[Node: Budget Planner] Done: flights=₹{split['flights_inr']:,.0f} "
        f"hotels=₹{split['hotels_inr']:,.0f} food=₹{split['food_inr']:,.0f}"
    )
    return {**state, "budget_breakdown": budget_breakdown,
            "current_node": "budget_planner_complete"}