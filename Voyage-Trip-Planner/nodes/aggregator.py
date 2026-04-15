"""
Aggregator Node - combines all state into final TripPlan.
"""

from typing import Dict, Any, List
from datetime import datetime
from utils.logger import logger


TIPS_PROMPT = """Generate 6 practical travel tips for this trip. Return ONLY JSON:
{"tips": ["tip1","tip2","tip3","tip4","tip5","tip6"]}"""


def aggregator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[Node: Aggregator] Starting")

    from models.trip_models import (
        TripPlan, MultiCurrencyAmount, CurrencyInfo,
        DestinationInfo, BudgetBreakdown
    )
    from tools.currency_converter import get_currency_converter

    converter = get_currency_converter()

    # ── Pull everything from state ───────────────────────────────────
    destination_info = state.get("destination_info")
    currency_info    = state.get("currency_info")
    budget_breakdown = state.get("budget_breakdown")
    hotels           = state.get("hotels")   or []
    itinerary        = state.get("itinerary") or []
    transport        = state.get("transport") or []
    weather_info     = state.get("weather_info")
    budget_inr       = float(state.get("budget_inr", 50000))
    duration_days    = int(state.get("duration_days", 5))
    interests        = state.get("interests", [])

    logger.info(
        f"[Node: Aggregator] Input: hotels={len(hotels)} "
        f"itinerary={len(itinerary)} transport={len(transport)}"
    )

    # ── Fallbacks for missing required objects ───────────────────────
    if not destination_info:
        destination_info = DestinationInfo(
            destination        = state.get("destination_query", "Unknown"),
            country            = "Unknown",
            is_domestic        = True,
            currency_code      = "INR",
            weather            = "N/A",
            best_time_to_visit = "N/A",
            highlights         = [],
            description        = "",
        )

    if not currency_info:
        currency_info = CurrencyInfo(
            base="INR", local="INR", usd="USD",
            exchange_rate_inr_to_local=1.0,
            exchange_rate_inr_to_usd=0.012,
        )

    if not budget_breakdown:
        # Emergency rule-based split
        is_dom = destination_info.is_domestic
        r = ({"flights": 0.25, "hotels": 0.32, "food": 0.20, "activities": 0.14, "transport": 0.09}
             if is_dom else
             {"flights": 0.38, "hotels": 0.28, "food": 0.14, "activities": 0.12, "transport": 0.08})

        def mc(v):
            conv = converter.get_full_conversion(v, currency_info.local, is_dom)
            return MultiCurrencyAmount(**conv)

        budget_breakdown = BudgetBreakdown(
            flights    = mc(budget_inr * r["flights"]),
            hotels     = mc(budget_inr * r["hotels"]),
            food       = mc(budget_inr * r["food"]),
            activities = mc(budget_inr * r["activities"]),
            transport  = mc(budget_inr * r["transport"]),
        )
        logger.warning("[Node: Aggregator] Used emergency budget split")

    is_domestic    = destination_info.is_domestic
    local_currency = currency_info.local

    # ── Total budget ─────────────────────────────────────────────────
    total_conv = converter.get_full_conversion(budget_inr, local_currency, is_domestic)

    # ── Tips ─────────────────────────────────────────────────────────
    tips = []
    try:
        from llm.groq_client import get_groq_client
        groq   = get_groq_client()
        result = groq.invoke_json(
            TIPS_PROMPT,
            f"Destination: {destination_info.destination}, {destination_info.country}\n"
            f"Duration: {duration_days} days\nBudget: Rs{budget_inr:,.0f}\n"
            f"Interests: {', '.join(interests)}"
        )
        if result and isinstance(result.get("tips"), list):
            tips = [str(t) for t in result["tips"] if t][:6]
    except Exception as e:
        logger.warning(f"[Node: Aggregator] Tips LLM failed: {e}")

    if not tips:
        tips = [
            f"Book accommodation at least 2 weeks in advance for {destination_info.destination}",
            "Carry local currency in small denominations for street shopping",
            "Download offline maps before your trip",
            "Try authentic local street food — it's often the best and cheapest",
            "Keep digital copies of all travel documents on your phone",
            "Purchase travel insurance that covers medical emergencies",
        ]

    # ── Build final plan ─────────────────────────────────────────────
    try:
        final_plan = TripPlan(
            destination      = destination_info.destination,
            country          = destination_info.country,
            is_domestic      = is_domestic,
            currency         = currency_info,
            duration_days    = duration_days,
            budget           = MultiCurrencyAmount(**total_conv),
            budget_breakdown = budget_breakdown,
            hotels           = hotels,
            itinerary        = itinerary,
            transport        = transport,
            destination_info = destination_info,
            weather          = weather_info,
            tips             = tips,
            generated_at     = datetime.now().isoformat(),
        )

        logger.info(
            f"[Node: Aggregator] TripPlan built: "
            f"hotels={len(final_plan.hotels)} "
            f"itinerary={len(final_plan.itinerary)} "
            f"transport={len(final_plan.transport)} "
            f"budget=Rs{final_plan.budget.inr:,.0f}"
        )

        return {**state, "final_plan": final_plan, "current_node": "aggregation_complete"}

    except Exception as e:
        logger.error(f"[Node: Aggregator] TripPlan build failed: {e}", exc_info=True)
        errors = list(state.get("errors", []))
        errors.append(f"Aggregator: {e}")
        return {**state, "errors": errors, "current_node": "aggregation_error"}