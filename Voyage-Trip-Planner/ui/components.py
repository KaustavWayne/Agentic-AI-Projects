"""
UI Components - Fixed: NO multiline HTML f-strings (causes raw HTML display).
Uses Streamlit native components + single-line safe HTML only.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Any, List


# ─────────────────────────────────────────────────────────────────────────────
# CSS - only static strings, no f-strings
# ─────────────────────────────────────────────────────────────────────────────

def inject_css():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    #MainMenu{visibility:hidden}footer{visibility:hidden}header{visibility:hidden}
    html,body,.stApp{font-family:'Inter',sans-serif}
    .stApp{background:linear-gradient(135deg,#0f0c29 0%,#302b63 50%,#24243e 100%);min-height:100vh}
    .block-container{padding-top:1rem!important;max-width:1200px}
    [data-testid="stSidebar"]{background:linear-gradient(180deg,#1a1a2e 0%,#16213e 100%)!important}
    [data-testid="stSidebar"] label,[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,[data-testid="stSidebar"] div{color:rgba(255,255,255,0.9)!important}
    [data-testid="stSidebar"] input[type="text"],[data-testid="stSidebar"] input[type="number"]{color:#111!important;background:#fff!important;border:2px solid rgba(102,126,234,0.6)!important;border-radius:8px!important}
    [data-testid="stSidebar"] input::placeholder{color:#999!important}
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div{background:rgba(255,255,255,0.12)!important;border:1px solid rgba(255,255,255,0.25)!important;border-radius:8px!important;color:white!important}
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] > div > div{background:rgba(255,255,255,0.10)!important;border:1px solid rgba(255,255,255,0.22)!important;border-radius:8px!important}
    .stApp .stMarkdown p{color:rgba(255,255,255,0.85)!important}
    h1,h2,h3{color:white!important}
    .stButton>button{background:linear-gradient(135deg,#667eea,#764ba2)!important;color:white!important;border:none!important;border-radius:12px!important;font-weight:600!important;width:100%!important}
    .stDownloadButton>button{background:rgba(255,255,255,0.1)!important;color:white!important;border:1px solid rgba(255,255,255,0.25)!important;border-radius:10px!important}
    .stProgress>div>div{background:linear-gradient(90deg,#667eea,#f093fb)!important;border-radius:4px!important}
    .stExpander{background:rgba(255,255,255,0.05)!important;border:1px solid rgba(255,255,255,0.12)!important;border-radius:14px!important}
    .stExpander summary p{color:white!important;font-weight:600!important}
    </style>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Safe HTML helpers - single-line only, values pre-escaped
# ─────────────────────────────────────────────────────────────────────────────

def _e(val) -> str:
    """Escape a value for safe HTML insertion."""
    return str(val).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _card(content_html: str, extra_style: str = "") -> None:
    """Render a glass card using a SINGLE-LINE html string."""
    style = ("background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.14);"
             "border-radius:18px;padding:20px;margin:10px 0;" + extra_style)
    st.markdown(f'<div style="{style}">{content_html}</div>', unsafe_allow_html=True)


def _box(content: str, bg: str = "rgba(255,255,255,0.07)",
         border: str = "rgba(255,255,255,0.13)",
         radius: str = "12px", padding: str = "12px 16px",
         margin: str = "6px 0") -> None:
    st.markdown(
        f'<div style="background:{bg};border:1px solid {border};border-radius:{radius};'
        f'padding:{padding};margin:{margin};">{content}</div>',
        unsafe_allow_html=True
    )


def _text(txt: str, size: str = "0.9rem", color: str = "rgba(255,255,255,0.8)",
          weight: str = "400", margin: str = "0") -> None:
    st.markdown(
        f'<div style="font-size:{size};color:{color};font-weight:{weight};margin:{margin};">'
        f'{txt}</div>',
        unsafe_allow_html=True
    )


def _divider():
    st.markdown(
        '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.10);margin:22px 0;">',
        unsafe_allow_html=True
    )


def _section_title(emoji: str, title: str):
    st.markdown(
        f'<div style="font-size:1.5rem;font-weight:700;color:white;margin:8px 0 16px;">'
        f'{emoji} {_e(title)}</div>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────────────────────
# Hero
# ─────────────────────────────────────────────────────────────────────────────

def render_hero():
    st.markdown(
        '<div style="text-align:center;padding:36px 20px 20px;">'
        '<div style="font-size:3rem;font-weight:800;background:linear-gradient(135deg,#f093fb,#f5576c,#4facfe,#00f2fe);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.2;">'
        '🌍 AI Trip Planner</div>'
        '<div style="color:rgba(255,255,255,0.6);font-size:1rem;margin-top:8px;">'
        'Plan your dream trip with multi-agent AI</div>'
        '</div>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────────────────────
# Success Banner
# ─────────────────────────────────────────────────────────────────────────────

def render_success_banner(plan):
    dest    = _e(plan.destination)
    country = _e(plan.country)
    st.markdown(
        f'<div style="background:linear-gradient(135deg,rgba(0,242,254,0.15),rgba(79,172,254,0.15));'
        f'border:1px solid rgba(0,242,254,0.35);border-radius:16px;padding:16px 22px;margin:12px 0;">'
        f'<span style="font-size:1.8rem;">✅</span>'
        f'<span style="font-size:1rem;font-weight:700;color:white;margin-left:12px;">Trip Plan Ready!</span>'
        f'<div style="color:rgba(255,255,255,0.6);font-size:0.85rem;margin-top:4px;">'
        f'{dest}, {country} &nbsp;·&nbsp; {plan.duration_days} Days &nbsp;·&nbsp; '
        f'{len(plan.hotels)} Hotels &nbsp;·&nbsp; {len(plan.itinerary)} Itinerary Days</div>'
        f'</div>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────────────────────
# Destination Info — uses st.columns, NO multiline f-string HTML
# ─────────────────────────────────────────────────────────────────────────────

def render_destination_info(plan):
    dest  = plan.destination_info
    flag  = "🇮🇳" if plan.is_domestic else "🌐"
    dtype = "Domestic" if plan.is_domestic else "International"

    st.markdown(
        '<div style="background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.14);'
        'border-radius:18px;padding:22px;margin:10px 0;">',
        unsafe_allow_html=True
    )

    col_left, col_right = st.columns([2, 1])

    with col_left:
        # Title
        st.markdown(
            f'<div style="font-size:2rem;font-weight:800;color:white;">📍 {_e(plan.destination)}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="color:rgba(255,255,255,0.5);font-size:0.95rem;margin-bottom:12px;">'
            f'{_e(plan.country)} {flag} · {dtype}</div>',
            unsafe_allow_html=True
        )
        # Description
        desc = _e(dest.description or "")
        if desc:
            st.markdown(
                f'<div style="color:rgba(255,255,255,0.78);font-size:0.9rem;line-height:1.6;">'
                f'{desc}</div>',
                unsafe_allow_html=True
            )
        st.markdown("<br>", unsafe_allow_html=True)

        # Weather badge
        weather_txt = _e((dest.weather or "")[:70])
        best_time   = _e((dest.best_time_to_visit or "")[:50])
        if weather_txt:
            st.markdown(
                f'<span style="background:rgba(79,172,254,0.18);border:1px solid rgba(79,172,254,0.35);'
                f'color:#4facfe;padding:4px 12px;border-radius:20px;font-size:0.78rem;">'
                f'🌤️ {weather_txt}</span>',
                unsafe_allow_html=True
            )
        if best_time:
            st.markdown(
                f'<span style="background:rgba(240,147,251,0.18);border:1px solid rgba(240,147,251,0.35);'
                f'color:#f093fb;padding:4px 12px;border-radius:20px;font-size:0.78rem;margin-left:6px;">'
                f'📅 Best: {best_time}</span>',
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown(
            '<div style="font-size:0.75rem;font-weight:700;color:rgba(255,255,255,0.4);'
            'text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Highlights</div>',
            unsafe_allow_html=True
        )
        for h in (dest.highlights or [])[:5]:
            st.markdown(
                f'<div style="color:rgba(255,255,255,0.8);font-size:0.87rem;margin:5px 0;">'
                f'<span style="color:#f093fb;">✦</span> {_e(str(h))}</div>',
                unsafe_allow_html=True
            )

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Currency Info
# ─────────────────────────────────────────────────────────────────────────────

def render_currency_info(plan):
    if plan.is_domestic:
        st.markdown(
            '<div style="background:rgba(255,193,7,0.10);border:1px solid rgba(255,193,7,0.28);'
            'border-radius:12px;padding:12px 18px;margin:8px 0;">'
            '<span style="font-size:1.3rem;">🇮🇳</span>'
            '<span style="color:white;font-weight:600;font-size:0.95rem;margin-left:10px;">'
            'Domestic Trip — INR Only</span>'
            '<div style="color:rgba(255,255,255,0.5);font-size:0.82rem;margin-top:3px;margin-left:40px;">'
            'All prices in Indian Rupees (₹)</div>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        c = plan.currency
        rate_local = f"{c.exchange_rate_inr_to_local:.4f}"
        rate_usd   = f"{c.exchange_rate_inr_to_usd:.4f}"
        st.markdown(
            f'<div style="background:rgba(79,172,254,0.10);border:1px solid rgba(79,172,254,0.28);'
            f'border-radius:12px;padding:12px 18px;margin:8px 0;">'
            f'<div style="color:white;font-weight:600;margin-bottom:8px;">💱 Multi-Currency View</div>'
            f'<span style="background:rgba(255,193,7,0.18);border:1px solid rgba(255,193,7,0.4);'
            f'color:#ffc107;padding:3px 10px;border-radius:16px;font-size:0.78rem;margin:2px;">₹ INR Base</span>'
            f'<span style="background:rgba(79,172,254,0.18);border:1px solid rgba(79,172,254,0.4);'
            f'color:#4facfe;padding:3px 10px;border-radius:16px;font-size:0.78rem;margin:2px;">'
            f'{_e(c.local)} @{rate_local}</span>'
            f'<span style="background:rgba(0,242,254,0.18);border:1px solid rgba(0,242,254,0.4);'
            f'color:#00f2fe;padding:3px 10px;border-radius:16px;font-size:0.78rem;margin:2px;">'
            f'$ USD @{rate_usd}</span>'
            f'</div>',
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────────────────────────────────────
# Budget Overview
# ─────────────────────────────────────────────────────────────────────────────

def render_budget_overview(plan):
    budget  = plan.budget
    c       = plan.currency
    per_day = budget.inr / max(plan.duration_days, 1)

    def metric(icon, label, value, sub=""):
        sub_html = f'<div style="font-size:0.72rem;color:rgba(255,255,255,0.38);margin-top:2px;">{_e(sub)}</div>' if sub else ""
        return (
            f'<div style="background:linear-gradient(135deg,rgba(102,126,234,0.25),rgba(118,75,162,0.25));'
            f'border:1px solid rgba(255,255,255,0.18);border-radius:14px;padding:16px;text-align:center;">'
            f'<div style="font-size:1.3rem;">{icon}</div>'
            f'<div style="font-size:1.35rem;font-weight:700;color:white;margin:5px 0;">{_e(value)}</div>'
            f'<div style="font-size:0.75rem;color:rgba(255,255,255,0.5);">{_e(label)}</div>'
            f'{sub_html}</div>'
        )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric("💰", "Total Budget", f"₹{budget.inr:,.0f}", "Indian Rupees"), unsafe_allow_html=True)
    with col2:
        if not plan.is_domestic:
            st.markdown(metric("🌐", "Local Currency", f"{c.local} {budget.local:,.0f}", "Destination currency"), unsafe_allow_html=True)
        else:
            st.markdown(metric("📅", "Duration", f"{plan.duration_days} Days", "Trip length"), unsafe_allow_html=True)
    with col3:
        if not plan.is_domestic:
            st.markdown(metric("💵", "USD Equiv.", f"${budget.usd:,.0f}", "US Dollars"), unsafe_allow_html=True)
        else:
            st.markdown(metric("📊", "Per Day", f"₹{per_day:,.0f}", "Daily budget"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric("🏨", "Hotels", str(len(plan.hotels)), "Options found"), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Budget Chart
# ─────────────────────────────────────────────────────────────────────────────

def render_budget_chart(plan):
    bd = plan.budget_breakdown
    categories = ["Flights", "Hotels", "Food", "Activities", "Transport"]
    values = [bd.flights.inr, bd.hotels.inr, bd.food.inr, bd.activities.inr, bd.transport.inr]

    if sum(values) == 0:
        st.info("Budget breakdown calculating...")
        return

    colors = ["#f5576c", "#f093fb", "#4facfe", "#00f2fe", "#667eea"]
    total_inr = sum(values)

    fig = go.Figure(go.Pie(
        labels=categories, values=values, hole=0.52,
        marker_colors=colors,
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
        textfont=dict(size=11, color="white"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", family="Inter"),
        legend=dict(font=dict(color="white", size=10), bgcolor="rgba(255,255,255,0.05)"),
        margin=dict(t=10, b=10, l=10, r=10), height=320,
        annotations=[dict(
            text=f"₹{total_inr:,.0f}",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color="white", family="Inter")
        )]
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# Hotels — pure Streamlit, no multiline HTML f-string
# ─────────────────────────────────────────────────────────────────────────────

def render_hotels_section(plan):
    _section_title("🏨", "Hotel Recommendations")

    if not plan.hotels:
        st.info("No hotels found for this destination.")
        return

    cols = st.columns(min(len(plan.hotels), 3))
    for idx, hotel in enumerate(plan.hotels[:3]):
        with cols[idx % 3]:
            _render_hotel_card(hotel, plan)


def _render_hotel_card(hotel, plan):
    c       = plan.currency
    is_dom  = plan.is_domestic
    stars   = "⭐" * min(int(hotel.rating), 5)
    amenities_str = ", ".join((hotel.amenities or [])[:4])
    price_inr_str = f"₹{hotel.price_per_night.inr:,.0f}/night"

    # Build secondary price line
    if not is_dom:
        price_secondary = f"{c.local} {hotel.price_per_night.local:,.0f} · ${hotel.price_per_night.usd:,.0f}"
    else:
        price_secondary = ""

    # Render using safe single-line strings
    st.markdown(
        '<div style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);'
        'border-radius:16px;padding:18px;margin-bottom:6px;">',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="font-size:3rem;text-align:center;padding:10px 0;">🏨</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="font-size:1rem;font-weight:700;color:white;">{_e(hotel.name)}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="font-size:0.82rem;color:rgba(255,255,255,0.5);margin:3px 0 8px;">'
        f'📍 {_e(hotel.location)}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="display:inline-block;background:rgba(255,193,7,0.18);'
        f'border:1px solid rgba(255,193,7,0.35);color:#ffc107;padding:3px 10px;'
        f'border-radius:8px;font-size:0.8rem;font-weight:600;margin-bottom:10px;">'
        f'{stars} {hotel.rating:.1f}/5.0</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="font-size:1.2rem;font-weight:700;color:#f5576c;">{_e(price_inr_str)}</div>',
        unsafe_allow_html=True
    )
    if price_secondary:
        st.markdown(
            f'<div style="font-size:0.77rem;color:rgba(255,255,255,0.45);margin-bottom:6px;">'
            f'{_e(price_secondary)}</div>',
            unsafe_allow_html=True
        )
    if amenities_str:
        st.markdown(
            f'<div style="font-size:0.77rem;color:rgba(255,255,255,0.5);margin-bottom:10px;">'
            f'{_e(amenities_str)}</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Native Streamlit link button - no HTML needed
    link = hotel.booking_link or f"https://www.booking.com/search.html?ss={hotel.name.replace(' ', '+')}"
    st.link_button("🏨 Book Now →", link, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# Itinerary — pure st.expander, no multiline HTML f-strings
# ─────────────────────────────────────────────────────────────────────────────

def render_itinerary_section(plan):
    _section_title("📅", "Day-by-Day Itinerary")

    if not plan.itinerary:
        st.info("No itinerary generated.")
        return

    for day in plan.itinerary:
        label = f"Day {day.day}  —  {day.date_note}"
        with st.expander(label, expanded=(day.day == 1)):
            # Meals
            if day.meals:
                meals_str = "  |  ".join(f"🍽️ {_e(m)}" for m in day.meals)
                st.markdown(
                    f'<div style="background:rgba(255,255,255,0.06);border-radius:8px;'
                    f'padding:8px 12px;margin-bottom:10px;font-size:0.8rem;'
                    f'color:rgba(255,255,255,0.6);">{meals_str}</div>',
                    unsafe_allow_html=True
                )

            # Activities
            if not day.plan:
                st.markdown(
                    '<p style="color:rgba(255,255,255,0.4);font-size:0.85rem;">No activities listed.</p>',
                    unsafe_allow_html=True
                )
            else:
                for act in day.plan:
                    cost_str = ""
                    if act.estimated_cost and act.estimated_cost.inr > 0:
                        cost_str = f" · ₹{act.estimated_cost.inr:,.0f}"

                    link = act.place_link or (
                        "https://www.google.com/maps/search/"
                        + f"{act.place} {plan.destination}".replace(" ", "+")
                    )

                    col_t, col_a = st.columns([1, 5])
                    with col_t:
                        st.markdown(
                            f'<div style="color:#4facfe;font-size:0.78rem;font-weight:600;padding-top:8px;">'
                            f'{_e(act.time)}</div>',
                            unsafe_allow_html=True
                        )
                    with col_a:
                        st.markdown(
                            f'<div style="background:rgba(255,255,255,0.05);'
                            f'border:1px solid rgba(255,255,255,0.10);border-radius:8px;'
                            f'padding:8px 12px;margin-bottom:5px;">'
                            f'<div style="font-size:0.9rem;font-weight:500;color:white;">'
                            f'{_e(act.activity)}</div>'
                            f'<div style="font-size:0.78rem;color:rgba(255,255,255,0.5);margin-top:2px;">'
                            f'📍 {_e(act.place)}{_e(cost_str)} '
                            f'<a href="{_e(link)}" target="_blank" style="color:#4facfe;">🔗 Map</a>'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )

            # Accommodation
            if day.accommodation:
                st.markdown(
                    f'<div style="margin-top:6px;padding:7px 12px;background:rgba(102,126,234,0.14);'
                    f'border-radius:7px;font-size:0.8rem;color:rgba(255,255,255,0.6);">'
                    f'🛌 {_e(day.accommodation)}</div>',
                    unsafe_allow_html=True
                )


# ─────────────────────────────────────────────────────────────────────────────
# Weather
# ─────────────────────────────────────────────────────────────────────────────

def render_weather_section(plan):
    if not plan.weather:
        return

    _section_title("🌤️", "Weather at Destination")

    weather = plan.weather
    cur     = weather.current
    loc     = weather.location

    source_map = {
        "openweathermap":  ("🟢", "Live — OpenWeatherMap"),
        "tavily_fallback": ("🟡", "Estimated — Web Search"),
        "minimal_fallback":("🔴", "Unavailable"),
        "error_fallback":  ("🔴", "Error"),
    }
    badge_icon, badge_label = source_map.get(weather.data_source, ("⚪", weather.data_source))
    st.markdown(
        f'<div style="font-size:0.8rem;color:rgba(255,255,255,0.4);margin-bottom:12px;">'
        f'{badge_icon} {_e(badge_label)} · {_e(cur.recorded_at)}</div>',
        unsafe_allow_html=True
    )

    col_temp, col_stats = st.columns([1, 2])

    with col_temp:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,rgba(79,172,254,0.22),rgba(0,242,254,0.14));'
            f'border:1px solid rgba(79,172,254,0.30);border-radius:16px;padding:22px;text-align:center;">'
            f'<div style="font-size:4rem;line-height:1;">{_e(cur.emoji)}</div>'
            f'<div style="font-size:2.8rem;font-weight:800;color:white;margin-top:8px;">{cur.temperature_c}°C</div>'
            f'<div style="font-size:0.9rem;color:rgba(255,255,255,0.5);">{cur.temperature_f}°F</div>'
            f'<div style="font-size:0.82rem;color:rgba(255,255,255,0.4);margin-top:4px;">Feels {cur.feels_like_c}°C</div>'
            f'<div style="font-size:1rem;font-weight:600;color:white;margin-top:8px;">{_e(cur.condition)}</div>'
            f'<div style="font-size:0.78rem;color:rgba(255,255,255,0.45);font-style:italic;">{_e(cur.condition_detail)}</div>'
            f'<div style="font-size:0.75rem;color:rgba(255,255,255,0.35);margin-top:6px;">📍 {_e(loc.name)}, {_e(loc.country)}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with col_stats:
        stats = [
            ("💧", "Humidity",    f"{cur.humidity_pct}%"),
            ("💨", "Wind",        f"{cur.wind_speed_kmh} km/h {cur.wind_direction}"),
            ("👁️", "Visibility", f"{cur.visibility_km} km"),
            ("☁️", "Cloud Cover", f"{cur.cloud_cover_pct}%"),
            ("🌅", "Sunrise",     cur.sunrise),
            ("🌇", "Sunset",      cur.sunset),
            ("📊", "Pressure",    f"{cur.pressure_hpa} hPa"),
            ("🌧️", "Rain 1h",   f"{cur.rain_1h_mm} mm"),
        ]
        r1, r2 = st.columns(2)
        for i, (icon, label, val) in enumerate(stats):
            with (r1 if i % 2 == 0 else r2):
                st.markdown(
                    f'<div style="background:rgba(255,255,255,0.07);border-radius:9px;'
                    f'padding:9px 11px;margin-bottom:7px;">'
                    f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.42);">{icon} {_e(label)}</div>'
                    f'<div style="font-size:0.9rem;font-weight:600;color:white;margin-top:2px;">{_e(val)}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    # 5-day forecast
    if weather.forecast:
        st.markdown(
            '<div style="font-size:1rem;font-weight:600;color:white;margin:18px 0 10px;">📅 5-Day Forecast</div>',
            unsafe_allow_html=True
        )
        f_cols = st.columns(len(weather.forecast))
        for col, day in zip(f_cols, weather.forecast):
            rain_pct  = day.precip_chance
            bar_color = "#4facfe" if rain_pct < 30 else "#f5a623" if rain_pct < 60 else "#f5576c"
            day_short = day.day_label.split(",")[0] if "," in day.day_label else day.day_label
            date_short= day.day_label.split(",")[1].strip() if "," in day.day_label else ""
            rain_html = (f'<div style="font-size:0.67rem;color:rgba(79,172,254,0.85);margin-top:3px;">'
                         f'🌧️ {day.rain_mm}mm</div>') if day.rain_mm >= 0.5 else ""
            with col:
                st.markdown(
                    f'<div style="background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);'
                    f'border-radius:12px;padding:12px 8px;text-align:center;">'
                    f'<div style="font-size:0.7rem;font-weight:700;color:rgba(255,255,255,0.5);text-transform:uppercase;">{_e(day_short)}</div>'
                    f'<div style="font-size:0.66rem;color:rgba(255,255,255,0.33);margin-bottom:6px;">{_e(date_short)}</div>'
                    f'<div style="font-size:1.9rem;">{_e(day.emoji)}</div>'
                    f'<div style="font-size:0.73rem;color:rgba(255,255,255,0.52);margin:4px 0;font-style:italic;">{_e(day.condition)}</div>'
                    f'<div style="font-size:1rem;font-weight:700;color:white;">{day.temp_max_c}°</div>'
                    f'<div style="font-size:0.8rem;color:rgba(255,255,255,0.4);">{day.temp_min_c}°</div>'
                    f'<div style="font-size:0.67rem;color:rgba(255,255,255,0.38);margin-top:7px;">💧 {rain_pct}%</div>'
                    f'<div style="background:rgba(255,255,255,0.12);border-radius:3px;height:3px;margin-top:3px;">'
                    f'<div style="width:{rain_pct}%;height:100%;background:{bar_color};border-radius:3px;"></div></div>'
                    f'{rain_html}</div>',
                    unsafe_allow_html=True
                )

    # Travel advice
    if weather.travel_advice:
        st.markdown(
            '<div style="font-size:1rem;font-weight:600;color:white;margin:18px 0 8px;">🧳 Weather Tips</div>',
            unsafe_allow_html=True
        )
        for tip in weather.travel_advice:
            st.markdown(
                f'<div style="background:rgba(0,242,254,0.07);border:1px solid rgba(0,242,254,0.18);'
                f'border-radius:9px;padding:9px 14px;margin:4px 0;font-size:0.86rem;'
                f'color:rgba(255,255,255,0.82);">{_e(tip)}</div>',
                unsafe_allow_html=True
            )


# ─────────────────────────────────────────────────────────────────────────────
# Transport
# ─────────────────────────────────────────────────────────────────────────────

def render_transport_section(plan):
    _section_title("✈️", "Transport Options")

    if not plan.transport:
        st.info("No transport information available.")
        return

    mode_emoji = {"flight":"✈️","train":"🚂","bus":"🚌","metro":"🚇",
                  "cab":"🚕","local":"🚌","international":"✈️"}

    for t in plan.transport:
        emoji = "🚀"
        for key, em in mode_emoji.items():
            if key in t.mode.lower():
                emoji = em
                break

        cost_str = f"₹{t.estimated_cost.inr:,.0f}"
        if not plan.is_domestic:
            cost_str += f" | {plan.currency.local} {t.estimated_cost.local:,.0f} | ${t.estimated_cost.usd:,.0f}"

        st.markdown(
            f'<div style="background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.13);'
            f'border-radius:14px;padding:16px;margin-bottom:10px;">'
            f'<div style="font-size:0.98rem;font-weight:600;color:white;">{emoji} {_e(t.mode)}</div>'
            f'<div style="font-size:0.82rem;color:rgba(255,255,255,0.53);margin:3px 0;">{_e(t.provider)}</div>'
            f'<div style="font-size:0.8rem;color:rgba(255,255,255,0.45);">⏱️ {_e(t.duration)}</div>'
            f'<div style="font-size:0.8rem;color:rgba(255,255,255,0.45);margin-top:3px;">{_e(t.details[:120])}</div>'
            f'<div style="font-size:1.1rem;font-weight:700;color:#00f2fe;margin-top:8px;">{_e(cost_str)}</div>'
            f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.33);">Estimated round trip</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        if t.booking_link:
            st.link_button(f"Book {t.mode} →", t.booking_link, use_container_width=False)


# ─────────────────────────────────────────────────────────────────────────────
# Tips
# ─────────────────────────────────────────────────────────────────────────────

def render_tips_section(plan):
    _section_title("💡", "Travel Tips")
    icons = ["💰","📱","��️","🍜","🧳","🏥","📷","⚠️"]
    for i, tip in enumerate(plan.tips or []):
        st.markdown(
            f'<div style="background:rgba(0,242,254,0.07);border:1px solid rgba(0,242,254,0.18);'
            f'border-radius:9px;padding:10px 14px;margin:5px 0;font-size:0.87rem;'
            f'color:rgba(255,255,255,0.82);">'
            f'{icons[i % len(icons)]} {_e(str(tip))}</div>',
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────────────────────────────────────
# Error & Footer
# ─────────────────────────────────────────────────────────────────────────────

def render_error(message: str):
    st.markdown(
        f'<div style="background:rgba(245,87,108,0.15);border:1px solid rgba(245,87,108,0.35);'
        f'border-radius:14px;padding:18px;color:white;">'
        f'<div style="font-size:1.05rem;font-weight:600;margin-bottom:6px;">❌ Error</div>'
        f'<div style="font-size:0.88rem;color:rgba(255,255,255,0.75);">{_e(message)}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


def render_footer():
    st.markdown(
        '<div style="text-align:center;padding:36px 20px 16px;'
        'border-top:1px solid rgba(255,255,255,0.08);margin-top:48px;">'
        '<div style="font-size:0.95rem;font-weight:600;color:rgba(255,255,255,0.5);">🌍 AI Trip Planner</div>'
        '<div style="font-size:0.8rem;color:rgba(255,255,255,0.3);margin-top:4px;">'
        'Powered by LangGraph · Groq AI · Tavily · OpenWeatherMap</div>'
        '<div style="font-size:0.88rem;color:rgba(255,255,255,0.4);margin-top:8px;">'
        '© Kaustav Roy Chowdhury</div>'
        '</div>',
        unsafe_allow_html=True
    )