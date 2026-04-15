"""
Destination Research Node - bulletproof version.
Uses Tavily + LLM with comprehensive hardcoded fallback database.
"""

from typing import Dict, Any, List
from models.trip_models import DestinationInfo
from tools.currency_converter import get_currency_converter
from utils.logger import logger
import json


# Hardcoded city database for instant fallback
CITY_DATABASE = {
    # Indian cities
    "kolkata": {"country": "India", "is_domestic": True, "currency": "INR",
                "weather": "Tropical - hot summers, mild winters",
                "best_time": "October to March",
                "highlights": ["Victoria Memorial", "Howrah Bridge", "Durga Puja Festival",
                               "Park Street food scene", "Sundarbans day trip"],
                "desc": "Kolkata, the cultural capital of India, is known for its colonial architecture, vibrant arts scene, and world-famous street food."},
    "mumbai": {"country": "India", "is_domestic": True, "currency": "INR",
               "weather": "Tropical - humid, heavy monsoons June-Sept",
               "best_time": "November to February",
               "highlights": ["Gateway of India", "Marine Drive", "Elephanta Caves",
                              "Bollywood studios", "Street food at Juhu Beach"],
               "desc": "Mumbai is India's financial capital and entertainment hub, offering a blend of colonial heritage, modern skyline, and vibrant street culture."},
    "delhi": {"country": "India", "is_domestic": True, "currency": "INR",
              "weather": "Extreme - hot summers, cold winters, pleasant spring/autumn",
              "best_time": "October to March",
              "highlights": ["Red Fort", "Qutub Minar", "India Gate", "Chandni Chowk", "Humayun's Tomb"],
              "desc": "Delhi, India's capital, is a city of contrasts blending Mughal history with modern governance and incredible street food."},
    "goa": {"country": "India", "is_domestic": True, "currency": "INR",
            "weather": "Tropical - sunny winters, heavy monsoons June-Sept",
            "best_time": "November to February",
            "highlights": ["Baga Beach", "Old Goa Churches", "Dudhsagar Falls",
                           "Spice Plantations", "Anjuna Flea Market"],
            "desc": "Goa is India's beach paradise, famous for its golden sands, Portuguese heritage, vibrant nightlife, and fresh seafood."},
    "jaipur": {"country": "India", "is_domestic": True, "currency": "INR",
               "weather": "Semi-arid - hot summers, mild winters",
               "best_time": "October to March",
               "highlights": ["Amber Fort", "Hawa Mahal", "City Palace", "Jantar Mantar", "Bazaar shopping"],
               "desc": "Jaipur, the Pink City, is a royal destination in Rajasthan known for its magnificent forts, palaces, and vibrant bazaars."},
    "kerala": {"country": "India", "is_domestic": True, "currency": "INR",
               "weather": "Tropical - warm year-round, monsoons June-August",
               "best_time": "September to March",
               "highlights": ["Alleppey Backwaters", "Munnar Tea Gardens", "Kovalam Beach",
                              "Periyar Wildlife", "Kathakali dance"],
               "desc": "Kerala, God's Own Country, enchants visitors with its serene backwaters, lush hill stations, and rich cultural traditions."},
    "agra": {"country": "India", "is_domestic": True, "currency": "INR",
             "weather": "Extreme - hot summers, cold winters",
             "best_time": "October to March",
             "highlights": ["Taj Mahal", "Agra Fort", "Fatehpur Sikri", "Mehtab Bagh", "Local handicrafts"],
             "desc": "Agra is home to the iconic Taj Mahal, one of the Seven Wonders of the World, and a treasure trove of Mughal architecture."},
    "bangalore": {"country": "India", "is_domestic": True, "currency": "INR",
                  "weather": "Pleasant year-round - mild temperatures",
                  "best_time": "October to February",
                  "highlights": ["Lalbagh Gardens", "Cubbon Park", "ISKCON Temple",
                                 "Tech parks", "Vibrant pub scene"],
                  "desc": "Bangalore is India's Silicon Valley, a modern cosmopolitan city with pleasant weather, gardens, and a thriving tech and food culture."},
    "hyderabad": {"country": "India", "is_domestic": True, "currency": "INR",
                  "weather": "Tropical - hot summers, mild winters",
                  "best_time": "October to February",
                  "highlights": ["Charminar", "Golconda Fort", "Ramoji Film City",
                                 "Biryani food trail", "Hussain Sagar Lake"],
                  "desc": "Hyderabad blends Nizami heritage with modern tech culture, famous for its biryani, pearls, and magnificent historical monuments."},
    "varanasi": {"country": "India", "is_domestic": True, "currency": "INR",
                 "weather": "Extreme - hot summers, cool winters",
                 "best_time": "October to March",
                 "highlights": ["Ganga Aarti", "Ghats of Varanasi", "Kashi Vishwanath Temple",
                                "Sarnath", "Silk weaving"],
                 "desc": "Varanasi is one of the world's oldest living cities, a spiritual heart of India where ancient rituals meet the sacred Ganges river."},
    "chennai": {"country": "India", "is_domestic": True, "currency": "INR",
                "weather": "Tropical - hot and humid, cyclones Oct-Dec",
                "best_time": "November to February",
                "highlights": ["Marina Beach", "Kapaleeshwarar Temple", "Mahabalipuram",
                               "Filter coffee culture", "Bharatanatyam performances"],
                "desc": "Chennai is the cultural gateway to South India, known for its classical arts, Dravidian temples, long coastline, and spicy cuisine."},
    "shimla": {"country": "India", "is_domestic": True, "currency": "INR",
               "weather": "Cool - snowy winters, pleasant summers",
               "best_time": "March to June, December for snow",
               "highlights": ["The Ridge", "Mall Road", "Jakhu Temple",
                              "Kufri snow point", "Toy Train"],
               "desc": "Shimla, the former summer capital of British India, is a charming hill station with colonial architecture and Himalayan vistas."},
    "manali": {"country": "India", "is_domestic": True, "currency": "INR",
               "weather": "Alpine - snowy winters, pleasant summers",
               "best_time": "October-June for snow, June-September for adventure",
               "highlights": ["Rohtang Pass", "Solang Valley", "Hadimba Temple",
                              "Old Manali cafes", "River rafting"],
               "desc": "Manali is a Himalayan adventure hub offering skiing, trekking, and breathtaking mountain scenery in Himachal Pradesh."},
    # International
    "bangkok": {"country": "Thailand", "is_domestic": False, "currency": "THB",
                "weather": "Tropical - hot and humid, monsoons May-Oct",
                "best_time": "November to February",
                "highlights": ["Grand Palace", "Wat Pho", "Chatuchak Market",
                               "Floating markets", "Khao San Road nightlife"],
                "desc": "Bangkok is Thailand's vibrant capital, a city of glittering temples, bustling street markets, world-class food, and electrifying nightlife."},
    "paris": {"country": "France", "is_domestic": False, "currency": "EUR",
              "weather": "Temperate - mild summers, cold winters",
              "best_time": "April to June, September to October",
              "highlights": ["Eiffel Tower", "Louvre Museum", "Champs-Élysées",
                             "Montmartre", "Seine River cruise"],
              "desc": "Paris, the City of Light, is the world's most romantic destination, celebrated for its art, cuisine, fashion, and iconic landmarks."},
    "dubai": {"country": "UAE", "is_domestic": False, "currency": "AED",
              "weather": "Desert - extremely hot summers, warm pleasant winters",
              "best_time": "November to March",
              "highlights": ["Burj Khalifa", "Dubai Mall", "Desert Safari",
                             "Palm Jumeirah", "Dubai Creek"],
              "desc": "Dubai is a futuristic desert metropolis combining record-breaking architecture, luxury shopping, and rich Emirati culture."},
    "singapore": {"country": "Singapore", "is_domestic": False, "currency": "SGD",
                  "weather": "Tropical - hot and humid year-round",
                  "best_time": "February to April",
                  "highlights": ["Marina Bay Sands", "Gardens by the Bay", "Sentosa Island",
                                 "Hawker food centres", "Universal Studios"],
                  "desc": "Singapore is a gleaming city-state known for its impeccable cleanliness, world-class food, futuristic gardens, and efficient living."},
    "tokyo": {"country": "Japan", "is_domestic": False, "currency": "JPY",
              "weather": "Temperate - hot summers, cold winters, cherry blossoms in spring",
              "best_time": "March-May and September-November",
              "highlights": ["Shibuya Crossing", "Senso-ji Temple", "Mount Fuji day trip",
                             "Akihabara electronics", "Tsukiji fish market"],
              "desc": "Tokyo is a mesmerising blend of ultramodern and traditional, from neon-lit skyscrapers to serene temples and world-renowned cuisine."},
    "bali": {"country": "Indonesia", "is_domestic": False, "currency": "IDR",
             "weather": "Tropical - dry season April-September, wet season Oct-March",
             "best_time": "April to October",
             "highlights": ["Ubud Rice Terraces", "Tanah Lot Temple", "Seminyak Beach",
                            "Mount Batur sunrise trek", "Monkey Forest"],
             "desc": "Bali is the Island of Gods, a tropical paradise offering stunning temples, terraced rice fields, surf beaches, and spiritual wellness retreats."},
    "london": {"country": "United Kingdom", "is_domestic": False, "currency": "GBP",
               "weather": "Temperate oceanic - mild, frequently rainy",
               "best_time": "June to August",
               "highlights": ["Big Ben & Westminster", "British Museum", "Tower of London",
                              "Buckingham Palace", "Notting Hill"],
               "desc": "London is a world-class metropolis blending royal heritage, world-renowned museums, diverse cuisine, and cutting-edge arts and culture."},
    "new york": {"country": "United States", "is_domestic": False, "currency": "USD",
                 "weather": "Humid continental - hot summers, cold snowy winters",
                 "best_time": "April-June and September-November",
                 "highlights": ["Times Square", "Central Park", "Statue of Liberty",
                                "Brooklyn Bridge", "Broadway shows"],
                 "desc": "New York City is the ultimate urban experience — a relentlessly exciting metropolis of art, culture, food, and architectural wonders."},
    "maldives": {"country": "Maldives", "is_domestic": False, "currency": "MVR",
                 "weather": "Tropical - warm year-round, dry season Nov-April",
                 "best_time": "November to April",
                 "highlights": ["Overwater bungalows", "Snorkelling & diving", "Sunset cruises",
                                "Bioluminescent beaches", "Whale shark spotting"],
                 "desc": "The Maldives is the ultimate luxury island escape, with crystal-clear lagoons, vibrant coral reefs, and iconic overwater villas."},
    "sri lanka": {"country": "Sri Lanka", "is_domestic": False, "currency": "LKR",
                  "weather": "Tropical - warm year-round, two monsoon seasons",
                  "best_time": "December to March for west coast",
                  "highlights": ["Sigiriya Rock Fortress", "Temple of the Tooth", "Tea plantations",
                                 "Yala National Park", "Mirissa whale watching"],
                  "desc": "Sri Lanka is the Pearl of the Indian Ocean, a compact island of ancient ruins, wildlife-rich jungles, pristine beaches, and world-famous Ceylon tea."},
    "nepal": {"country": "Nepal", "is_domestic": False, "currency": "NPR",
              "weather": "Varies by altitude - tropical lowlands to alpine peaks",
              "best_time": "October-November and March-May",
              "highlights": ["Everest Base Camp trek", "Kathmandu Durbar Square",
                             "Pokhara lakeside", "Chitwan wildlife safari", "Annapurna Circuit"],
              "desc": "Nepal is the rooftop of the world, home to eight of the ten highest peaks, ancient Hindu and Buddhist heritage, and legendary trekking routes."},
}


def _lookup_city(query: str) -> Dict[str, Any]:
    """Fast local city database lookup."""
    q = query.lower().strip()
    # Direct match
    if q in CITY_DATABASE:
        return CITY_DATABASE[q]
    # Partial match
    for key, data in CITY_DATABASE.items():
        if key in q or q in key:
            return data
    return {}


def destination_research_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 1: Destination Research
    Tries Tavily+LLM first, falls back to city database, then generic fallback.
    NEVER returns None for destination_info.
    """
    destination = state.get("destination_query", "")
    interests   = state.get("interests", [])
    logger.info(f"[Node: Destination Research] Query: '{destination}'")

    converter = get_currency_converter()

    # ── Step 1: Try local database first (instant, no API) ──────────
    db_match = _lookup_city(destination)

    if db_match:
        logger.info(f"[Node: Destination Research] Found in local DB: {destination}")
        destination_info = DestinationInfo(
            destination      = destination.title(),
            country          = db_match["country"],
            is_domestic      = db_match["is_domestic"],
            currency_code    = db_match["currency"],
            weather          = db_match["weather"],
            best_time_to_visit = db_match["best_time"],
            highlights       = db_match["highlights"],
            description      = db_match["desc"],
        )
        return {**state, "destination_info": destination_info,
                "current_node": "destination_research_complete"}

    # ── Step 2: Try Tavily + LLM ────────────────────────────────────
    try:
        from tools.tavily_search import get_tavily_tool
        from llm.groq_client import get_groq_client

        tavily = get_tavily_tool()
        groq   = get_groq_client()

        search_results = tavily.search_destination_info(destination, interests)
        context_parts  = []
        for r in search_results[:3]:
            if r.get("content"):
                context_parts.append(r["content"][:600])
        context = "\n---\n".join(context_parts) or f"Destination: {destination}"

        SYSTEM = """Extract destination info and return ONLY this JSON (no markdown):
{
  "destination": "city name",
  "country": "country name",
  "is_domestic": false,
  "currency_code": "THB",
  "weather": "brief weather",
  "best_time_to_visit": "months",
  "highlights": ["place1","place2","place3","place4","place5"],
  "description": "2 sentence description"
}
is_domestic = true ONLY if in India."""

        result = groq.invoke_json(SYSTEM,
                                  f"Destination: {destination}\nContext:\n{context}")

        if result and result.get("destination"):
            is_dom  = converter.is_domestic(result.get("country",""), destination)
            curr    = converter.detect_currency(result.get("country",""), destination)
            dest_info = DestinationInfo(
                destination        = result.get("destination", destination),
                country            = result.get("country", "Unknown"),
                is_domestic        = is_dom,
                currency_code      = curr,
                weather            = result.get("weather", "Varies by season"),
                best_time_to_visit = result.get("best_time_to_visit", "Year-round"),
                highlights         = result.get("highlights", []),
                description        = result.get("description", ""),
            )
            logger.info(f"[Node: Destination Research] LLM success: {dest_info.destination}")
            return {**state, "destination_info": dest_info,
                    "current_node": "destination_research_complete"}

    except Exception as e:
        logger.warning(f"[Node: Destination Research] Tavily/LLM failed: {e}")

    # ── Step 3: Generic smart fallback ──────────────────────────────
    logger.info(f"[Node: Destination Research] Using generic fallback for: {destination}")
    is_domestic = converter.is_domestic("", destination)
    currency    = converter.detect_currency("", destination)

    destination_info = DestinationInfo(
        destination        = destination.title(),
        country            = "India" if is_domestic else "International",
        is_domestic        = is_domestic,
        currency_code      = currency,
        weather            = "Pleasant climate suitable for tourism",
        best_time_to_visit = "October to March is generally ideal",
        highlights         = [
            f"Explore {destination} city centre",
            "Local cultural experiences",
            "Traditional cuisine and street food",
            "Historical monuments and museums",
            "Nature and scenic viewpoints",
        ],
        description = (
            f"{destination.title()} is a wonderful travel destination offering diverse "
            f"experiences in culture, cuisine, and sightseeing."
        ),
    )
    return {**state, "destination_info": destination_info,
            "current_node": "destination_research_complete"}