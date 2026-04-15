"""
Hotel Finder Node - always returns hotels.
Tries Tavily+LLM, falls back to realistic hardcoded options.
"""

from typing import Dict, Any, List
from models.trip_models import HotelOption, MultiCurrencyAmount
from tools.currency_converter import get_currency_converter
from utils.logger import logger


# Realistic hotel templates by travel style
HOTEL_TEMPLATES = {
    "budget": [
        {"suffix": "Backpackers Hostel",  "rating": 3.6, "price_factor": 0.40},
        {"suffix": "Budget Inn",           "rating": 3.4, "price_factor": 0.35},
        {"suffix": "Economy Lodge",        "rating": 3.2, "price_factor": 0.30},
    ],
    "mid-range": [
        {"suffix": "Grand Hotel",          "rating": 4.1, "price_factor": 0.55},
        {"suffix": "Comfort Suites",       "rating": 3.9, "price_factor": 0.48},
        {"suffix": "Premier Inn",          "rating": 4.0, "price_factor": 0.52},
    ],
    "luxury": [
        {"suffix": "Luxury Palace Hotel",  "rating": 4.7, "price_factor": 0.75},
        {"suffix": "Five Star Resort",     "rating": 4.8, "price_factor": 0.82},
        {"suffix": "Boutique Grand Hotel", "rating": 4.6, "price_factor": 0.70},
    ],
}

AMENITY_MAP = {
    "budget":    ["Free WiFi", "24/7 Reception", "Common Kitchen", "Lockers"],
    "mid-range": ["Free WiFi", "AC", "Restaurant", "Room Service", "Parking"],
    "luxury":    ["Free WiFi", "AC", "Pool", "Spa", "Fine Dining", "Concierge", "Gym"],
}


def _make_fallback_hotels(
    destination: str,
    hotel_budget_total: float,
    duration_days: int,
    travel_style: str,
    converter,
    local_currency: str,
    is_domestic: bool,
) -> List[HotelOption]:
    """Generate realistic fallback hotels when API/LLM fails."""
    per_night_base = hotel_budget_total / max(duration_days, 1)
    style          = travel_style if travel_style in HOTEL_TEMPLATES else "mid-range"
    templates      = HOTEL_TEMPLATES[style]
    amenities      = AMENITY_MAP[style]
    dest_enc       = destination.replace(" ", "+")
    hotels         = []

    for t in templates:
        price_inr = round(per_night_base * t["price_factor"], 0)
        if price_inr < 500:
            price_inr = 500

        conv = converter.get_full_conversion(price_inr, local_currency, is_domestic)

        booking_sites = [
            f"https://www.booking.com/search.html?ss={dest_enc}",
            f"https://www.makemytrip.com/hotels/hotel-listing/?city={dest_enc}",
            f"https://www.goibibo.com/hotels/{dest_enc.lower()}-hotels/",
        ]

        hotels.append(HotelOption(
            name            = f"{destination.title()} {t['suffix']}",
            price_per_night = MultiCurrencyAmount(**conv),
            rating          = t["rating"],
            location        = f"City Centre, {destination.title()}",
            booking_link    = booking_sites[len(hotels) % len(booking_sites)],
            amenities       = amenities,
            image_url       = "",
        ))

    return hotels


def hotel_finder_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Hotel Finder - always returns at least 3 hotels."""
    logger.info("[Node: Hotel Finder] Starting")

    destination_info = state.get("destination_info")
    budget_breakdown = state.get("budget_breakdown")
    currency_info    = state.get("currency_info")
    duration_days    = int(state.get("duration_days", 5))
    travel_style     = state.get("travel_style", "mid-range")
    budget_inr       = float(state.get("budget_inr", 50000))

    destination    = destination_info.destination if destination_info else state.get("destination_query", "")
    is_domestic    = destination_info.is_domestic if destination_info else True
    local_currency = currency_info.local if currency_info else "INR"
    converter      = get_currency_converter()

    hotel_budget_total = (budget_breakdown.hotels.inr
                          if budget_breakdown and budget_breakdown.hotels.inr > 0
                          else budget_inr * 0.32)
    per_night = hotel_budget_total / max(duration_days, 1)

    # ── Try Tavily + LLM ────────────────────────────────────────────
    hotels = []
    try:
        from tools.tavily_search import get_tavily_tool
        from llm.groq_client import get_groq_client

        tavily = get_tavily_tool()
        groq   = get_groq_client()

        search_results = tavily.search_hotels(destination, per_night)
        context_parts  = []
        for r in search_results[:4]:
            if r.get("content"):
                url = r.get("url", "")
                context_parts.append(f"URL:{url}\n{r['content'][:600]}")
        context = "\n---\n".join(context_parts) or f"Hotels in {destination}"

        SYSTEM = """Extract hotels and return ONLY this JSON (no markdown):
{
  "hotels": [
    {
      "name": "Hotel Name",
      "price_per_night_inr": 3000,
      "rating": 4.2,
      "location": "Area, City",
      "booking_link": "https://www.booking.com/...",
      "amenities": ["WiFi","AC","Pool"]
    }
  ]
}
Return 3 hotels. All price values must be numbers. Ratings must be 1.0-5.0."""

        result = groq.invoke_json(SYSTEM,
            f"Destination: {destination}\n"
            f"Budget per night: {per_night} INR\n"
            f"Travel style: {travel_style}\n"
            f"Search data:\n{context}")

        raw_hotels = result.get("hotels", []) if result else []

        for h in raw_hotels[:3]:
            price_inr = float(h.get("price_per_night_inr") or per_night * 0.7)
            if price_inr <= 0:
                price_inr = per_night * 0.7

            conv  = converter.get_full_conversion(price_inr, local_currency, is_domestic)
            link  = h.get("booking_link") or f"https://www.booking.com/search.html?ss={destination.replace(' ','+')}"
            rating = float(h.get("rating") or 3.5)
            rating = max(1.0, min(5.0, rating))

            hotels.append(HotelOption(
                name            = h.get("name") or f"Hotel in {destination}",
                price_per_night = MultiCurrencyAmount(**conv),
                rating          = rating,
                location        = h.get("location") or destination,
                booking_link    = link,
                amenities       = h.get("amenities") or ["WiFi", "AC"],
                image_url       = "",
            ))

    except Exception as e:
        logger.warning(f"[Node: Hotel Finder] Tavily/LLM failed: {e}")

    # ── Always ensure 3 hotels ──────────────────────────────────────
    if len(hotels) < 3:
        logger.info(f"[Node: Hotel Finder] Got {len(hotels)} from LLM, filling with fallback")
        fallback = _make_fallback_hotels(
            destination, hotel_budget_total, duration_days,
            travel_style, converter, local_currency, is_domestic
        )
        # Merge: keep LLM hotels, fill remaining from fallback
        existing_names = {h.name for h in hotels}
        for fh in fallback:
            if len(hotels) >= 3:
                break
            if fh.name not in existing_names:
                hotels.append(fh)

    logger.info(f"[Node: Hotel Finder] Returning {len(hotels)} hotels")
    return {**state, "hotels": hotels, "current_node": "hotel_finder_complete"}