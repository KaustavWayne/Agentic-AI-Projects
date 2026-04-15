# Entry point for the CLI application 

"""
Main entry point for the AI Trip Planner.
Can be run directly for CLI testing or imported by Streamlit app.
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from graph.trip_graph import run_trip_planner
from utils.logger import logger


def main():
    """CLI entry point for testing the trip planner."""
    
    print("\n" + "="*60)
    print("🌍 AI Trip Planner - Powered by LangGraph + Groq")
    print("="*60 + "\n")
    
    # Validate environment
    required_env_vars = ["GROQ_API_KEY", "TAVILY_API_KEY"]
    missing = [v for v in required_env_vars if not os.getenv(v)]
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("Please set them in your .env file")
        sys.exit(1)
    
    # Example trip request
    trip_config = {
        "destination": "Bangkok, Thailand",
        "budget_inr": 150000,
        "duration_days": 7,
        "interests": ["temples", "street food", "shopping", "nightlife"],
        "travel_style": "mid-range"
    }
    
    print(f"📍 Planning trip to: {trip_config['destination']}")
    print(f"💰 Budget: ₹{trip_config['budget_inr']:,} INR")
    print(f"📅 Duration: {trip_config['duration_days']} days")
    print(f"🎯 Interests: {', '.join(trip_config['interests'])}")
    print(f"✈️  Style: {trip_config['travel_style']}")
    print("\n⏳ Planning your trip... This may take 1-2 minutes.\n")
    
    result = run_trip_planner(**trip_config)
    
    if result["success"] and result["plan"]:
        plan = result["plan"]
        
        print("\n" + "="*60)
        print("✅ TRIP PLAN GENERATED SUCCESSFULLY!")
        print("="*60)
        
        print(f"\n📍 Destination: {plan.destination}, {plan.country}")
        print(f"💱 Currency: {plan.currency.local} (Local) | USD")
        print(f"💰 Budget: ₹{plan.budget.inr:,.0f} | {plan.currency.local} {plan.budget.local:,.2f} | ${plan.budget.usd:,.2f}")
        
        print(f"\n🏨 Hotels Found: {len(plan.hotels)}")
        for hotel in plan.hotels[:2]:
            print(f"  • {hotel.name} - ₹{hotel.price_per_night.inr:,.0f}/night (Rating: {hotel.rating}⭐)")
        
        print(f"\n📅 Itinerary: {len(plan.itinerary)} days planned")
        for day in plan.itinerary[:2]:
            print(f"  Day {day.day}: {day.date_note}")
            for act in day.plan[:2]:
                print(f"    {act.time} - {act.activity}")
        
        print(f"\n✈️  Transport Options: {len(plan.transport)}")
        for t in plan.transport[:2]:
            print(f"  • {t.mode}: ₹{t.estimated_cost.inr:,.0f} ({t.duration})")
        
        # Save JSON output
        output_path = Path("trip_plan_output.json")
        with open(output_path, "w") as f:
            f.write(plan.to_json())
        
        print(f"\n💾 Full JSON saved to: {output_path}")
        
        if result["errors"]:
            print(f"\n⚠️  Warnings ({len(result['errors'])}): {'; '.join(result['errors'][:3])}")
    
    else:
        print("\n❌ Trip planning failed!")
        for error in result.get("errors", []):
            print(f"  Error: {error}")


if __name__ == "__main__":
    main()