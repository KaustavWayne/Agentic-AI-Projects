# Currency API tool 

"""
Currency Converter Tool - Converts INR to local destination currency and USD.
Uses Exchange Rate API with fallback rates and caching.
"""

import os
import requests
from typing import Dict, Optional, Tuple
from utils.cache import cached
from utils.retry import with_retry
from utils.logger import logger
from dotenv import load_dotenv

load_dotenv()

# Fallback exchange rates (INR base) - updated periodically
FALLBACK_RATES_FROM_INR = {
    "USD": 0.01200,
    "EUR": 0.01110,
    "GBP": 0.00950,
    "JPY": 1.79000,
    "AUD": 0.01850,
    "CAD": 0.01640,
    "SGD": 0.01620,
    "AED": 0.04400,
    "THB": 0.43000,
    "MYR": 0.05600,
    "IDR": 196.00000,
    "PHP": 0.70000,
    "VND": 305.00000,
    "KRW": 16.50000,
    "CNY": 0.08700,
    "HKD": 0.09400,
    "NZD": 0.02000,
    "CHF": 0.01080,
    "SEK": 0.12900,
    "NOK": 0.13200,
    "DKK": 0.08300,
    "ZAR": 0.22600,
    "BRL": 0.06200,
    "MXN": 0.20500,
    "TRY": 0.39000,
    "RUB": 1.11000,
    "INR": 1.00000,
    "NPR": 1.60000,
    "LKR": 3.72000,
    "BDT": 1.32000,
    "PKR": 3.33000,
    "MMK": 25.20000,
    "KHR": 49.00000,
    "LAK": 263.00000,
    "BND": 0.01620,
    "MVR": 0.18500,
    "BTN": 1.00000,
    "AFN": 0.86000,
    "QAR": 0.04370,
    "SAR": 0.04500,
    "KWD": 0.00369,
    "BHD": 0.00453,
    "OMR": 0.00462,
    "JOD": 0.00851,
    "EGP": 0.58500,
    "MAD": 0.12300,
    "TND": 0.03800,
    "GHS": 0.18000,
    "NGN": 19.20000,
    "KES": 1.55000,
    "TZS": 31.20000,
    "ETB": 1.38000,
    "XOF": 7.29000,
    "MZN": 0.76800,
    "ZMW": 0.32900,
}

# Country to currency code mapping
COUNTRY_CURRENCY_MAP = {
    "india": "INR",
    "united states": "USD",
    "usa": "USD",
    "uk": "GBP",
    "united kingdom": "GBP",
    "france": "EUR",
    "germany": "EUR",
    "italy": "EUR",
    "spain": "EUR",
    "japan": "JPY",
    "australia": "AUD",
    "canada": "CAD",
    "singapore": "SGD",
    "dubai": "AED",
    "uae": "AED",
    "united arab emirates": "AED",
    "thailand": "THB",
    "malaysia": "MYR",
    "indonesia": "IDR",
    "bali": "IDR",
    "philippines": "PHP",
    "vietnam": "VND",
    "south korea": "KRW",
    "korea": "KRW",
    "china": "CNY",
    "hong kong": "HKD",
    "new zealand": "NZD",
    "switzerland": "CHF",
    "sweden": "SEK",
    "norway": "NOK",
    "denmark": "DKK",
    "south africa": "ZAR",
    "brazil": "BRL",
    "mexico": "MXN",
    "turkey": "TRY",
    "russia": "RUB",
    "nepal": "NPR",
    "sri lanka": "LKR",
    "bangladesh": "BDT",
    "maldives": "MVR",
    "bhutan": "BTN",
    "myanmar": "MMK",
    "cambodia": "KHR",
    "laos": "LAK",
    "brunei": "BND",
    "qatar": "QAR",
    "saudi arabia": "SAR",
    "kuwait": "KWD",
    "bahrain": "BHD",
    "oman": "OMR",
    "jordan": "JOD",
    "egypt": "EGP",
    "morocco": "MAD",
    "greece": "EUR",
    "portugal": "EUR",
    "netherlands": "EUR",
    "belgium": "EUR",
    "austria": "EUR",
    "poland": "EUR",
    "czech republic": "EUR",
    "hungary": "EUR",
    "croatia": "EUR",
    "iceland": "EUR",
    "ireland": "EUR",
    "finland": "EUR",
    "israel": "USD",
    "kenya": "KES",
    "tanzania": "TZS",
    "ethiopia": "ETB",
    "nigeria": "NGN",
    "ghana": "GHS",
    "peru": "USD",
    "colombia": "USD",
    "argentina": "USD",
    "chile": "USD",
    "cuba": "USD",
    "costa rica": "USD",
    "panama": "USD",
}


class CurrencyConverter:
    """
    Converts currencies using Exchange Rate API with fallback to static rates.
    Implements caching and retry for production reliability.
    """

    def __init__(self):
        self.api_key = os.getenv("EXCHANGE_API_KEY", "")
        self.base_url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/INR"
        self._rates_cache: Dict[str, float] = {}
        logger.info("CurrencyConverter initialized")

    @cached(ttl=3600, prefix="exchange_rates")
    @with_retry(max_attempts=3, min_wait=1.0, max_wait=5.0)
    def _fetch_live_rates(self) -> Dict[str, float]:
        """Fetch live exchange rates from API."""
        if not self.api_key or self.api_key == "your_exchange_rate_api_key_here":
            logger.warning("No valid EXCHANGE_API_KEY - using fallback rates")
            return FALLBACK_RATES_FROM_INR

        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("result") == "success":
                rates = data.get("conversion_rates", {})
                logger.info(f"Fetched live rates for {len(rates)} currencies")
                return rates
            else:
                logger.warning(f"API returned non-success: {data.get('result')}")
                return FALLBACK_RATES_FROM_INR

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch exchange rates: {e}")
            return FALLBACK_RATES_FROM_INR

    def get_rates(self) -> Dict[str, float]:
        """Get exchange rates (live or cached or fallback)."""
        if not self._rates_cache:
            self._rates_cache = self._fetch_live_rates()
        return self._rates_cache

    def detect_currency(self, country: str, destination: str) -> str:
        """
        Detect local currency for a destination.
        
        Args:
            country: Country name
            destination: Destination/city name
            
        Returns:
            Currency code string
        """
        # Check country first, then destination
        lookup_keys = [
            country.lower().strip(),
            destination.lower().strip(),
        ]
        
        # Also check partial matches for destination
        for key in lookup_keys:
            if key in COUNTRY_CURRENCY_MAP:
                return COUNTRY_CURRENCY_MAP[key]
        
        # Partial match
        for key, currency in COUNTRY_CURRENCY_MAP.items():
            if key in country.lower() or key in destination.lower():
                return currency
        
        logger.warning(f"Could not detect currency for {country}/{destination}, defaulting to USD")
        return "USD"

    def is_domestic(self, country: str, destination: str) -> bool:
        """Check if destination is within India."""
        india_keywords = ["india", "indian", "goa", "kerala", "rajasthan", "kashmir",
                         "himachal", "uttarakhand", "maharashtra", "karnataka",
                         "tamil Nadu", "andhra", "telangana", "gujarat", "punjab",
                         "west bengal", "odisha", "jharkhand", "bihar", "up",
                         "mp", "chhattisgarh", "assam", "meghalaya", "sikkim",
                         "arunachal", "manipur", "nagaland", "tripura", "mizoram",
                         "delhi", "mumbai", "bangalore", "bengaluru", "chennai",
                         "kolkata", "hyderabad", "pune", "ahmedabad", "jaipur",
                         "agra", "varanasi", "amritsar", "kochi", "mysuru"]
        
        check_str = f"{country} {destination}".lower()
        return any(keyword in check_str for keyword in india_keywords)

    def inr_to_local(self, amount_inr: float, currency_code: str) -> float:
        """Convert INR to local currency."""
        if currency_code == "INR":
            return amount_inr
        
        rates = self.get_rates()
        rate = rates.get(currency_code, FALLBACK_RATES_FROM_INR.get(currency_code, 1.0))
        converted = amount_inr * rate
        return round(converted, 2)

    def inr_to_usd(self, amount_inr: float) -> float:
        """Convert INR to USD."""
        rates = self.get_rates()
        rate = rates.get("USD", FALLBACK_RATES_FROM_INR["USD"])
        return round(amount_inr * rate, 2)

    def get_full_conversion(
        self,
        amount_inr: float,
        local_currency: str,
        is_domestic: bool
    ) -> Dict[str, float]:
        """
        Get full currency conversion based on domestic/international logic.
        
        Returns dict with inr, local, usd values.
        """
        if is_domestic:
            return {
                "inr": round(amount_inr, 2),
                "local": round(amount_inr, 2),  # Same as INR for India
                "usd": self.inr_to_usd(amount_inr)
            }
        else:
            return {
                "inr": round(amount_inr, 2),
                "local": self.inr_to_local(amount_inr, local_currency),
                "usd": self.inr_to_usd(amount_inr)
            }

    def get_exchange_rates_info(
        self,
        local_currency: str
    ) -> Tuple[float, float]:
        """
        Get exchange rates for INR → local and INR → USD.
        Returns (inr_to_local_rate, inr_to_usd_rate)
        """
        rates = self.get_rates()
        inr_to_local = rates.get(local_currency, FALLBACK_RATES_FROM_INR.get(local_currency, 1.0))
        inr_to_usd = rates.get("USD", FALLBACK_RATES_FROM_INR["USD"])
        return inr_to_local, inr_to_usd


# Singleton instance
_converter = None

def get_currency_converter() -> CurrencyConverter:
    """Get singleton CurrencyConverter instance."""
    global _converter
    if _converter is None:
        _converter = CurrencyConverter()
    return _converter