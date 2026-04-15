# Pydantic models for State and Schema

"""
Pydantic models for strict structured output validation.
All monetary values support multi-currency representation.
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
import json


class MultiCurrencyAmount(BaseModel):
    """Represents an amount in multiple currencies."""
    inr: float = Field(default=0.0, description="Amount in Indian Rupees")
    local: float = Field(default=0.0, description="Amount in local destination currency")
    usd: float = Field(default=0.0, description="Amount in US Dollars")

    @field_validator("inr", "local", "usd", mode="before")
    @classmethod
    def round_currency(cls, v):
        try:
            return round(float(v), 2)
        except (TypeError, ValueError):
            return 0.0


class CurrencyInfo(BaseModel):
    """Currency metadata for the trip."""
    base: str = Field(default="INR", description="Base currency always INR")
    local: str = Field(default="INR", description="Local destination currency code")
    usd: str = Field(default="USD", description="USD reference")
    exchange_rate_inr_to_local: float = Field(default=1.0)
    exchange_rate_inr_to_usd: float = Field(default=0.012)


class BudgetBreakdown(BaseModel):
    """Detailed budget breakdown across categories."""
    flights: MultiCurrencyAmount = Field(default_factory=MultiCurrencyAmount)
    hotels: MultiCurrencyAmount = Field(default_factory=MultiCurrencyAmount)
    food: MultiCurrencyAmount = Field(default_factory=MultiCurrencyAmount)
    activities: MultiCurrencyAmount = Field(default_factory=MultiCurrencyAmount)
    transport: MultiCurrencyAmount = Field(default_factory=MultiCurrencyAmount)


class HotelOption(BaseModel):
    """Individual hotel recommendation."""
    name: str = Field(default="", description="Hotel name")
    price_per_night: MultiCurrencyAmount = Field(default_factory=MultiCurrencyAmount)
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    location: str = Field(default="")
    booking_link: str = Field(default="")
    amenities: List[str] = Field(default_factory=list)
    image_url: str = Field(default="")

    @field_validator("rating", mode="before")
    @classmethod
    def validate_rating(cls, v):
        try:
            return min(5.0, max(0.0, float(v)))
        except (TypeError, ValueError):
            return 0.0


class ItineraryActivity(BaseModel):
    """Single activity in the itinerary."""
    time: str = Field(default="", description="Time slot e.g. 09:00 AM")
    activity: str = Field(default="", description="Activity description")
    place: str = Field(default="", description="Place name")
    place_link: str = Field(default="", description="Google Maps or search link")
    estimated_cost: Optional[MultiCurrencyAmount] = Field(default=None)
    duration_hours: float = Field(default=1.0)


class DayItinerary(BaseModel):
    """Day-wise itinerary plan."""
    day: int = Field(default=1, ge=1)
    date_note: str = Field(default="", description="Optional date note")
    plan: List[ItineraryActivity] = Field(default_factory=list)
    meals: List[str] = Field(default_factory=list)
    accommodation: str = Field(default="")


class TransportInfo(BaseModel):
    """Transport recommendations."""
    mode: str = Field(default="")
    provider: str = Field(default="")
    estimated_cost: MultiCurrencyAmount = Field(default_factory=MultiCurrencyAmount)
    duration: str = Field(default="")
    details: str = Field(default="")
    booking_link: str = Field(default="")


class DestinationInfo(BaseModel):
    """Destination research output."""
    destination: str = Field(default="")
    country: str = Field(default="")
    is_domestic: bool = Field(default=True)
    currency_code: str = Field(default="INR")
    weather: str = Field(default="")
    best_time_to_visit: str = Field(default="")
    highlights: List[str] = Field(default_factory=list)
    description: str = Field(default="")

# ── ADD these classes to models/trip_models.py ──────────────────────────────
# Insert them BEFORE the TripPlan class definition.

class WeatherCurrent(BaseModel):
    """Current weather conditions."""
    condition: str         = Field(default="Unknown")
    condition_detail: str  = Field(default="")
    emoji: str             = Field(default="🌡️")
    temperature_c: float   = Field(default=0.0)
    temperature_f: float   = Field(default=0.0)
    feels_like_c: float    = Field(default=0.0)
    feels_like_f: float    = Field(default=0.0)
    humidity_pct: int      = Field(default=0)
    pressure_hpa: int      = Field(default=1013)
    visibility_km: float   = Field(default=10.0)
    cloud_cover_pct: int   = Field(default=0)
    wind_speed_kmh: float  = Field(default=0.0)
    wind_direction: str    = Field(default="N")
    rain_1h_mm: float      = Field(default=0.0)
    snow_1h_mm: float      = Field(default=0.0)
    sunrise: str           = Field(default="N/A")
    sunset: str            = Field(default="N/A")
    uv_index: Optional[float] = Field(default=None)
    recorded_at: str       = Field(default="")


class WeatherForecastDay(BaseModel):
    """Single day weather forecast."""
    date: str          = Field(default="")
    day_label: str     = Field(default="")
    emoji: str         = Field(default="🌡️")
    condition: str     = Field(default="")
    temp_max_c: float  = Field(default=0.0)
    temp_min_c: float  = Field(default=0.0)
    temp_max_f: float  = Field(default=0.0)
    temp_min_f: float  = Field(default=0.0)
    humidity_avg: int  = Field(default=0)
    rain_mm: float     = Field(default=0.0)
    snow_mm: float     = Field(default=0.0)
    precip_chance: int = Field(default=0)


class WeatherLocation(BaseModel):
    """Geocoded location info."""
    name: str            = Field(default="")
    country: str         = Field(default="")
    lat: Optional[float] = Field(default=None)
    lon: Optional[float] = Field(default=None)


class WeatherInfo(BaseModel):
    """
    Complete weather information for the destination.
    Attached to TripPlan as an optional field.
    """
    data_source: str                  = Field(default="unknown")
    location: WeatherLocation         = Field(default_factory=WeatherLocation)
    current: WeatherCurrent           = Field(default_factory=WeatherCurrent)
    forecast: List[WeatherForecastDay]= Field(default_factory=list)
    travel_advice: List[str]          = Field(default_factory=list)


# ── Also UPDATE TripPlan to include weather ──────────────────────────────────
# In your TripPlan class, add this field:
#
#     weather: Optional[WeatherInfo] = Field(default=None)
#
# And update TripPlannerState with:
#
#     weather_info: Optional[WeatherInfo] = None


class TripPlan(BaseModel):
    """
    Master trip plan model - STRICT structured output.
    This is the final aggregated output returned to the user.
    """
    destination: str                         = Field(default="")
    country: str                             = Field(default="")
    is_domestic: bool                        = Field(default=True)
    currency: CurrencyInfo                   = Field(default_factory=CurrencyInfo)
    duration_days: int                       = Field(default=0, ge=0)
    budget: MultiCurrencyAmount              = Field(default_factory=MultiCurrencyAmount)
    budget_breakdown: BudgetBreakdown        = Field(default_factory=BudgetBreakdown)
    hotels: List[HotelOption]                = Field(default_factory=list)
    itinerary: List[DayItinerary]            = Field(default_factory=list)
    transport: List[TransportInfo]           = Field(default_factory=list)
    destination_info: DestinationInfo        = Field(default_factory=DestinationInfo)
    weather: Optional["WeatherInfo"]         = Field(default=None)   # ← NEW
    tips: List[str]                          = Field(default_factory=list)
    generated_at: str                        = Field(default="")

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TripPlan":
        return cls.model_validate(data)


class TripPlannerState(BaseModel):
    """LangGraph state object."""
    destination_query: str      = Field(default="")
    budget_inr: float           = Field(default=0.0)
    duration_days: int          = Field(default=0)
    interests: List[str]        = Field(default_factory=list)
    travel_style: str           = Field(default="budget")

    destination_info: Optional[DestinationInfo]  = None
    currency_info: Optional[CurrencyInfo]         = None
    budget_breakdown: Optional[BudgetBreakdown]   = None
    hotels: List[HotelOption]                     = Field(default_factory=list)
    itinerary: List[DayItinerary]                 = Field(default_factory=list)
    transport: List[TransportInfo]                = Field(default_factory=list)
    weather_info: Optional["WeatherInfo"]         = None   # ← NEW
    tips: List[str]                               = Field(default_factory=list)
    final_plan: Optional[TripPlan]                = None

    errors: List[str]  = Field(default_factory=list)
    current_node: str  = Field(default="")

    model_config = {"arbitrary_types_allowed": True}