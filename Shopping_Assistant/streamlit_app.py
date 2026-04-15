"""
streamlit_app.py  –  ShopMind AI  (fully fixed version)
Uses st.components.v1.html() for all rich card/table rendering so that
custom CSS classes are NEVER stripped by Streamlit's HTML sanitiser.
"""

import os, json, time
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ShopMind AI",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS  (only for native Streamlit widgets & page shell) ───────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0b0f !important;
    color: #e8e9f0;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stSidebar"] {
    background: #0d0e14 !important;
    border-right: 1px solid #1e2030;
}
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

[data-testid="stTextInput"] input {
    background: #141620 !important;
    border: 1px solid #252840 !important;
    border-radius: 12px !important;
    color: #e8e9f0 !important;
    font-size: 15px !important;
    padding: 14px 18px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,.15) !important;
}
[data-testid="stTextInput"] input::placeholder { color: #4b5563 !important; }

[data-testid="stButton"] button {
    background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
    color: #fff !important; border: none !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important; font-size: 14px !important;
    padding: 12px 28px !important; width: 100% !important;
}
[data-testid="stButton"] button:hover { opacity:.88 !important; transform:translateY(-1px) !important; }

[data-testid="stSelectbox"] > div > div {
    background: #141620 !important;
    border-color: #252840 !important;
    color: #e8e9f0 !important;
    border-radius: 8px !important;
}

[data-testid="metric-container"] {
    background: #0f1117 !important;
    border: 1px solid #1e2030 !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="metric-container"] label { color: #6b7280 !important; font-size: 12px !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e8e9f0 !important; font-family: 'Syne', sans-serif !important;
}

[data-testid="stTabs"] [data-baseweb="tab"] { color: #6b7280 !important; }
[data-testid="stTabs"] [aria-selected="true"] {
    color: #818cf8 !important; border-bottom-color: #6366f1 !important;
}

/* remove iframe border/bg */
iframe { border: none !important; background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ── Base CSS injected into every iframe component ─────────────────────────
IFRAME_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { background: transparent; font-family: 'DM Sans', sans-serif; color: #e8e9f0; }
"""


# ── Helpers ────────────────────────────────────────────────────────────────
def stars(r: float) -> str:
    f = int(r); h = 1 if (r - f) >= .5 else 0; e = 5 - f - h
    return "★" * f + "✦" * h + "☆" * e

def fmt_price(p: float) -> str:
    if p >= 100000: return f"₹{p/100000:.1f}L"
    if p >= 1000:   return f"₹{p:,.0f}"
    return f"₹{p:.0f}"

ICONS = {
    "smartphone": "📱", "phone": "📱", "laptop": "💻", "notebook": "💻",
    "headphone": "🎧", "tablet": "📲", "tv": "📺", "camera": "📷",
    "watch": "⌚", "earbuds": "🎵", "earbud": "🎵", "speaker": "🔊",
    "keyboard": "⌨️", "mouse": "🖱️", "monitor": "🖥️",
}
def get_icon(name: str) -> str:
    n = name.lower()
    for k, v in ICONS.items():
        if k in n: return v
    return "🛍️"

def wrap_iframe(body_html: str, extra_css: str = "") -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>{IFRAME_CSS}{extra_css}</style>
</head><body>{body_html}</body></html>"""


# ═══════════════════════════════════════════════════════════════════════════
#  COMPONENT RENDERERS
# ═══════════════════════════════════════════════════════════════════════════

def render_hero():
    css = """
    .hero {
        background: linear-gradient(135deg, #0d0e16 0%, #131520 40%, #0d1a2e 100%);
        border: 1px solid #1e2540; border-radius: 20px;
        padding: 44px 40px 36px; position: relative; overflow: hidden;
    }
    .hero::before {
        content: ''; position: absolute; top: -60px; right: -60px;
        width: 320px; height: 320px;
        background: radial-gradient(circle, rgba(99,102,241,.14) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero::after {
        content: ''; position: absolute; bottom: -40px; left: 20%;
        width: 200px; height: 200px;
        background: radial-gradient(circle, rgba(236,72,153,.09) 0%, transparent 70%);
        pointer-events: none;
    }
    .badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(99,102,241,.15); border: 1px solid rgba(99,102,241,.3);
        color: #818cf8; font-size: 11px; font-weight: 600; letter-spacing: 1.5px;
        text-transform: uppercase; padding: 5px 12px; border-radius: 100px;
        margin-bottom: 16px;
    }
    h1 {
        font-family: 'Syne', sans-serif; font-size: 38px; font-weight: 800;
        line-height: 1.15; margin-bottom: 12px;
        background: linear-gradient(135deg, #e8e9f0 0%, #818cf8 50%, #ec4899 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }
    p { font-size: 15px; color: #6b7280; font-weight: 300; max-width: 540px; line-height: 1.65; }
    """
    body = """
    <div class="hero">
        <div class="badge">✦ AI-Powered · 7-Agent Pipeline</div>
        <h1>Your Smart Shopping Assistant</h1>
        <p>Describe what you're looking for. Our AI pipeline searches, compares,
           and recommends the perfect product — always within your budget.</p>
    </div>"""
    components.html(wrap_iframe(body, css), height=210, scrolling=False)


def render_best_choice(best: dict):
    name   = best.get("name", "")
    reason = best.get("reason", "")
    css = """
    .banner {
        background: linear-gradient(135deg, #1a0d26 0%, #1a1030 50%, #0d1a2e 100%);
        border: 1px solid rgba(236,72,153,.35); border-radius: 18px;
        padding: 28px 32px; position: relative; overflow: hidden;
    }
    .banner::after { content: '🏆'; position: absolute; right: 28px; top: 20px;
        font-size: 52px; opacity: .12; }
    .label { font-family: 'Syne', sans-serif; font-size: 10px; font-weight: 700;
        letter-spacing: 2px; text-transform: uppercase; color: #ec4899; margin-bottom: 8px; }
    .name  { font-family: 'Syne', sans-serif; font-size: 26px; font-weight: 800;
        color: #f0e8ff; margin-bottom: 10px; line-height: 1.2; }
    .reason { font-size: 14px; color: #9ca3af; line-height: 1.75; max-width: 740px; }
    """
    body = f"""
    <div class="banner">
        <div class="label">🏆 AI Recommendation</div>
        <div class="name">{name}</div>
        <div class="reason">{reason}</div>
    </div>"""
    components.html(wrap_iframe(body, css), height=155, scrolling=False)


def render_product_cards(products: list, best_name: str):
    """Amazon/Flipkart-style product cards — completely self-contained iframe."""
    n_cols = min(3, len(products))

    css = f"""
    .grid {{
        display: grid;
        grid-template-columns: repeat({n_cols}, 1fr);
        gap: 18px;
        padding: 4px 0;
    }}
    .card {{
        background: linear-gradient(145deg, #0f1117, #141620);
        border: 1px solid #1e2030; border-radius: 16px;
        padding: 22px; position: relative; overflow: hidden;
        display: flex; flex-direction: column;
        transition: border-color .2s, transform .2s;
    }}
    .card:hover {{ border-color: #6366f1; transform: translateY(-2px); }}
    .card.best {{ background: linear-gradient(145deg, #130e1a, #1a1020); border-color: #ec4899; }}
    .best-badge {{
        position: absolute; top: 14px; right: 14px;
        background: linear-gradient(135deg, #ec4899, #f97316);
        color: #fff; font-size: 10px; font-weight: 700; letter-spacing: 1px;
        text-transform: uppercase; padding: 4px 10px; border-radius: 100px;
    }}
    .p-icon {{
        width: 52px; height: 52px;
        background: linear-gradient(135deg, #1e2040, #252850);
        border-radius: 14px; display: flex; align-items: center;
        justify-content: center; font-size: 26px; margin-bottom: 14px;
    }}
    .p-name {{
        font-family: 'Syne', sans-serif; font-size: 14px; font-weight: 700;
        color: #e8e9f0; line-height: 1.35; margin-bottom: 6px;
    }}
    .p-price {{
        font-family: 'Syne', sans-serif; font-size: 22px; font-weight: 800;
        color: #6366f1; margin-bottom: 4px;
    }}
    .p-rating {{ display: flex; align-items: center; gap: 6px; margin-bottom: 12px; }}
    .stars    {{ color: #fbbf24; font-size: 13px; letter-spacing: 1px; }}
    .rnum     {{ font-size: 12px; color: #6b7280; }}
    .feat-tag {{
        display: inline-block;
        background: rgba(99,102,241,.12); border: 1px solid rgba(99,102,241,.25);
        color: #a5b4fc; font-size: 11px; padding: 3px 9px;
        border-radius: 6px; margin: 2px;
    }}
    .divider  {{ border-top: 1px solid #1e2030; margin: 12px 0 10px; }}
    .pro {{ color: #34d399; font-size: 12px; margin: 4px 0; }}
    .con {{ color: #f87171; font-size: 12px; margin: 4px 0; }}
    """

    cards_html = ""
    for p in products:
        is_best = p["name"] == best_name
        cls     = "card best" if is_best else "card"
        badge   = '<span class="best-badge">BEST PICK</span>' if is_best else ""
        rating  = p.get("rating", 4.0)

        feats = "".join(f'<span class="feat-tag">{f}</span>'
                        for f in p.get("features", [])[:4])
        pros  = "".join(f'<div class="pro">✓ {x}</div>'
                        for x in p.get("pros", [])[:3])
        cons  = "".join(f'<div class="con">✗ {x}</div>'
                        for x in p.get("cons", [])[:2])

        cards_html += f"""
        <div class="{cls}">
            {badge}
            <div class="p-icon">{get_icon(p['name'])}</div>
            <div class="p-name">{p['name']}</div>
            <div class="p-price">{fmt_price(p.get('price', 0))}</div>
            <div class="p-rating">
                <span class="stars">{stars(rating)}</span>
                <span class="rnum">{rating:.1f} / 5</span>
            </div>
            <div>{feats}</div>
            <div class="divider"></div>
            {pros}{cons}
        </div>"""

    body   = f'<div class="grid">{cards_html}</div>'
    rows   = ((len(products) + n_cols - 1) // n_cols)
    height = 400 * rows + 24
    components.html(wrap_iframe(body, css), height=height, scrolling=False)


def render_alternatives(alts: list):
    css = """
    .alt {
        background: #0f1117; border: 1px solid #1e2030; border-radius: 12px;
        padding: 14px 20px; display: flex; align-items: center;
        justify-content: space-between; margin-bottom: 8px;
    }
    .alt:hover { border-color: #252840; }
    .aname { font-size: 13px; font-weight: 500; color: #d1d5db; }
    .aprice { font-family: 'Syne', sans-serif; font-weight: 700;
              color: #818cf8; font-size: 14px; }
    """
    rows = "".join(f"""
    <div class="alt">
        <span class="aname">{get_icon(a['name'])} &nbsp;{a['name']}</span>
        <span class="aprice">{fmt_price(a.get('price', 0))}</span>
    </div>""" for a in alts)

    components.html(wrap_iframe(rows, css),
                    height=len(alts) * 60 + 16, scrolling=False)


def render_compare_table(products: list, best_name: str):
    css = """
    .wrap { overflow-x: auto; border-radius: 12px; border: 1px solid #1e2030; }
    table { width: 100%; border-collapse: separate; border-spacing: 0; }
    th {
        background: #141620; color: #6b7280;
        font-family: 'Syne', sans-serif; font-size: 11px; font-weight: 700;
        letter-spacing: 1px; text-transform: uppercase;
        padding: 13px 16px; text-align: left; border-bottom: 1px solid #1e2030;
    }
    td {
        padding: 13px 16px; border-bottom: 1px solid #141620;
        font-size: 13px; color: #d1d5db; background: #0f1117;
    }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background: #131620; }
    """

    headers = ["Product", "Price", "Rating", "Features", "Pros", "Cons"]
    thead   = "".join(f"<th>{h}</th>" for h in headers)
    rows    = ""
    for p in products:
        is_b  = p["name"] == best_name
        nm    = (f'<strong style="color:#ec4899">{p["name"]} 🏆</strong>'
                 if is_b else p["name"])
        rows += f"""<tr>
          <td>{nm}</td>
          <td style="color:#6366f1;font-weight:700;font-family:'Syne',sans-serif">
              {fmt_price(p.get('price', 0))}</td>
          <td style="color:#fbbf24;font-weight:600">{p.get('rating', 0):.1f} ★</td>
          <td style="font-size:12px;color:#9ca3af">{", ".join(p.get("features",[])[:2]) or "—"}</td>
          <td style="font-size:12px;color:#6ee7b7">{" · ".join(p.get("pros",[])[:2]) or "—"}</td>
          <td style="font-size:12px;color:#fca5a5">{" · ".join(p.get("cons",[])[:1]) or "—"}</td>
        </tr>"""

    body   = f'<div class="wrap"><table><thead><tr>{thead}</tr></thead><tbody>{rows}</tbody></table></div>'
    height = 52 + len(products) * 52 + 16
    components.html(wrap_iframe(body, css), height=height, scrolling=False)


def render_reviews(review: dict, product_name: str):
    sentiment  = review.get("sentiment", "neutral")
    sc_map = {"positive": ("#34d399", "rgba(52,211,153,.15)"),
              "neutral":  ("#fbbf24", "rgba(251,191,36,.15)"),
              "negative": ("#f87171", "rgba(248,113,113,.15)")}
    sc, sbg = sc_map.get(sentiment, sc_map["neutral"])
    sem_emoji = {"positive":"😊","neutral":"😐","negative":"😕"}.get(sentiment,"😐")

    def item_rows(lst, fg, bg, sym):
        return "".join(
            f'<div style="background:{bg};border:1px solid {fg}44;border-radius:8px;'
            f'padding:10px 14px;margin:5px 0;font-size:13px;color:{fg}">'
            f'{sym} {x}</div>' for x in lst)

    pos_rows   = item_rows(review.get("positives",   []), "#34d399","rgba(52,211,153,.07)","✓")
    neg_rows   = item_rows(review.get("negatives",   []), "#fca5a5","rgba(248,113,113,.07)","✗")
    issue_rows = item_rows(review.get("common_issues",[]),"#fde68a","rgba(251,191,36,.07)","⚠")

    css = f"""
    .card  {{ background:#0f1117;border:1px solid #1e2030;border-radius:14px;padding:20px }}
    .hdr   {{ display:flex;align-items:center;justify-content:space-between;margin-bottom:18px }}
    .title {{ font-family:'Syne',sans-serif;font-size:14px;font-weight:700;color:#e8e9f0 }}
    .badge {{ display:inline-flex;align-items:center;gap:6px;background:{sbg};
              color:{sc};font-size:12px;font-weight:600;padding:5px 14px;
              border-radius:100px;text-transform:capitalize }}
    .grid  {{ display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:14px }}
    .lbl   {{ font-family:'Syne',sans-serif;font-size:11px;font-weight:700;
              letter-spacing:1px;text-transform:uppercase;color:#6b7280;margin-bottom:8px }}
    """
    issue_section = (f'<div><div class="lbl">⚠️ Common Issues</div>{issue_rows}</div>'
                     if issue_rows else "")
    body = f"""
    <div class="card">
        <div class="hdr">
            <div class="title">{product_name} — Review Summary</div>
            <span class="badge">{sem_emoji} {sentiment}</span>
        </div>
        <div class="grid">
            <div><div class="lbl">✅ Positives</div>{pos_rows}</div>
            <div><div class="lbl">❌ Negatives</div>{neg_rows}</div>
        </div>
        {issue_section}
    </div>"""

    n = (len(review.get("positives",[])) + len(review.get("negatives",[])) +
         len(review.get("common_issues",[])))
    components.html(wrap_iframe(body, css), height=120 + n * 54, scrolling=False)


def render_section_header(emoji: str, title: str):
    css = """
    .sh { font-family:'Syne',sans-serif; font-size:18px; font-weight:700;
          color:#e8e9f0; display:flex; align-items:center; gap:10px; padding:6px 0; }
    .sh::after { content:''; flex:1; height:1px;
                 background:linear-gradient(90deg,#1e2030,transparent); }
    """
    components.html(wrap_iframe(f'<div class="sh">{emoji}&nbsp;{title}</div>', css),
                    height=48, scrolling=False)


# ═══════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<div style="font-family:Syne,sans-serif;font-size:20px;font-weight:800;'
        'background:linear-gradient(135deg,#818cf8,#ec4899);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        'padding:20px 0 4px">ShopMind AI</div>'
        '<div style="font-size:11px;color:#4b5563;margin-bottom:16px">'
        'Powered by LangGraph + Groq</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown('<p style="font-size:11px;font-weight:700;letter-spacing:1.5px;'
                'text-transform:uppercase;color:#4b5563;margin-bottom:8px">🎛️ Filters</p>',
                unsafe_allow_html=True)

    budget   = st.slider("Max Budget (₹)", 2000, 200000, 30000, 1000, format="₹%d")
    category = st.selectbox("Category", ["All","Smartphones","Laptops","Headphones",
                 "Tablets","Smart Watches","Cameras","Speakers","TVs","Accessories"])
    brand    = st.selectbox("Brand Preference", ["Any","Samsung","Apple","OnePlus",
                 "Xiaomi","Realme","Boat","Sony","LG","Lenovo","HP","Dell","Asus"])

    st.divider()
    st.markdown('<p style="font-size:11px;font-weight:700;letter-spacing:1.5px;'
                'text-transform:uppercase;color:#4b5563;margin-bottom:8px">⚙️ API Keys</p>',
                unsafe_allow_html=True)

    groq_key   = st.text_input("GROQ API Key",  value="",
                               type="password", placeholder="gsk_...")
    tavily_key = st.text_input("TAVILY API Key", value="",
                               type="password", placeholder="tvly-...")

    if groq_key:   os.environ["GROQ_API_KEY"]   = groq_key
    if tavily_key: os.environ["TAVILY_API_KEY"]  = tavily_key

    st.divider()
    st.markdown("""<div style='font-size:11px;color:#374151;line-height:2'>
        🔗 <a href='https://console.groq.com' style='color:#6366f1' target='_blank'>Get Groq Key</a><br>
        🔗 <a href='https://tavily.com' style='color:#6366f1' target='_blank'>Get Tavily Key</a><br><br>
        Rate-limit safe · Disk cache enabled</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN  –  Hero + Search
# ═══════════════════════════════════════════════════════════════════════════
render_hero()

col_in, col_btn = st.columns([4, 1])
with col_in:
    hint = f"e.g. best {category.lower() if category!='All' else 'smartphone'} under ₹{budget:,}"
    if brand != "Any": hint += f" from {brand}"
    user_query = st.text_input("Search", placeholder=hint, label_visibility="collapsed")
with col_btn:
    st.write("")
    search_clicked = st.button("🔍  Search", use_container_width=True)

st.markdown('<div style="margin-top:8px;margin-bottom:4px;font-size:11px;color:#4b5563">✦ Quick searches:</div>',
            unsafe_allow_html=True)
examples = ["Best phone under ₹15,000","Wireless earbuds under ₹3,000",
            "Gaming laptop under ₹80,000","Smart watch under ₹5,000"]
ec = st.columns(len(examples))
for i, ex in enumerate(examples):
    with ec[i]:
        if st.button(ex, key=f"ex_{i}"):
            user_query = ex; search_clicked = True

st.write("")


# ═══════════════════════════════════════════════════════════════════════════
#  PIPELINE
# ═══════════════════════════════════════════════════════════════════════════
if search_clicked and user_query:
    if not os.getenv("GROQ_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        st.error("⚠️  Please add your **GROQ_API_KEY** and **TAVILY_API_KEY** in the sidebar.")
        st.stop()

    full_query = user_query
    if "under" not in user_query.lower() and f"₹{budget:,}" not in user_query:
        full_query += f" under ₹{budget:,}"
    if brand != "Any" and brand.lower() not in user_query.lower():
        full_query += f" {brand}"
    if category != "All" and category.lower() not in user_query.lower():
        full_query += f" {category}"

    steps = ["🔍 Understanding your query…","🛒 Searching for products…",
             "⚖️  Comparing products…","💰 Optimising for your budget…",
             "📝 Analysing reviews…","🏆 Generating recommendation…","📦 Assembling output…"]

    prog    = st.progress(0)
    step_ph = st.empty()

    def upd(i, msg):
        prog.progress((i + 1) / len(steps))
        step_ph.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;padding:10px 16px;'
            f'background:#0f1117;border:1px solid #1e2030;border-radius:10px;'
            f'font-size:13px;color:#9ca3af;margin-bottom:4px">'
            f'<span style="color:#6366f1;font-size:16px">⚡</span>{msg}</div>',
            unsafe_allow_html=True)

    upd(0, steps[0])
    time.sleep(0.05)

    try:
        from graph.shopping_graph import run_shopping_assistant
        upd(1, steps[1])
        with st.spinner("Running AI agent pipeline…"):
            result = run_shopping_assistant(full_query)
        for i, s in enumerate(steps[2:], 2):
            upd(i, s); time.sleep(0.04)
        prog.progress(1.0); step_ph.empty(); prog.empty()
    except Exception as e:
        prog.empty(); step_ph.empty()
        st.error(f"❌ Pipeline error: {e}")
        st.info("💡 Check your API keys and that all dependencies are installed.")
        st.stop()

    if not result or "error" in result:
        st.error(f"❌ {result.get('error','Unknown error')}"); st.stop()

    st.session_state["result"] = result
    st.session_state["query"]  = user_query


# ═══════════════════════════════════════════════════════════════════════════
#  RESULTS
# ═══════════════════════════════════════════════════════════════════════════
if "result" in st.session_state:
    result   = st.session_state["result"]
    products = result.get("products", [])
    best     = result.get("best_choice", {})
    alts     = result.get("alternatives", [])
    review   = result.get("review_summary")

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    prices = [p["price"] for p in products if p.get("price")]
    with m1: st.metric("Products Found", len(products))
    with m2: st.metric("Price Range",
        f"{fmt_price(min(prices))} – {fmt_price(max(prices))}" if prices else "—")
    with m3:
        avg = sum(p.get("rating",0) for p in products) / len(products) if products else 0
        st.metric("Avg Rating", f"{stars(avg)} {avg:.1f}")
    with m4: st.metric("Your Budget", fmt_price(result.get("budget", 0)))

    st.write("")

    if best:
        render_best_choice(best)

    st.write("")

    tab_prod, tab_cmp, tab_rev, tab_json = st.tabs([
        "🛍️  Products", "⚖️  Compare", "📝  Reviews", "{ }  JSON"
    ])

    with tab_prod:
        render_section_header("🛍️", "Products Found")
        if products:
            render_product_cards(products, best.get("name", ""))
        else:
            st.info("No products found.")
        if alts:
            render_section_header("💡", "Budget Alternatives")
            render_alternatives(alts)

    with tab_cmp:
        render_section_header("⚖️", "Side-by-Side Comparison")
        if products:
            render_compare_table(products, best.get("name", ""))
        else:
            st.info("No products to compare.")

    with tab_rev:
        render_section_header("📝", "Review Insights")
        if review:
            render_reviews(review, best.get("name", "Top Product"))
        else:
            st.info("📝 Review data not available for this search.")

    with tab_json:
        render_section_header("{ }", "Raw JSON Output")
        st.code(json.dumps(result, indent=2, ensure_ascii=False), language="json")
        st.download_button("⬇️  Download JSON",
            data=json.dumps(result, indent=2, ensure_ascii=False),
            file_name="shopping_result.json", mime="application/json")

# ── Empty state ────────────────────────────────────────────────────────────
elif not search_clicked:
    css = """
    body { text-align: center; padding: 50px 20px; background: transparent; }
    .icon  { font-size: 64px; margin-bottom: 16px; }
    .title { font-family:'Syne',sans-serif; font-size: 20px; font-weight: 700;
             color: #374151; margin-bottom: 8px; }
    .sub   { font-size: 14px; color: #4b5563; }
    """
    body = """
    <div class="icon">🛍️</div>
    <div class="title">Ready to find your perfect product?</div>
    <div class="sub">Enter a search query above or try one of the quick searches.</div>"""
    components.html(wrap_iframe(body, css), height=200, scrolling=False)

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:32px 0 16px;border-top:1px solid #1e2030;
     margin-top:40px;color:#374151;font-size:12px;letter-spacing:.5px">
  © Kaustav Roy Chowdhury &nbsp;·&nbsp;
  <span style="color:#4b5563">ShopMind AI</span> &nbsp;·&nbsp;
  Built with LangGraph · Groq · Tavily · Streamlit
</div>
""", unsafe_allow_html=True)
