"""
Streamlit App - Clean fixed version.
"""

import streamlit as st
import os
import time
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Trip Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.components import (
    inject_css, render_hero, render_success_banner,
    render_destination_info, render_currency_info,
    render_budget_overview, render_budget_chart,
    render_hotels_section, render_itinerary_section,
    render_weather_section, render_transport_section,
    render_tips_section, render_error, render_footer,
)
from graph.trip_graph import run_trip_planner
from utils.logger import logger


def check_api_keys():
    return [k for k in ["GROQ_API_KEY", "TAVILY_API_KEY"] if not os.getenv(k)]


def render_sidebar():
    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:14px 0 8px;">'
            '<div style="font-size:1.9rem;">🌍</div>'
            '<div style="font-size:1.1rem;font-weight:700;color:white;">Trip Planner</div>'
            '<div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">AI-Powered · Multi-Agent</div>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.12);margin:8px 0;">',
            unsafe_allow_html=True
        )

        st.markdown('<p style="color:white;font-weight:600;margin-bottom:2px;">📍 Destination</p>',
                    unsafe_allow_html=True)
        destination = st.text_input("dest", placeholder="e.g. Paris, Goa, Tokyo...",
                                    label_visibility="collapsed", key="dest_input")

        st.markdown('<p style="color:white;font-weight:600;margin:10px 0 2px;">💰 Budget (INR)</p>',
                    unsafe_allow_html=True)
        budget_inr = st.number_input("budget", min_value=10_000, max_value=2_000_000,
                                     value=150_000, step=10_000, format="%d",
                                     label_visibility="collapsed", key="budget_input")
        st.markdown(
            f'<div style="background:rgba(255,193,7,0.18);border:1px solid rgba(255,193,7,0.35);'
            f'border-radius:7px;padding:5px 10px;text-align:center;'
            f'font-size:0.85rem;color:#ffc107;margin:3px 0;">₹{budget_inr:,} INR</div>',
            unsafe_allow_html=True
        )

        st.markdown('<p style="color:white;font-weight:600;margin:10px 0 2px;">📅 Duration (days)</p>',
                    unsafe_allow_html=True)
        duration_days = st.slider("dur", min_value=1, max_value=30, value=7,
                                  label_visibility="collapsed", key="dur_input")
        st.markdown(
            f'<div style="text-align:center;color:rgba(255,255,255,0.55);font-size:0.85rem;">'
            f'{duration_days} days</div>',
            unsafe_allow_html=True
        )

        st.markdown('<p style="color:white;font-weight:600;margin:10px 0 2px;">🎯 Travel Style</p>',
                    unsafe_allow_html=True)
        travel_style = st.selectbox("style",
                                    options=["budget", "mid-range", "luxury"],
                                    index=1,
                                    format_func=lambda x: {"budget":"🎒 Budget",
                                                            "mid-range":"✈️ Mid-Range",
                                                            "luxury":"💎 Luxury"}[x],
                                    label_visibility="collapsed", key="style_input")

        st.markdown('<p style="color:white;font-weight:600;margin:10px 0 2px;">🎨 Interests</p>',
                    unsafe_allow_html=True)
        interests_opts = ["History & Culture", "Food & Cuisine", "Beaches", "Adventure",
                          "Shopping", "Nature", "Nightlife", "Photography",
                          "Wellness & Spa", "Local Experiences"]
        selected = st.multiselect("interests", options=interests_opts,
                                  default=["Food & Cuisine", "History & Culture"],
                                  label_visibility="collapsed", key="interests_input")

        st.markdown(
            '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.12);margin:14px 0;">',
            unsafe_allow_html=True
        )
        plan_clicked = st.button("🚀 Plan My Trip", use_container_width=True, key="plan_btn")

        missing = check_api_keys()
        if missing:
            st.markdown(
                f'<div style="background:rgba(245,87,108,0.18);border:1px solid rgba(245,87,108,0.35);'
                f'border-radius:8px;padding:9px;margin-top:8px;">'
                f'<div style="color:#f5576c;font-size:0.8rem;font-weight:600;">⚠️ Missing keys</div>'
                f'<div style="color:rgba(255,255,255,0.6);font-size:0.75rem;">{", ".join(missing)}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div style="background:rgba(0,242,254,0.10);border:1px solid rgba(0,242,254,0.22);'
                'border-radius:7px;padding:7px;margin-top:8px;text-align:center;'
                'font-size:0.75rem;color:rgba(255,255,255,0.5);">✅ API keys ready</div>',
                unsafe_allow_html=True
            )

    return {
        "destination":   destination,
        "budget_inr":    budget_inr,
        "duration_days": duration_days,
        "travel_style":  travel_style,
        "interests":     selected,
        "plan_clicked":  plan_clicked,
    }


def show_planning_ui(config: dict):
    """Show progress bar and run the planner synchronously."""
    steps = [
        "🔍 Researching destination...",
        "💱 Setting up currency conversion...",
        "🌤️ Fetching weather data...",
        "💰 Planning budget breakdown...",
        "🏨 Finding best hotels...",
        "📅 Building day-wise itinerary...",
        "✈️ Finding transport options...",
        "🔄 Aggregating final plan...",
    ]

    st.markdown(
        '<div style="text-align:center;padding:28px 0 16px;">'
        '<div style="font-size:2.8rem;">✈️</div>'
        '<div style="font-size:1.3rem;font-weight:700;color:white;margin-top:12px;">'
        'Planning Your Dream Trip…</div>'
        '<div style="color:rgba(255,255,255,0.5);margin-top:5px;font-size:0.88rem;">'
        'AI agents collaborating — this takes 30-90 seconds</div>'
        '</div>',
        unsafe_allow_html=True
    )

    progress_bar  = st.progress(0)
    status_holder = st.empty()

    # Animate steps cosmetically while we wait
    for i, step in enumerate(steps[:-1]):
        progress_bar.progress((i + 1) / len(steps))
        status_holder.markdown(
            f'<div style="text-align:center;color:rgba(255,255,255,0.7);'
            f'font-size:0.9rem;padding:5px;">{step}</div>',
            unsafe_allow_html=True
        )
        time.sleep(0.2)

    status_holder.markdown(
        '<div style="text-align:center;color:rgba(255,255,255,0.7);'
        'font-size:0.9rem;padding:5px;">⏳ AI agents working…</div>',
        unsafe_allow_html=True
    )

    # ── Run synchronously (no threading — fixes state loss bug) ─────
    result = run_trip_planner(
        destination   = config["destination"],
        budget_inr    = config["budget_inr"],
        duration_days = config["duration_days"],
        interests     = config["interests"],
        travel_style  = config["travel_style"],
    )

    progress_bar.progress(1.0)
    status_holder.empty()

    return result


def render_plan(plan):
    """Render the complete trip plan."""
    from models.trip_models import TripPlan

    render_success_banner(plan)

    # Download
    col_dl, _ = st.columns([1, 4])
    with col_dl:
        st.download_button(
            "⬇️ Download JSON", plan.to_json(),
            file_name=f"trip_{plan.destination.lower().replace(' ','_')}.json",
            mime="application/json"
        )

    st.markdown(
        '<hr style="border:none;border-top:2px solid rgba(240,147,251,0.4);margin:20px 0;">',
        unsafe_allow_html=True
    )

    # 1. Destination
    render_destination_info(plan)
    render_currency_info(plan)

    # 2. Weather
    if plan.weather:
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.1);margin:20px 0;">',
                    unsafe_allow_html=True)
        render_weather_section(plan)

    # 3. Budget
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.1);margin:20px 0;">',
                unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:1.5rem;font-weight:700;color:white;margin-bottom:14px;">💰 Budget Overview</div>',
        unsafe_allow_html=True
    )
    render_budget_overview(plan)

    col_chart, col_stats = st.columns([1.3, 1])
    with col_chart:
        render_budget_chart(plan)
    with col_stats:
        bd      = plan.budget_breakdown
        per_day = plan.budget.inr / max(plan.duration_days, 1)
        for icon, label, val in [
            ("📊", "Per Day Budget",  f"₹{per_day:,.0f}"),
            ("✈️", "Flight Budget",   f"₹{bd.flights.inr:,.0f}"),
            ("🏨", "Hotel Budget",    f"₹{bd.hotels.inr:,.0f}"),
            ("🍜", "Food Budget",     f"₹{bd.food.inr:,.0f}"),
            ("🎭", "Activity Budget", f"₹{bd.activities.inr:,.0f}"),
        ]:
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.07);border-radius:9px;'
                f'padding:11px 14px;margin-bottom:7px;">'
                f'<div style="font-size:0.72rem;color:rgba(255,255,255,0.42);">{icon} {label}</div>'
                f'<div style="font-size:1.05rem;font-weight:700;color:white;">{val}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    # 4. Hotels
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.1);margin:20px 0;">',
                unsafe_allow_html=True)
    render_hotels_section(plan)

    # 5. Itinerary
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.1);margin:20px 0;">',
                unsafe_allow_html=True)
    render_itinerary_section(plan)

    # 6. Transport
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.1);margin:20px 0;">',
                unsafe_allow_html=True)
    render_transport_section(plan)

    # 7. Tips
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.1);margin:20px 0;">',
                unsafe_allow_html=True)
    render_tips_section(plan)

    # 8. Raw JSON
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.1);margin:20px 0;">',
                unsafe_allow_html=True)
    with st.expander("🔧 Raw JSON Output", expanded=False):
        st.code(plan.to_json(), language="json")


def main():
    inject_css()
    render_hero()

    # Session state
    if "trip_plan" not in st.session_state:
        st.session_state.trip_plan = None
    if "error_msg" not in st.session_state:
        st.session_state.error_msg = None

    config = render_sidebar()

    # Plan button
    if config["plan_clicked"]:
        if not config["destination"].strip():
            st.warning("⚠️ Please enter a destination first!")
            st.stop()
        if check_api_keys():
            st.error(f"❌ Missing API keys: {', '.join(check_api_keys())}")
            st.stop()

        st.session_state.trip_plan = None
        st.session_state.error_msg = None

        result = show_planning_ui(config)

        if result["success"] and result["plan"]:
            st.session_state.trip_plan = result["plan"]
            logger.info("Plan stored in session state successfully")
        else:
            err = "; ".join(result.get("errors", ["Unknown error"]))
            st.session_state.error_msg = err
            logger.error(f"Planning failed: {err}")

        st.rerun()

    # Error
    if st.session_state.error_msg:
        render_error(st.session_state.error_msg)
        if st.button("🔄 Try Again"):
            st.session_state.error_msg = None
            st.rerun()
        render_footer()
        return

    # Show plan
    if st.session_state.trip_plan:
        render_plan(st.session_state.trip_plan)
    else:
        # Welcome
        st.markdown(
            '<div style="text-align:center;padding:60px 20px;">'
            '<div style="font-size:4.5rem;margin-bottom:16px;">✈️</div>'
            '<div style="font-size:1.65rem;font-weight:700;color:white;margin-bottom:8px;">'
            'Ready to Plan Your Journey?</div>'
            '<div style="font-size:0.92rem;color:rgba(255,255,255,0.5);max-width:460px;margin:0 auto;">'
            'Enter destination, budget and preferences in the sidebar, then click Plan My Trip.'
            '</div></div>',
            unsafe_allow_html=True
        )

        c1, c2, c3, c4 = st.columns(4)
        for col, icon, title, desc in [
            (c1, "🤖", "Multi-Agent AI",  "8 LangGraph agents"),
            (c2, "💱", "Live Currency",    "INR + Local + USD"),
            (c3, "🌤️", "Real Weather",   "OpenWeatherMap live"),
            (c4, "📊", "Validated JSON",  "Pydantic structured"),
        ]:
            with col:
                st.markdown(
                    f'<div style="background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);'
                    f'border-radius:14px;padding:20px;text-align:center;">'
                    f'<div style="font-size:2rem;">{icon}</div>'
                    f'<div style="font-weight:600;color:white;margin:8px 0 4px;">{title}</div>'
                    f'<div style="font-size:0.76rem;color:rgba(255,255,255,0.42);">{desc}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    render_footer()


if __name__ == "__main__":
    main()