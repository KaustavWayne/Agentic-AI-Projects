"""
Itinerary Planner Node - always returns a full itinerary.
Uses city DB activities or generic templates when LLM fails.
"""

from typing import Dict, Any, List
from models.trip_models import DayItinerary, ItineraryActivity, MultiCurrencyAmount
from tools.currency_converter import get_currency_converter
from utils.logger import logger


# Per-city activity templates
CITY_ACTIVITIES = {
    "kolkata": [
        [("09:00 AM", "Visit Victoria Memorial", "Victoria Memorial", 200),
         ("12:00 PM", "Explore Howrah Bridge", "Howrah Bridge", 0),
         ("02:00 PM", "Lunch at Peter Cat restaurant", "Peter Cat, Park Street", 600),
         ("04:00 PM", "Stroll on Park Street", "Park Street, Kolkata", 0),
         ("07:00 PM", "Watch Ganga Aarti at Prinsep Ghat", "Prinsep Ghat", 0)],
        [("08:00 AM", "Morning at Kalighat Temple", "Kalighat Temple", 0),
         ("11:00 AM", "Visit Indian Museum", "Indian Museum, Kolkata", 30),
         ("01:00 PM", "Kathi roll lunch at Nizam's", "Nizam's Restaurant", 200),
         ("03:00 PM", "Shop at New Market", "New Market, Kolkata", 1000),
         ("07:00 PM", "Dinner at Oh! Calcutta", "Oh! Calcutta Restaurant", 800)],
        [("07:30 AM", "Morning boat ride on Ganges", "Babughat Ferry", 50),
         ("10:00 AM", "Explore Kumartuli potters district", "Kumartuli, Kolkata", 0),
         ("12:30 PM", "Street food at Dacres Lane", "Dacres Lane, Kolkata", 150),
         ("03:00 PM", "Visit Marble Palace", "Marble Palace, Kolkata", 10),
         ("06:00 PM", "Sunset at Eco Park", "Eco Park New Town", 30)],
    ],
    "mumbai": [
        [("09:00 AM", "Visit Gateway of India", "Gateway of India", 0),
         ("10:30 AM", "Explore Colaba Causeway market", "Colaba Causeway", 500),
         ("01:00 PM", "Lunch at Leopold Cafe", "Leopold Cafe, Colaba", 700),
         ("03:00 PM", "Marine Drive sunset walk", "Marine Drive", 0),
         ("08:00 PM", "Dinner at street food stalls at Juhu", "Juhu Beach", 300)],
        [("08:00 AM", "Ferry to Elephanta Caves", "Elephanta Caves", 600),
         ("01:00 PM", "Vada pav at iconic stall", "Andheri Station", 50),
         ("03:00 PM", "Visit Dharavi documentary walk", "Dharavi, Mumbai", 400),
         ("06:00 PM", "Bandra Bandstand sea walk", "Bandstand Promenade", 0),
         ("08:30 PM", "Dinner at Bademiya", "Bademiya, Colaba", 500)],
    ],
    "bangkok": [
        [("08:00 AM", "Grand Palace & Wat Phra Kaew", "Grand Palace, Bangkok", 500),
         ("11:30 AM", "Wat Pho Reclining Buddha", "Wat Pho Temple", 200),
         ("01:00 PM", "Riverside lunch", "Asiatique Riverfront", 800),
         ("04:00 PM", "Chao Phraya river boat tour", "Chao Phraya River", 400),
         ("07:00 PM", "Khao San Road nightlife", "Khao San Road", 1000)],
        [("09:00 AM", "Damnoen Saduak Floating Market", "Damnoen Saduak", 1500),
         ("01:00 PM", "Chatuchak Weekend Market shopping", "Chatuchak Market", 2000),
         ("04:00 PM", "Jim Thompson House museum", "Jim Thompson House", 500),
         ("07:00 PM", "Rooftop bar dinner", "Sky Bar, Lebua Hotel", 3000),
         ("10:00 PM", "Silom nightlife walk", "Silom Road", 1000)],
    ],
    "goa": [
        [("09:00 AM", "Baga Beach morning swim", "Baga Beach", 0),
         ("11:00 AM", "Water sports at Calangute", "Calangute Beach", 1500),
         ("01:30 PM", "Seafood lunch at beach shack", "Curlies Beach Shack", 600),
         ("04:00 PM", "Visit Basilica of Bom Jesus", "Old Goa Churches", 0),
         ("07:00 PM", "Sundowner at Sunset Point", "Vagator Beach", 0)],
        [("08:00 AM", "Dudhsagar Falls day trip", "Dudhsagar Falls", 1200),
         ("01:00 PM", "Lunch at local dhaba", "Panjim Market Area", 300),
         ("03:00 PM", "Spice plantation tour", "Tropical Spice Plantation", 800),
         ("06:00 PM", "Anjuna Flea Market", "Anjuna Market", 1000),
         ("08:30 PM", "Dinner at Infantaria", "Infantaria Bakery Cafe", 700)],
    ],
    "delhi": [
        [("08:00 AM", "Red Fort early morning visit", "Red Fort, Delhi", 35),
         ("10:30 AM", "Jama Masjid exploration", "Jama Masjid", 0),
         ("12:00 PM", "Chandni Chowk street food walk", "Chandni Chowk", 300),
         ("03:00 PM", "India Gate & Rajpath walk", "India Gate", 0),
         ("07:00 PM", "Dinner at Karim's", "Karim's Restaurant, Old Delhi", 500)],
        [("09:00 AM", "Qutub Minar complex", "Qutub Minar", 35),
         ("11:30 AM", "Hauz Khas Village art walk", "Hauz Khas Village", 0),
         ("01:30 PM", "Humayun's Tomb", "Humayun's Tomb", 35),
         ("04:00 PM", "Khan Market shopping", "Khan Market", 1000),
         ("08:00 PM", "Dinner at Bukhara ITC Maurya", "Bukhara Restaurant", 3000)],
    ],
}


def _get_generic_activities(destination: str, day_num: int) -> List[tuple]:
    """Generic day template for any destination."""
    templates = [
        [("09:00 AM", f"Explore {destination} city centre & main square",
          f"City Centre, {destination}", 200),
         ("11:30 AM", f"Visit main heritage monument",
          f"Main Monument, {destination}", 300),
         ("01:00 PM", "Lunch at popular local restaurant",
          f"Local Restaurant, {destination}", 400),
         ("03:30 PM", "Cultural museum visit",
          f"City Museum, {destination}", 150),
         ("06:00 PM", "Sunset viewpoint photography",
          f"Viewpoint, {destination}", 0),
         ("08:00 PM", "Dinner at recommended eatery",
          f"Famous Restaurant, {destination}", 600)],
        [("08:30 AM", "Morning local market exploration",
          f"Local Market, {destination}", 500),
         ("11:00 AM", "Guided city heritage walk",
          f"Heritage District, {destination}", 200),
         ("01:00 PM", "Street food lunch experience",
          f"Street Food Lane, {destination}", 250),
         ("03:00 PM", "Shopping for local handicrafts",
          f"Souvenir Market, {destination}", 1000),
         ("06:30 PM", "Cultural performance or show",
          f"Cultural Centre, {destination}", 400),
         ("08:30 PM", "Farewell dinner at top-rated restaurant",
          f"Top Restaurant, {destination}", 800)],
        [("07:30 AM", "Nature walk or park visit",
          f"City Park, {destination}", 0),
         ("10:00 AM", "Local temple or religious site",
          f"Main Temple, {destination}", 0),
         ("12:30 PM", "Traditional cuisine lunch",
          f"Traditional Restaurant, {destination}", 350),
         ("02:30 PM", "Art gallery or exhibition",
          f"Art Gallery, {destination}", 100),
         ("05:00 PM", "Waterfront or garden stroll",
          f"Waterfront, {destination}", 0),
         ("07:30 PM", "Rooftop dinner with city views",
          f"Rooftop Restaurant, {destination}", 700)],
    ]
    return templates[(day_num - 1) % len(templates)]


def _activities_to_plan(
    activities: List[tuple],
    destination: str,
    converter,
    local_currency: str,
    is_domestic: bool,
) -> List[ItineraryActivity]:
    """Convert activity tuples to ItineraryActivity models."""
    plan = []
    for time_str, activity, place, cost_inr in activities:
        conv      = converter.get_full_conversion(float(cost_inr), local_currency, is_domestic)
        place_enc = place.replace(" ", "+")
        link      = f"https://www.google.com/maps/search/{place_enc}"

        plan.append(ItineraryActivity(
            time            = time_str,
            activity        = activity,
            place           = place,
            place_link      = link,
            estimated_cost  = MultiCurrencyAmount(**conv),
            duration_hours  = 1.5,
        ))
    return plan


def _build_fallback_itinerary(
    destination: str,
    duration_days: int,
    converter,
    local_currency: str,
    is_domestic: bool,
) -> List[DayItinerary]:
    """Build complete fallback itinerary from city DB or generic templates."""
    dest_key = destination.lower().strip()
    # Find city match
    city_acts = None
    for key, acts in CITY_ACTIVITIES.items():
        if key in dest_key or dest_key in key:
            city_acts = acts
            break

    days = []
    day_titles = [
        "Arrival & First Exploration",
        "Culture & Heritage Day",
        "Food & Shopping Day",
        "Nature & Adventure",
        "Local Experiences",
        "Leisure & Relaxation",
        "Final Exploration & Departure",
    ]
    meals_rotation = [
        ["Breakfast at hotel", "Lunch at local restaurant", "Dinner at city favourite"],
        ["Hotel breakfast", "Street food lunch", "Rooftop dinner"],
        ["Café breakfast", "Traditional local lunch", "Seafood/specialty dinner"],
        ["Early breakfast", "Packed lunch on tour", "Welcome back dinner"],
        ["Buffet breakfast", "Quick bites at market", "Fine dining experience"],
    ]

    for day_num in range(1, duration_days + 1):
        if city_acts and (day_num - 1) < len(city_acts):
            raw_acts = city_acts[day_num - 1]
        else:
            raw_acts = _get_generic_activities(destination, day_num)

        # Last day special
        if day_num == duration_days and duration_days > 1:
            raw_acts = [
                ("09:00 AM", "Souvenir shopping", f"Market, {destination}", 800),
                ("11:30 AM", "Final breakfast at favourite cafe",
                 f"Cafe, {destination}", 300),
                ("01:00 PM", "Checkout and luggage drop", "Hotel", 0),
                ("03:00 PM", "Transfer to airport / station",
                 f"Airport, {destination}", 500),
            ]

        plan = _activities_to_plan(raw_acts, destination, converter, local_currency, is_domestic)
        title_idx = (day_num - 1) % len(day_titles)

        days.append(DayItinerary(
            day           = day_num,
            date_note     = f"Day {day_num} — {day_titles[title_idx]}",
            plan          = plan,
            meals         = meals_rotation[(day_num - 1) % len(meals_rotation)],
            accommodation = f"Your Hotel, {destination.title()}",
        ))
    return days


def itinerary_planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Itinerary Planner - always returns complete day-wise itinerary."""
    logger.info("[Node: Itinerary Planner] Starting")

    destination_info = state.get("destination_info")
    currency_info    = state.get("currency_info")
    duration_days    = int(state.get("duration_days", 5))
    interests        = state.get("interests", [])
    budget_breakdown = state.get("budget_breakdown")
    budget_inr       = float(state.get("budget_inr", 50000))

    destination    = destination_info.destination if destination_info else state.get("destination_query", "")
    is_domestic    = destination_info.is_domestic if destination_info else True
    local_currency = currency_info.local if currency_info else "INR"
    converter      = get_currency_converter()

    activity_budget = (budget_breakdown.activities.inr
                       if budget_breakdown and budget_breakdown.activities.inr > 0
                       else budget_inr * 0.12)
    per_day_activity = activity_budget / max(duration_days, 1)

    # ── Try LLM first ───────────────────────────────────────────────
    itinerary = []
    try:
        from tools.tavily_search import get_tavily_tool
        from llm.groq_client import get_groq_client

        tavily = get_tavily_tool()
        groq   = get_groq_client()

        activity_results = tavily.search_activities(destination, interests)
        context_parts    = []
        for r in activity_results[:3]:
            if r.get("content"):
                context_parts.append(r["content"][:500])
        context = "\n".join(context_parts)

        SYSTEM = f"""Create a {duration_days}-day itinerary and return ONLY this JSON (no markdown):
{{
  "itinerary": [
    {{
      "day": 1,
      "date_note": "Day 1 - Arrival",
      "accommodation": "hotel name",
      "meals": ["Breakfast at hotel","Local lunch","Dinner"],
      "plan": [
        {{
          "time": "09:00 AM",
          "activity": "Visit famous attraction",
          "place": "Place Name",
          "place_link": "https://www.google.com/maps/search/Place+Name+{destination.replace(' ', '+')}",
          "duration_hours": 2,
          "estimated_cost_inr": 200
        }}
      ]
    }}
  ]
}}
Include exactly {duration_days} days with 4-5 activities each.
All estimated_cost_inr must be numbers."""

        result = groq.invoke_json(SYSTEM,
            f"Destination: {destination}\n"
            f"Duration: {duration_days} days\n"
            f"Interests: {', '.join(interests) if interests else 'general tourism'}\n"
            f"Activity budget per day: {per_day_activity:.0f} INR\n"
            f"Attractions data:\n{context}")

        raw_days = result.get("itinerary", []) if result else []

        for day_dict in raw_days[:duration_days]:
            plan = []
            for act in day_dict.get("plan", []):
                cost_inr = float(act.get("estimated_cost_inr") or 0)
                conv     = converter.get_full_conversion(cost_inr, local_currency, is_domestic)
                place    = act.get("place") or destination
                link     = (act.get("place_link") or
                            f"https://www.google.com/maps/search/{place.replace(' ', '+')}")
                plan.append(ItineraryActivity(
                    time           = act.get("time") or "09:00 AM",
                    activity       = act.get("activity") or "Explore the area",
                    place          = place,
                    place_link     = link,
                    estimated_cost = MultiCurrencyAmount(**conv),
                    duration_hours = float(act.get("duration_hours") or 1.5),
                ))

            if plan:
                itinerary.append(DayItinerary(
                    day           = day_dict.get("day", len(itinerary) + 1),
                    date_note     = day_dict.get("date_note", f"Day {len(itinerary)+1}"),
                    plan          = plan,
                    meals         = day_dict.get("meals", ["Breakfast", "Lunch", "Dinner"]),
                    accommodation = day_dict.get("accommodation", f"Hotel in {destination}"),
                ))

    except Exception as e:
        logger.warning(f"[Node: Itinerary Planner] LLM failed: {e}")

    # ── Ensure we have the right number of days ──────────────────────
    if len(itinerary) < duration_days:
        logger.info(
            f"[Node: Itinerary Planner] LLM gave {len(itinerary)} days, "
            f"filling {duration_days - len(itinerary)} with fallback"
        )
        fallback = _build_fallback_itinerary(
            destination, duration_days, converter, local_currency, is_domestic
        )
        # Fill missing days
        existing_days = {d.day for d in itinerary}
        for fb_day in fallback:
            if fb_day.day not in existing_days and len(itinerary) < duration_days:
                itinerary.append(fb_day)

        # Sort by day number
        itinerary.sort(key=lambda d: d.day)

    logger.info(f"[Node: Itinerary Planner] Returning {len(itinerary)} days")
    return {**state, "itinerary": itinerary,
            "current_node": "itinerary_planner_complete"}