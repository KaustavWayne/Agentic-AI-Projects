"""
Transport Node - always returns transport options.
"""

from typing import Dict, Any, List
from models.trip_models import TransportInfo, MultiCurrencyAmount
from tools.currency_converter import get_currency_converter
from utils.logger import logger


def _hardcoded_transport(
    destination: str,
    transport_budget: float,
    is_domestic: bool,
    converter,
    local_currency: str,
) -> List[TransportInfo]:
    """Always-available transport options."""
    dest_enc = destination.replace(" ", "-").lower()

    if is_domestic:
        options = [
            {"mode": "Flight", "provider": "IndiGo / SpiceJet / Air India",
             "cost": transport_budget * 0.65, "duration": "1-3 hours",
             "details": f"Direct or connecting domestic flights to {destination}",
             "link": f"https://www.makemytrip.com/flights/"},
            {"mode": "Train (IRCTC)", "provider": "Indian Railways",
             "cost": transport_budget * 0.25, "duration": "4-16 hours",
             "details": f"AC train to {destination} - comfortable and economical",
             "link": "https://www.irctc.co.in/nget/train-search"},
            {"mode": "Local Transport", "provider": "Ola / Uber / Auto",
             "cost": transport_budget * 0.10, "duration": "As needed",
             "details": f"Getting around {destination} by cab, auto or metro",
             "link": "https://www.olacabs.com"},
        ]
    else:
        options = [
            {"mode": "International Flight", "provider": "Air India / IndiGo / Emirates",
             "cost": transport_budget * 0.80, "duration": "4-14 hours",
             "details": f"International flights from India to {destination}",
             "link": "https://www.makemytrip.com/flights/international/"},
            {"mode": "Airport Transfer", "provider": "Local Taxi / Grab",
             "cost": transport_budget * 0.12, "duration": "30-60 min",
             "details": f"Airport to hotel transfer in {destination}",
             "link": ""},
            {"mode": "Local Transport", "provider": "Metro / Bus / Taxi",
             "cost": transport_budget * 0.08, "duration": "As needed",
             "details": f"Public and private transport within {destination}",
             "link": ""},
        ]

    results = []
    for opt in options:
        conv = converter.get_full_conversion(opt["cost"], local_currency, is_domestic)
        results.append(TransportInfo(
            mode           = opt["mode"],
            provider       = opt["provider"],
            estimated_cost = MultiCurrencyAmount(**conv),
            duration       = opt["duration"],
            details        = opt["details"],
            booking_link   = opt["link"],
        ))
    return results


def transport_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Transport Node - always returns options."""
    logger.info("[Node: Transport] Starting")

    destination_info = state.get("destination_info")
    budget_breakdown = state.get("budget_breakdown")
    currency_info    = state.get("currency_info")
    budget_inr       = float(state.get("budget_inr", 50000))

    destination    = destination_info.destination if destination_info else state.get("destination_query","")
    is_domestic    = destination_info.is_domestic if destination_info else True
    local_currency = currency_info.local if currency_info else "INR"
    converter      = get_currency_converter()

    transport_budget = (budget_breakdown.transport.inr
                        if budget_breakdown and budget_breakdown.transport.inr > 0
                        else budget_inr * 0.10)

    # ── Try LLM first ───────────────────────────────────────────────
    transport = []
    try:
        from tools.tavily_search import get_tavily_tool
        from llm.groq_client import get_groq_client

        tavily = get_tavily_tool()
        groq   = get_groq_client()

        search = tavily.search_transport("India", destination)
        context_parts = []
        for r in search[:3]:
            if r.get("content"):
                context_parts.append(r["content"][:400])
        context = "\n".join(context_parts)

        SYSTEM = """Return ONLY this JSON (no markdown):
{
  "transport_options": [
    {
      "mode": "Flight",
      "provider": "Air India",
      "estimated_cost_inr": 15000,
      "duration": "3 hours",
      "details": "Direct flight",
      "booking_link": "https://www.makemytrip.com"
    }
  ]
}
Return 2-3 options. All cost values must be numbers."""

        result = groq.invoke_json(SYSTEM,
            f"From: India\nTo: {destination}\nDomestic: {is_domestic}\n"
            f"Transport budget: {transport_budget} INR\nContext:\n{context}")

        raw = result.get("transport_options", []) if result else []
        for t in raw[:3]:
            cost = float(t.get("estimated_cost_inr") or transport_budget * 0.5)
            if cost <= 0:
                cost = transport_budget * 0.5
            conv = converter.get_full_conversion(cost, local_currency, is_domestic)
            transport.append(TransportInfo(
                mode           = t.get("mode") or "Transport",
                provider       = t.get("provider") or "Various",
                estimated_cost = MultiCurrencyAmount(**conv),
                duration       = t.get("duration") or "Varies",
                details        = t.get("details") or "",
                booking_link   = t.get("booking_link") or "",
            ))
    except Exception as e:
        logger.warning(f"[Node: Transport] LLM failed: {e}")

    # ── Fallback ────────────────────────────────────────────────────
    if not transport:
        transport = _hardcoded_transport(
            destination, transport_budget, is_domestic, converter, local_currency
        )

    logger.info(f"[Node: Transport] Returning {len(transport)} options")
    return {**state, "transport": transport, "current_node": "transport_complete"}