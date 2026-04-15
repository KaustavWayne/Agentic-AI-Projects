"""
Weather Tool - Fetches real-time and forecast weather data
using OpenWeatherMap API for any travel destination.

Provides:
- Current weather conditions
- 5-day / 3-hour forecast
- Travel-specific weather advice
- UV index, humidity, wind speed

Free tier: 60 calls/minute, 1M calls/month
API Docs: https://openweathermap.org/api
"""

import os
import requests
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from utils.cache import cached
from utils.retry import with_retry
from utils.logger import logger
from dotenv import load_dotenv

load_dotenv()

# Weather condition codes mapped to emojis and descriptions
WEATHER_CONDITION_MAP = {
    # Thunderstorm
    range(200, 300): ("⛈️", "Thunderstorm"),
    # Drizzle
    range(300, 400): ("🌦️", "Drizzle"),
    # Rain
    range(500, 600): ("🌧️", "Rain"),
    # Snow
    range(600, 700): ("❄️", "Snow"),
    # Atmosphere (fog, mist, haze)
    range(700, 800): ("🌫️", "Haze/Fog"),
    # Clear
    range(800, 801): ("☀️", "Clear Sky"),
    # Clouds
    range(801, 900): ("⛅", "Cloudy"),
}

WIND_DIRECTION_MAP = {
    (0, 22.5): "N", (22.5, 67.5): "NE", (67.5, 112.5): "E",
    (112.5, 157.5): "SE", (157.5, 202.5): "S", (202.5, 247.5): "SW",
    (247.5, 292.5): "W", (292.5, 337.5): "NW", (337.5, 360): "N"
}


def get_weather_emoji(weather_code: int) -> Tuple[str, str]:
    """Get emoji and label for a weather condition code."""
    for code_range, (emoji, label) in WEATHER_CONDITION_MAP.items():
        if weather_code in code_range:
            return emoji, label
    return "🌡️", "Unknown"


def get_wind_direction(degrees: float) -> str:
    """Convert wind degrees to compass direction."""
    for (low, high), direction in WIND_DIRECTION_MAP.items():
        if low <= degrees < high:
            return direction
    return "N"


def celsius_to_fahrenheit(c: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return round(c * 9 / 5 + 32, 1)


class WeatherTool:
    """
    Fetches real-time weather data from OpenWeatherMap API.

    Endpoints used:
    - /weather   → Current weather
    - /forecast  → 5-day / 3-hour forecast
    - /uvi       → UV Index (if available)

    Falls back to Tavily-based weather search if API key not set.
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5"
    GEO_URL  = "http://api.openweathermap.org/geo/1.0"

    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self._has_valid_key = bool(
            self.api_key
            and self.api_key != "your_openweathermap_api_key_here"
        )
        if self._has_valid_key:
            logger.info("WeatherTool initialized with OpenWeatherMap API")
        else:
            logger.warning(
                "OPENWEATHER_API_KEY not set – weather will use Tavily fallback"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_weather(self, destination: str, country: str = "") -> Dict[str, Any]:
        """
        Master method: returns a unified weather dict for the destination.

        Returns a dict with keys:
            current, forecast, location, travel_advice, data_source
        """
        if self._has_valid_key:
            return self._get_from_openweather(destination, country)
        else:
            return self._get_fallback_weather(destination, country)

    # ------------------------------------------------------------------
    # OpenWeatherMap path
    # ------------------------------------------------------------------

    @with_retry(max_attempts=3, min_wait=1.0, max_wait=5.0)
    def _geocode(self, destination: str, country: str) -> Optional[Dict[str, float]]:
        """Resolve destination name → lat/lon using Geocoding API."""
        query = f"{destination},{country}" if country else destination
        url   = f"{self.GEO_URL}/direct"
        params = {"q": query, "limit": 1, "appid": self.api_key}

        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            # Retry with destination only
            params["q"] = destination
            resp = requests.get(url, params=params, timeout=8)
            resp.raise_for_status()
            data = resp.json()

        if data:
            return {
                "lat":      data[0]["lat"],
                "lon":      data[0]["lon"],
                "name":     data[0].get("name", destination),
                "country":  data[0].get("country", country),
            }
        return None

    @cached(ttl=1800, prefix="weather_current")   # 30-min cache
    @with_retry(max_attempts=3, min_wait=1.0, max_wait=5.0)
    def _fetch_current(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch current weather for lat/lon."""
        url    = f"{self.BASE_URL}/weather"
        params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
        resp   = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        return resp.json()

    @cached(ttl=3600, prefix="weather_forecast")  # 1-hour cache
    @with_retry(max_attempts=3, min_wait=1.0, max_wait=5.0)
    def _fetch_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch 5-day / 3-hour forecast for lat/lon."""
        url    = f"{self.BASE_URL}/forecast"
        params = {"lat": lat, "lon": lon, "appid": self.api_key,
                  "units": "metric", "cnt": 40}  # 40 × 3h = 5 days
        resp   = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        return resp.json()

    def _get_from_openweather(
        self, destination: str, country: str
    ) -> Dict[str, Any]:
        """Full pipeline: geocode → current + forecast → format."""
        try:
            geo = self._geocode(destination, country)
            if not geo:
                logger.warning(f"Geocoding failed for {destination}, using fallback")
                return self._get_fallback_weather(destination, country)

            lat, lon = geo["lat"], geo["lon"]
            current_raw  = self._fetch_current(lat, lon)
            forecast_raw = self._fetch_forecast(lat, lon)

            current  = self._parse_current(current_raw, geo)
            forecast = self._parse_forecast(forecast_raw)
            advice   = self._generate_travel_advice(current, forecast)

            logger.info(
                f"Weather fetched for {destination}: "
                f"{current['temperature_c']}°C, {current['condition']}"
            )

            return {
                "data_source": "openweathermap",
                "location":    {
                    "name":     geo["name"],
                    "country":  geo["country"],
                    "lat":      round(lat, 4),
                    "lon":      round(lon, 4),
                },
                "current":       current,
                "forecast":      forecast,
                "travel_advice": advice,
            }

        except Exception as e:
            logger.error(f"OpenWeatherMap error: {e}")
            return self._get_fallback_weather(destination, country)

    # ------------------------------------------------------------------
    # Parsers
    # ------------------------------------------------------------------

    def _parse_current(
        self, raw: Dict[str, Any], geo: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse current weather API response into clean dict."""
        weather    = raw.get("weather", [{}])[0]
        main       = raw.get("main", {})
        wind       = raw.get("wind", {})
        sys_data   = raw.get("sys", {})
        clouds     = raw.get("clouds", {})
        rain       = raw.get("rain", {})
        snow       = raw.get("snow", {})

        code  = weather.get("id", 800)
        emoji, condition_label = get_weather_emoji(code)

        temp_c  = round(main.get("temp", 0), 1)
        feels_c = round(main.get("feels_like", temp_c), 1)

        # Sunrise / Sunset (UTC → local string)
        sunrise_ts = sys_data.get("sunrise", 0)
        sunset_ts  = sys_data.get("sunset", 0)
        sunrise_str = datetime.utcfromtimestamp(sunrise_ts).strftime("%I:%M %p UTC") if sunrise_ts else "N/A"
        sunset_str  = datetime.utcfromtimestamp(sunset_ts).strftime("%I:%M %p UTC") if sunset_ts else "N/A"

        wind_speed_ms  = wind.get("speed", 0)
        wind_speed_kmh = round(wind_speed_ms * 3.6, 1)
        wind_dir_deg   = wind.get("deg", 0)
        wind_dir       = get_wind_direction(wind_dir_deg)

        return {
            "condition":        condition_label,
            "condition_detail": weather.get("description", "").title(),
            "emoji":            emoji,
            "temperature_c":    temp_c,
            "temperature_f":    celsius_to_fahrenheit(temp_c),
            "feels_like_c":     feels_c,
            "feels_like_f":     celsius_to_fahrenheit(feels_c),
            "humidity_pct":     main.get("humidity", 0),
            "pressure_hpa":     main.get("pressure", 1013),
            "visibility_km":    round(raw.get("visibility", 10000) / 1000, 1),
            "cloud_cover_pct":  clouds.get("all", 0),
            "wind_speed_kmh":   wind_speed_kmh,
            "wind_direction":   wind_dir,
            "rain_1h_mm":       rain.get("1h", 0),
            "snow_1h_mm":       snow.get("1h", 0),
            "sunrise":          sunrise_str,
            "sunset":           sunset_str,
            "uv_index":         None,   # requires separate endpoint
            "recorded_at":      datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        }

    def _parse_forecast(self, raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Collapse 3-hour slots into daily summaries (next 5 days).
        Returns list of daily dicts sorted by date.
        """
        daily: Dict[str, Dict] = {}

        for slot in raw.get("list", []):
            dt_str   = slot["dt_txt"]                   # "2025-07-04 09:00:00"
            date_key = dt_str.split(" ")[0]             # "2025-07-04"

            main    = slot.get("main", {})
            weather = slot.get("weather", [{}])[0]
            rain    = slot.get("rain", {}).get("3h", 0)
            snow    = slot.get("snow", {}).get("3h", 0)
            pop     = slot.get("pop", 0)                # probability of precipitation

            if date_key not in daily:
                daily[date_key] = {
                    "date":      date_key,
                    "temps_c":   [],
                    "humidity":  [],
                    "codes":     [],
                    "rain_mm":   0,
                    "snow_mm":   0,
                    "pop_max":   0,
                }

            d = daily[date_key]
            d["temps_c"].append(main.get("temp", 0))
            d["humidity"].append(main.get("humidity", 0))
            d["codes"].append(weather.get("id", 800))
            d["rain_mm"]  += rain
            d["snow_mm"]  += snow
            d["pop_max"]   = max(d["pop_max"], pop)

        # Summarise
        result = []
        for date_key in sorted(daily.keys())[:5]:
            d = daily[date_key]
            if not d["temps_c"]:
                continue

            # Most frequent weather code → representative
            from collections import Counter
            rep_code = Counter(d["codes"]).most_common(1)[0][0]
            emoji, condition = get_weather_emoji(rep_code)

            # Day-of-week label
            try:
                dt_obj  = datetime.strptime(date_key, "%Y-%m-%d")
                day_str = dt_obj.strftime("%A, %b %d")
            except ValueError:
                day_str = date_key

            result.append({
                "date":          date_key,
                "day_label":     day_str,
                "emoji":         emoji,
                "condition":     condition,
                "temp_max_c":    round(max(d["temps_c"]), 1),
                "temp_min_c":    round(min(d["temps_c"]), 1),
                "temp_max_f":    celsius_to_fahrenheit(max(d["temps_c"])),
                "temp_min_f":    celsius_to_fahrenheit(min(d["temps_c"])),
                "humidity_avg":  round(sum(d["humidity"]) / len(d["humidity"])),
                "rain_mm":       round(d["rain_mm"], 1),
                "snow_mm":       round(d["snow_mm"], 1),
                "precip_chance": round(d["pop_max"] * 100),
            })

        return result

    # ------------------------------------------------------------------
    # Travel advice generator
    # ------------------------------------------------------------------

    def _generate_travel_advice(
        self,
        current: Dict[str, Any],
        forecast: List[Dict[str, Any]],
    ) -> List[str]:
        """Generate context-aware travel tips based on weather data."""
        advice = []
        temp   = current["temperature_c"]
        humid  = current["humidity_pct"]
        cond   = current["condition"].lower()
        wind   = current["wind_speed_kmh"]

        # Temperature advice
        if temp >= 35:
            advice.append("🌡️ Extreme heat expected – carry water, sunscreen (SPF 50+), and a hat")
        elif temp >= 28:
            advice.append("☀️ Hot weather – light breathable clothing recommended; stay hydrated")
        elif temp >= 18:
            advice.append("🌤️ Pleasant temperatures – ideal for outdoor sightseeing")
        elif temp >= 8:
            advice.append("🧥 Cool weather – pack a jacket or light sweater")
        else:
            advice.append("🥶 Cold conditions – pack warm layers and thermal wear")

        # Humidity
        if humid > 80:
            advice.append("💧 High humidity – carry a small towel; mornings are the best time to explore")
        elif humid < 30:
            advice.append("🏜️ Very dry air – moisturise regularly and drink extra water")

        # Rain / Storm
        if "rain" in cond or "drizzle" in cond:
            advice.append("🌧️ Carry a compact umbrella or rain poncho")
        if "thunderstorm" in cond:
            advice.append("⛈️ Thunderstorms possible – avoid open areas and outdoor activities")
        if "snow" in cond:
            advice.append("❄️ Snow expected – wear waterproof boots and warm layers")

        # Wind
        if wind > 50:
            advice.append("💨 Strong winds – outdoor activities near water may be disrupted")
        elif wind > 30:
            advice.append("🌬️ Windy conditions – hold on to loose items when outdoors")

        # Forecast-based advice
        if forecast:
            rainy_days = sum(1 for d in forecast if d["rain_mm"] > 5)
            if rainy_days >= 3:
                advice.append(
                    f"🌦️ {rainy_days} of the next 5 days expect significant rain – "
                    "plan indoor activities as backup"
                )
            elif rainy_days >= 1:
                advice.append(
                    f"☔ Light rain expected on {rainy_days} day(s) – keep an umbrella handy"
                )

            max_temps = [d["temp_max_c"] for d in forecast]
            if max_temps and max(max_temps) >= 38:
                advice.append(
                    "🔥 Heat wave possible during your trip – schedule heavy activities before noon"
                )

        # Visibility
        if current.get("visibility_km", 10) < 2:
            advice.append("🌫️ Poor visibility – take care while driving; some tours may be affected")

        # UV note (static since free-tier doesn't bundle UV)
        if temp >= 25 and "clear" in cond:
            advice.append("🕶️ High UV likely on clear sunny days – wear sunglasses and apply sunscreen")

        if not advice:
            advice.append("✅ Weather looks good – enjoy your trip!")

        return advice

    # ------------------------------------------------------------------
    # Tavily Fallback
    # ------------------------------------------------------------------

    def _get_fallback_weather(
        self, destination: str, country: str
    ) -> Dict[str, Any]:
        """
        Fallback weather info using Tavily search + static seasonal estimates.
        Used when OpenWeatherMap API key is unavailable.
        """
        logger.info(f"Using Tavily fallback weather for {destination}")

        try:
            from tools.tavily_search import get_tavily_tool
            tavily  = get_tavily_tool()
            results = tavily.search(
                f"current weather {destination} {country} temperature humidity forecast today",
                max_results=3,
                search_depth="basic",
            )

            # Extract summary text
            summary = ""
            for r in results:
                if r.get("content"):
                    summary = r["content"][:400]
                    break

            # Attempt rough temp extraction from text
            import re
            temps = re.findall(r"(\d{1,2})\s*°?[Cc]", summary)
            avg_temp = int(temps[0]) if temps else self._seasonal_temp(destination)

            emoji, condition = get_weather_emoji(800 if avg_temp > 22 else 803)

            return {
                "data_source": "tavily_fallback",
                "location": {
                    "name":    destination,
                    "country": country,
                    "lat":     None,
                    "lon":     None,
                },
                "current": {
                    "condition":        condition,
                    "condition_detail": summary[:120] if summary else "Data from web search",
                    "emoji":            emoji,
                    "temperature_c":    avg_temp,
                    "temperature_f":    celsius_to_fahrenheit(avg_temp),
                    "feels_like_c":     avg_temp + 2,
                    "feels_like_f":     celsius_to_fahrenheit(avg_temp + 2),
                    "humidity_pct":     65,
                    "pressure_hpa":     1013,
                    "visibility_km":    10,
                    "cloud_cover_pct":  40,
                    "wind_speed_kmh":   15,
                    "wind_direction":   "N",
                    "rain_1h_mm":       0,
                    "snow_1h_mm":       0,
                    "sunrise":          "06:00 AM (approx)",
                    "sunset":           "06:30 PM (approx)",
                    "uv_index":         None,
                    "recorded_at":      datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
                },
                "forecast":      self._build_static_forecast(avg_temp),
                "travel_advice": [
                    f"🌐 Live weather data requires OPENWEATHER_API_KEY",
                    f"🌡️ Estimated temperature around {avg_temp}°C based on seasonal norms",
                    "☀️ Check local weather app before each outing",
                    "🧳 Pack layers to adapt to changing conditions",
                ],
            }

        except Exception as e:
            logger.error(f"Tavily weather fallback failed: {e}")
            return self._get_minimal_fallback(destination, country)

    def _seasonal_temp(self, destination: str) -> int:
        """Rough seasonal temperature estimate by keyword matching."""
        dest_lower = destination.lower()
        month = datetime.now().month

        tropical = ["thailand", "bali", "singapore", "malaysia", "maldives",
                    "goa", "kerala", "mumbai", "chennai", "indonesia"]
        cold     = ["iceland", "norway", "finland", "sweden", "alaska",
                    "canada", "russia", "kashmir", "shimla", "manali"]

        if any(k in dest_lower for k in tropical):
            return 30 if month in [3, 4, 5, 6, 7, 8] else 27
        elif any(k in dest_lower for k in cold):
            return -2 if month in [12, 1, 2] else 12
        else:
            # Temperate default
            seasonal = {1: 10, 2: 12, 3: 15, 4: 18, 5: 22, 6: 26,
                        7: 28, 8: 27, 9: 22, 10: 17, 11: 13, 12: 10}
            return seasonal.get(month, 20)

    def _build_static_forecast(self, base_temp: int) -> List[Dict[str, Any]]:
        """Build a plausible 5-day forecast around base temperature."""
        import random
        forecast = []
        for i in range(5):
            date    = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            day_lbl = (datetime.now() + timedelta(days=i)).strftime("%A, %b %d")
            var     = random.randint(-3, 4)
            t_max   = base_temp + var + 3
            t_min   = base_temp + var - 3
            emoji, cond = get_weather_emoji(800 if var > 0 else 803)

            forecast.append({
                "date":          date,
                "day_label":     day_lbl,
                "emoji":         emoji,
                "condition":     cond,
                "temp_max_c":    t_max,
                "temp_min_c":    t_min,
                "temp_max_f":    celsius_to_fahrenheit(t_max),
                "temp_min_f":    celsius_to_fahrenheit(t_min),
                "humidity_avg":  random.randint(55, 80),
                "rain_mm":       round(random.uniform(0, 5), 1),
                "snow_mm":       0,
                "precip_chance": random.randint(10, 40),
            })
        return forecast

    def _get_minimal_fallback(
        self, destination: str, country: str
    ) -> Dict[str, Any]:
        """Absolute last-resort fallback."""
        return {
            "data_source": "minimal_fallback",
            "location":    {"name": destination, "country": country,
                            "lat": None, "lon": None},
            "current": {
                "condition":        "Unavailable",
                "condition_detail": "Weather data could not be fetched",
                "emoji":            "🌡️",
                "temperature_c":    25,
                "temperature_f":    77,
                "feels_like_c":     26,
                "feels_like_f":     79,
                "humidity_pct":     60,
                "pressure_hpa":     1013,
                "visibility_km":    10,
                "cloud_cover_pct":  30,
                "wind_speed_kmh":   10,
                "wind_direction":   "N",
                "rain_1h_mm":       0,
                "snow_1h_mm":       0,
                "sunrise":          "N/A",
                "sunset":           "N/A",
                "uv_index":         None,
                "recorded_at":      datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            },
            "forecast":      self._build_static_forecast(25),
            "travel_advice": [
                "⚠️ Weather data unavailable – please check a local weather app",
                "🌡️ Pack for variable conditions",
            ],
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_weather_tool: Optional[WeatherTool] = None

def get_weather_tool() -> WeatherTool:
    """Return singleton WeatherTool instance."""
    global _weather_tool
    if _weather_tool is None:
        _weather_tool = WeatherTool()
    return _weather_tool