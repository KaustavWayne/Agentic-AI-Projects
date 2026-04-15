"""
Weather Node - Fetches real-time weather data for the travel destination.
Runs after destination_research so it knows the exact location.

Integrates:
- OpenWeatherMap API (live data)
- Tavily fallback (if no API key)
- Travel advice generation
"""

from typing import Dict, Any
from models.trip_models import WeatherInfo, WeatherCurrent, WeatherForecastDay, WeatherLocation
from tools.weather_tool import get_weather_tool
from utils.logger import logger


def weather_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node: Weather
    Fetches current weather + 5-day forecast for the destination.

    Input  state keys: destination_info
    Output state keys: weather_info
    """
    logger.info("[Node: Weather] Fetching weather data")

    try:
        destination_info = state.get("destination_info")

        # Resolve destination & country strings
        if destination_info:
            destination = destination_info.destination
            country     = destination_info.country
        else:
            destination = state.get("destination_query", "")
            country     = ""

        weather_tool = get_weather_tool()
        raw = weather_tool.get_weather(destination, country)

        # ── Parse into Pydantic models ────────────────────────────────────
        loc_raw = raw.get("location", {})
        location = WeatherLocation(
            name    = loc_raw.get("name", destination),
            country = loc_raw.get("country", country),
            lat     = loc_raw.get("lat"),
            lon     = loc_raw.get("lon"),
        )

        cur_raw = raw.get("current", {})
        current = WeatherCurrent(
            condition        = cur_raw.get("condition", "Unknown"),
            condition_detail = cur_raw.get("condition_detail", ""),
            emoji            = cur_raw.get("emoji", "🌡️"),
            temperature_c    = float(cur_raw.get("temperature_c", 0)),
            temperature_f    = float(cur_raw.get("temperature_f", 0)),
            feels_like_c     = float(cur_raw.get("feels_like_c", 0)),
            feels_like_f     = float(cur_raw.get("feels_like_f", 0)),
            humidity_pct     = int(cur_raw.get("humidity_pct", 0)),
            pressure_hpa     = int(cur_raw.get("pressure_hpa", 1013)),
            visibility_km    = float(cur_raw.get("visibility_km", 10)),
            cloud_cover_pct  = int(cur_raw.get("cloud_cover_pct", 0)),
            wind_speed_kmh   = float(cur_raw.get("wind_speed_kmh", 0)),
            wind_direction   = cur_raw.get("wind_direction", "N"),
            rain_1h_mm       = float(cur_raw.get("rain_1h_mm", 0)),
            snow_1h_mm       = float(cur_raw.get("snow_1h_mm", 0)),
            sunrise          = cur_raw.get("sunrise", "N/A"),
            sunset           = cur_raw.get("sunset", "N/A"),
            uv_index         = cur_raw.get("uv_index"),
            recorded_at      = cur_raw.get("recorded_at", ""),
        )

        forecast = []
        for day_raw in raw.get("forecast", []):
            forecast.append(WeatherForecastDay(
                date          = day_raw.get("date", ""),
                day_label     = day_raw.get("day_label", ""),
                emoji         = day_raw.get("emoji", "🌡️"),
                condition     = day_raw.get("condition", ""),
                temp_max_c    = float(day_raw.get("temp_max_c", 0)),
                temp_min_c    = float(day_raw.get("temp_min_c", 0)),
                temp_max_f    = float(day_raw.get("temp_max_f", 0)),
                temp_min_f    = float(day_raw.get("temp_min_f", 0)),
                humidity_avg  = int(day_raw.get("humidity_avg", 0)),
                rain_mm       = float(day_raw.get("rain_mm", 0)),
                snow_mm       = float(day_raw.get("snow_mm", 0)),
                precip_chance = int(day_raw.get("precip_chance", 0)),
            ))

        weather_info = WeatherInfo(
            data_source   = raw.get("data_source", "unknown"),
            location      = location,
            current       = current,
            forecast      = forecast,
            travel_advice = raw.get("travel_advice", []),
        )

        logger.info(
            f"[Node: Weather] Complete: {current.temperature_c}°C, "
            f"{current.condition}, {len(forecast)} forecast days"
        )

        return {
            **state,
            "weather_info": weather_info,
            "current_node": "weather_complete",
        }

    except Exception as e:
        logger.error(f"[Node: Weather] Error: {e}")

        # Safe minimal fallback so the graph never crashes here
        weather_info = WeatherInfo(
            data_source   = "error_fallback",
            travel_advice = ["⚠️ Weather data temporarily unavailable"],
        )

        errors = state.get("errors", [])
        errors.append(f"Weather Node Error: {str(e)}")

        return {
            **state,
            "weather_info": weather_info,
            "errors":       errors,
            "current_node": "weather_error",
        }