"""
LangGraph Trip Planner - Fixed state passing between nodes.
"""

from typing import TypedDict, List, Optional, Any, Dict
from langgraph.graph import StateGraph, END, START
from utils.logger import logger


class TripState(TypedDict, total=False):
    destination_query: str
    budget_inr: float
    duration_days: int
    interests: List[str]
    travel_style: str
    destination_info: Optional[Any]
    currency_info: Optional[Any]
    budget_breakdown: Optional[Any]
    hotels: List[Any]
    itinerary: List[Any]
    transport: List[Any]
    weather_info: Optional[Any]
    tips: List[str]
    final_plan: Optional[Any]
    errors: List[str]
    current_node: str


def run_destination_research(state: TripState) -> TripState:
    from nodes.destination_research import destination_research_node
    logger.info(f"[GRAPH] Running destination_research | dest={state.get('destination_query')}")
    result = destination_research_node(dict(state))
    logger.info(f"[GRAPH] destination_research done | dest_info={result.get('destination_info')}")
    return result


def run_currency_conversion(state: TripState) -> TripState:
    from nodes.currency_conversion import currency_conversion_node
    logger.info(f"[GRAPH] Running currency_conversion")
    result = currency_conversion_node(dict(state))
    logger.info(f"[GRAPH] currency done | currency_info={result.get('currency_info')}")
    return result


def run_weather(state: TripState) -> TripState:
    try:
        from nodes.weather_node import weather_node
        logger.info("[GRAPH] Running weather_node")
        result = weather_node(dict(state))
        logger.info(f"[GRAPH] weather done | has_weather={result.get('weather_info') is not None}")
        return result
    except Exception as e:
        logger.error(f"[GRAPH] weather_node crashed: {e}")
        return {**dict(state), "weather_info": None}


def run_budget_planner(state: TripState) -> TripState:
    from nodes.budget_planner import budget_planner_node
    logger.info(f"[GRAPH] Running budget_planner | budget_inr={state.get('budget_inr')}")
    result = budget_planner_node(dict(state))
    bd = result.get('budget_breakdown')
    if bd:
        logger.info(f"[GRAPH] budget done | flights={bd.flights.inr} hotels={bd.hotels.inr}")
    else:
        logger.error("[GRAPH] budget_breakdown is None after budget_planner!")
    return result


def run_hotel_finder(state: TripState) -> TripState:
    from nodes.hotel_finder import hotel_finder_node
    logger.info("[GRAPH] Running hotel_finder")
    result = hotel_finder_node(dict(state))
    logger.info(f"[GRAPH] hotel_finder done | hotels={len(result.get('hotels', []))}")
    return result


def run_itinerary_planner(state: TripState) -> TripState:
    from nodes.itinerary_planner import itinerary_planner_node
    logger.info("[GRAPH] Running itinerary_planner")
    result = itinerary_planner_node(dict(state))
    logger.info(f"[GRAPH] itinerary done | days={len(result.get('itinerary', []))}")
    return result


def run_transport(state: TripState) -> TripState:
    from nodes.transport_node import transport_node
    logger.info("[GRAPH] Running transport_node")
    result = transport_node(dict(state))
    logger.info(f"[GRAPH] transport done | options={len(result.get('transport', []))}")
    return result


def run_aggregator(state: TripState) -> TripState:
    from nodes.aggregator import aggregator_node
    logger.info("[GRAPH] Running aggregator")
    result = aggregator_node(dict(state))
    plan = result.get('final_plan')
    if plan:
        logger.info(f"[GRAPH] aggregator done | hotels={len(plan.hotels)} itinerary={len(plan.itinerary)}")
    else:
        logger.error("[GRAPH] final_plan is None after aggregator!")
    return result


def create_trip_planner_graph():
    graph = StateGraph(TripState)

    graph.add_node("destination_research", run_destination_research)
    graph.add_node("currency_conversion",  run_currency_conversion)
    graph.add_node("weather",              run_weather)
    graph.add_node("budget_planner",       run_budget_planner)
    graph.add_node("hotel_finder",         run_hotel_finder)
    graph.add_node("itinerary_planner",    run_itinerary_planner)
    graph.add_node("transport_planner",    run_transport)
    graph.add_node("aggregator",           run_aggregator)

    graph.add_edge(START,                  "destination_research")
    graph.add_edge("destination_research", "currency_conversion")
    graph.add_edge("currency_conversion",  "weather")
    graph.add_edge("weather",              "budget_planner")
    graph.add_edge("budget_planner",       "hotel_finder")
    graph.add_edge("hotel_finder",         "itinerary_planner")
    graph.add_edge("itinerary_planner",    "transport_planner")
    graph.add_edge("transport_planner",    "aggregator")
    graph.add_edge("aggregator",           END)

    return graph.compile()


def run_trip_planner(
    destination: str,
    budget_inr: float,
    duration_days: int,
    interests: List[str],
    travel_style: str = "mid-range",
) -> Dict[str, Any]:

    logger.info(f"[GRAPH] START | dest={destination} budget={budget_inr} days={duration_days}")

    initial: TripState = {
        "destination_query": destination,
        "budget_inr":        float(budget_inr),
        "duration_days":     int(duration_days),
        "interests":         interests or [],
        "travel_style":      travel_style,
        "hotels":            [],
        "itinerary":         [],
        "transport":         [],
        "weather_info":      None,
        "tips":              [],
        "errors":            [],
        "current_node":      "start",
    }

    try:
        graph        = create_trip_planner_graph()
        final_state  = graph.invoke(initial)
        plan         = final_state.get("final_plan")
        errors       = final_state.get("errors", [])

        logger.info(f"[GRAPH] COMPLETE | plan={'OK' if plan else 'NONE'} errors={errors}")

        if plan:
            logger.info(
                f"[GRAPH] Plan summary: dest={plan.destination} "
                f"hotels={len(plan.hotels)} itinerary={len(plan.itinerary)} "
                f"transport={len(plan.transport)}"
            )

        return {"success": bool(plan), "plan": plan, "errors": errors, "state": final_state}

    except Exception as e:
        logger.error(f"[GRAPH] CRASHED: {e}", exc_info=True)
        return {"success": False, "plan": None, "errors": [str(e)], "state": initial}