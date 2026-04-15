# Handle currency calculations 

"""
Currency Conversion Node - Converts all monetary values to multi-currency format.
Must run AFTER destination research and BEFORE budget planning completion.
"""

from typing import Dict, Any
from models.trip_models import TripPlannerState, CurrencyInfo
from tools.currency_converter import get_currency_converter
from utils.logger import logger


def currency_conversion_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node: Currency Conversion
    
    Reads destination info and sets up currency conversion context.
    All subsequent nodes use this for monetary conversions.
    
    Input state keys:
        - destination_info: DestinationInfo with country/currency details
        
    Output state keys:
        - currency_info: CurrencyInfo with rates and codes
    """
    logger.info("[Node: Currency Conversion] Starting currency setup")
    
    try:
        converter = get_currency_converter()
        destination_info = state.get("destination_info")
        
        if not destination_info:
            logger.warning("No destination info available, defaulting to INR")
            currency_info = CurrencyInfo(
                base="INR",
                local="INR",
                usd="USD",
                exchange_rate_inr_to_local=1.0,
                exchange_rate_inr_to_usd=0.012
            )
            return {
                **state,
                "currency_info": currency_info,
                "current_node": "currency_conversion_complete"
            }
        
        is_domestic = destination_info.is_domestic
        local_currency = destination_info.currency_code if not is_domestic else "INR"
        
        # Get exchange rates
        inr_to_local, inr_to_usd = converter.get_exchange_rates_info(local_currency)
        
        currency_info = CurrencyInfo(
            base="INR",
            local=local_currency,
            usd="USD",
            exchange_rate_inr_to_local=inr_to_local,
            exchange_rate_inr_to_usd=inr_to_usd
        )
        
        logger.info(
            f"[Node: Currency Conversion] Setup complete: "
            f"INR → {local_currency} @ {inr_to_local:.4f}, "
            f"INR → USD @ {inr_to_usd:.4f}"
        )
        
        return {
            **state,
            "currency_info": currency_info,
            "current_node": "currency_conversion_complete"
        }
        
    except Exception as e:
        logger.error(f"[Node: Currency Conversion] Error: {str(e)}")
        
        # Safe fallback
        currency_info = CurrencyInfo(
            base="INR",
            local="INR",
            usd="USD",
            exchange_rate_inr_to_local=1.0,
            exchange_rate_inr_to_usd=0.012
        )
        
        errors = state.get("errors", [])
        errors.append(f"Currency Conversion Error: {str(e)}")
        
        return {
            **state,
            "currency_info": currency_info,
            "errors": errors,
            "current_node": "currency_conversion_error"
        }