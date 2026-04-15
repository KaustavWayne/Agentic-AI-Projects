import streamlit as st
import requests
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DentaFlow · Appointments",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Injected CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: #F7F9FC !important;
    color: #111827 !important;
}
[data-testid="stAppViewContainer"] > .main { background: #F7F9FC !important; }
[data-testid="block-container"] { padding: 2rem 2.5rem 3rem !important; max-width: 1280px !important; }
#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }

[data-testid="stSidebar"] {
    background: #0F172A !important;
    border-right: none !important;
    min-width: 240px !important;
    max-width: 240px !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }
[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div { color: #CBD5E1 !important; }
[data-testid="stSidebar"] .stTextInput input {
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
    font-size: 0.875rem !important;
    padding: 0.6rem 0.9rem !important;
}
[data-testid="stSidebar"] .stTextInput input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.2) !important;
}
[data-testid="stSidebar"] .stTextInput label { display: none !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #94A3B8 !important;
    border-radius: 10px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 0.6rem 1rem !important;
    margin-bottom: 2px !important;
    transition: all 0.15s !important;
    box-shadow: none !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1E293B !important;
    color: #F1F5F9 !important;
    transform: none !important;
}
[data-testid="stMainBlockContainer"] .stButton > button {
    background: linear-gradient(135deg, #1D4ED8, #2563EB) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.65rem 2rem !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.35) !important;
    transition: all 0.2s !important;
}
[data-testid="stMainBlockContainer"] .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(37,99,235,0.45) !important;
    filter: brightness(1.05) !important;
}
[data-testid="stMainBlockContainer"] .stTextInput input,
[data-testid="stMainBlockContainer"] .stTextArea textarea {
    border-radius: 12px !important;
    border: 1.5px solid #E2E8F0 !important;
    padding: 0.75rem 1rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9rem !important;
    background: #fff !important;
    color: #1E293B !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}
[data-testid="stMainBlockContainer"] .stTextInput input:focus,
[data-testid="stMainBlockContainer"] .stTextArea textarea:focus {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
}
[data-testid="stMainBlockContainer"] .stTextInput label,
[data-testid="stMainBlockContainer"] .stTextArea label {
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    color: #64748B !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}
[data-testid="column"] { padding: 0 0.6rem !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_id_val" not in st.session_state:
    st.session_state.user_id_val = ""
if "prefill" not in st.session_state:
    st.session_state.prefill = ""
if "active_page" not in st.session_state:
    st.session_state.active_page = "Chat Assistant"
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

def send_callback():
    if st.session_state.chat_input.strip():
        st.session_state.last_query = st.session_state.chat_input
        st.session_state.chat_input = "" # Safely clear here

API_URL = "http://127.0.0.1:8003/execute"

DOCTORS = [
    ("John Doe",        "General Dentist",   "🦷"),
    ("Jane Smith",      "Orthodontist",       "😁"),
    ("Emily Johnson",   "Pediatric Dentist",  "👶"),
    ("Robert Martinez", "Oral Surgeon",       "🔬"),
    ("Susan Davis",     "Cosmetic Dentist",   "✨"),
    ("Michael Green",   "Prosthodontist",     "🏥"),
    ("Kevin Anderson",  "Emergency Dentist",  "🚑"),
    ("Daniel Miller",   "General Dentist",    "🦷"),
    ("Sarah Wilson",    "Orthodontist",       "😁"),
    ("Lisa Brown",      "Cosmetic Dentist",   "✨"),
]

SPECS = ["🦷 General", "😁 Orthodontist", "👶 Pediatric",
         "✨ Cosmetic", "🏥 Prosthodontist", "🔬 Oral Surgeon", "🚑 Emergency"]

# ── Helper: render chat messages using st.chat_message (Streamlit-native, no HTML injection) ──
def render_chat():
    """
    Uses Streamlit's native st.chat_message so there is zero chance of
    raw HTML leaking into the displayed text.
    """
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="min-height:220px;display:flex;flex-direction:column;
                    align-items:center;justify-content:center;padding:2.5rem;text-align:center;">
            <div style="font-size:2.8rem;margin-bottom:0.8rem;">🦷</div>
            <div style="font-size:1rem;font-weight:700;color:#0F172A;margin-bottom:6px;
                        font-family:'Plus Jakarta Sans',sans-serif;">Hello! How can I help you today?</div>
            <div style="font-size:0.85rem;color:#64748B;max-width:320px;line-height:1.6;
                        font-family:'Plus Jakarta Sans',sans-serif;">
                Ask about doctor availability, book, cancel or reschedule appointments.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    for msg in st.session_state.chat_history:
        role = msg["role"]          # "user" or "assistant"
        # Convert stored <br> back to newlines for st.chat_message display
        content = msg["content"].replace("<br>", "\n")
        ts = msg.get("time", "")

        if role == "user":
            with st.chat_message("user"):
                st.markdown(
                    f"<div style='font-family:Plus Jakarta Sans,sans-serif;font-size:0.9rem;'>"
                    f"{content}</div>"
                    f"<div style='font-size:0.68rem;color:#94A3B8;text-align:right;margin-top:3px;'>{ts}</div>",
                    unsafe_allow_html=True,
                )
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(
                    f"<div style='font-family:Plus Jakarta Sans,sans-serif;font-size:0.9rem;"
                    f"line-height:1.65;'>{content}</div>"
                    f"<div style='font-size:0.68rem;color:#94A3B8;margin-top:3px;'>{ts}</div>",
                    unsafe_allow_html=True,
                )

# ════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:1.8rem 1.4rem 0.5rem;">
        <div style="font-size:1.5rem;font-weight:800;color:#FFFFFF !important;letter-spacing:-0.03em;
                    font-family:'Plus Jakarta Sans',sans-serif;">
            🦷 DentaFlow
        </div>
        <div style="font-size:0.68rem;color:#64748B;letter-spacing:0.1em;
                    text-transform:uppercase;margin-top:3px;font-family:'Plus Jakarta Sans',sans-serif;">
            Smart Appointment System
        </div>
    </div>
    <hr style="border:none;border-top:1px solid #1E293B;margin:1rem 0;">
    """, unsafe_allow_html=True)

    nav_items = [
        ("💬", "Chat Assistant"),
        ("📅", "My Appointments"),
        ("👨‍⚕️", "Find a Doctor"),
        ("📋", "Medical History"),
    ]
    for icon, label in nav_items:
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state.active_page = label
            st.rerun()

    st.markdown("""
    <hr style="border:none;border-top:1px solid #1E293B;margin:1rem 0;">
    <div style="padding:0 1.4rem 0.5rem;">
        <div style="font-size:0.68rem;font-weight:700;color:#64748B;
                    letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;
                    font-family:'Plus Jakarta Sans',sans-serif;">Your Patient ID</div>
    </div>""", unsafe_allow_html=True)

    pid = st.text_input("pid_label", placeholder="e.g. 1234567",
                        label_visibility="collapsed", key="pid_input")
    if pid:
        st.session_state.user_id_val = pid
        st.markdown(f"""
        <div style="margin:6px 0.7rem 0;padding:10px 14px;background:#166534;
                    border:1px solid #22C55E;border-radius:8px;font-size:0.82rem;
                    color:#FFFFFF;font-family:'Plus Jakarta Sans',sans-serif;">
            ✅ &nbsp;ID set: &nbsp;<strong style="color:#86EFAC;">#{pid}</strong>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <hr style="border:none;border-top:1px solid #1E293B;margin:1rem 0;">
    <div style="padding:0 1.4rem 0.6rem;">
        <div style="font-size:0.68rem;font-weight:700;color:#64748B;
                    letter-spacing:0.1em;text-transform:uppercase;
                    font-family:'Plus Jakarta Sans',sans-serif;">Quick Queries</div>
    </div>""", unsafe_allow_html=True)

    for s in ["Check tomorrow's availability", "Book with Dr. Jane Smith", "Cancel my appointment"]:
        if st.button(f"→ {s}", key=f"s_{s}", use_container_width=True):
            st.session_state.prefill = s
            st.rerun()

    st.markdown("""
    <div style="padding:2rem 1.4rem 1rem;font-size:0.68rem;color:#475569;
                text-align:center;font-family:'Plus Jakarta Sans',sans-serif;">
        DentaFlow v1.1 · Powered by LangGraph + Groq
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# PAGES
# ════════════════════════════════════════════════════════════════════════
active = st.session_state.active_page

if active == "My Appointments":
    st.markdown("""
    <div style="background:#fff;border:1px solid #E2E8F0;border-radius:16px;
                padding:2rem;margin-bottom:1.5rem;box-shadow:0 2px 10px rgba(0,0,0,0.05);">
        <div style="font-size:1.3rem;font-weight:800;color:#0F172A;margin-bottom:0.4rem;
                    font-family:'Plus Jakarta Sans',sans-serif;">📅 My Appointments</div>
        <div style="font-size:0.9rem;color:#64748B;">Enter your Patient ID in the sidebar and use the chat to view your appointments.</div>
    </div>""", unsafe_allow_html=True)
    st.info("💡 Use the Chat Assistant to check, book, or cancel your appointments.")

elif active == "Find a Doctor":
    st.markdown("""<div style="font-size:1.3rem;font-weight:800;color:#0F172A;margin-bottom:1.2rem;
                font-family:'Plus Jakarta Sans',sans-serif;">👨‍⚕️ Find a Doctor</div>""",
                unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (name, spec, emoji) in enumerate(DOCTORS):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #E2E8F0;border-radius:14px;
                        padding:1rem 1.2rem;margin-bottom:0.8rem;
                        box-shadow:0 2px 8px rgba(0,0,0,0.05);display:flex;align-items:center;gap:12px;">
                <div style="width:44px;height:44px;min-width:44px;
                            background:linear-gradient(135deg,#0F172A,#1D4ED8);
                            border-radius:50%;display:flex;align-items:center;
                            justify-content:center;font-size:1.2rem;">{emoji}</div>
                <div>
                    <div style="font-size:0.9rem;font-weight:700;color:#0F172A;">{name}</div>
                    <div style="font-size:0.78rem;color:#64748B;margin-top:2px;">{spec}</div>
                </div>
            </div>""", unsafe_allow_html=True)

elif active == "Medical History":
    st.markdown("""
    <div style="background:#fff;border:1px solid #E2E8F0;border-radius:16px;
                padding:2rem;margin-bottom:1.5rem;box-shadow:0 2px 10px rgba(0,0,0,0.05);">
        <div style="font-size:1.3rem;font-weight:800;color:#0F172A;margin-bottom:0.4rem;
                    font-family:'Plus Jakarta Sans',sans-serif;">📋 Medical History</div>
        <div style="font-size:0.9rem;color:#64748B;">Your dental records and visit history will appear here.</div>
    </div>""", unsafe_allow_html=True)
    st.info("💡 Medical history feature coming soon.")

# ── Chat Assistant ────────────────────────────────────────────────────────────
else:
    # Hero banner
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0F172A 0%,#1E3A5F 50%,#1D4ED8 100%);
                border-radius:20px;padding:2.8rem 3rem;margin-bottom:2rem;
                box-shadow:0 20px 60px rgba(15,23,42,0.3);">
      <div style="display:inline-flex;align-items:center;gap:6px;
                  background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);
                  border-radius:50px;padding:5px 14px;font-size:0.75rem;font-weight:600;
                  color:#BAE6FD;margin-bottom:1rem;">⚡ AI-Powered &nbsp;·&nbsp; Available 24/7</div>
      <div style="font-size:2.4rem;font-weight:800;color:#FFFFFF;line-height:1.15;
                  letter-spacing:-0.03em;margin-bottom:0.7rem;">
          Your Smart Dental<br>Assistant</div>
      <div style="font-size:1rem;color:#94A3B8;max-width:500px;line-height:1.65;margin-bottom:2rem;">
          Book, reschedule, or check availability across 10 specialist dentists — all through a natural conversation.</div>
      <div style="display:flex;gap:3rem;">
        <div><div style="font-size:2rem;font-weight:800;color:#FFFFFF;">10</div>
             <div style="font-size:0.75rem;color:#64748B;margin-top:2px;">Specialist Doctors</div></div>
        <div><div style="font-size:2rem;font-weight:800;color:#FFFFFF;">7</div>
             <div style="font-size:0.75rem;color:#64748B;margin-top:2px;">Specializations</div></div>
        <div><div style="font-size:2rem;font-weight:800;color:#FFFFFF;">∞</div>
             <div style="font-size:0.75rem;color:#64748B;margin-top:2px;">Available Slots</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([3, 2], gap="large")

    # ── LEFT: CHAT ────────────────────────────────────────────────────
    with left:
        # Chat card header
        st.markdown("""
        <div style="background:#fff;border:1px solid #E2E8F0;border-radius:16px 16px 0 0;
                    padding:1.2rem 1.6rem;border-bottom:1px solid #F1F5F9;">
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:1.1rem;">💬</span>
                <span style="font-size:1rem;font-weight:700;color:#0F172A;">Chat with DentaFlow AI</span>
                <span style="margin-left:auto;background:#DCFCE7;color:#16A34A;
                             font-size:0.7rem;font-weight:700;padding:3px 10px;
                             border-radius:50px;border:1px solid #BBF7D0;">● Online</span>
            </div>
        </div>
        <div style="background:#fff;border-left:1px solid #E2E8F0;border-right:1px solid #E2E8F0;
                    padding:0.5rem 0;">
        </div>
        """, unsafe_allow_html=True)

        # ── FIX: Use st.chat_message (native Streamlit) — no raw HTML injection ──
        render_chat()

        # Input area
        st.markdown("""
        <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:0 0 16px 16px;
                    padding:1rem 0 0 0;border-top:1px solid #F1F5F9;">
        </div>""", unsafe_allow_html=True)

        prefill_val = st.session_state.prefill if st.session_state.prefill else ""
        if prefill_val:
            st.session_state.prefill = ""

        user_query = st.text_area(
            "Message",
            value=prefill_val,
            placeholder='e.g. "Is Dr. Jane Smith available on 7/15/2026 8:00 AM? My ID is 1234567"',
            height=95,
            label_visibility="collapsed",
            key="chat_input",
        )

        c1, c2 = st.columns([1, 2])
        with c1:
            st.button("Send Message →", use_container_width=True, key="send_btn", on_click=send_callback)
        with c2:
            st.markdown("""
            <div style="padding-top:10px;font-size:0.78rem;color:#94A3B8;">
                💡 Date format: MM-DD-YYYY
            </div>""", unsafe_allow_html=True)

        if st.session_state.chat_history:
            if st.button("🗑 Clear Chat", key="clear"):
                st.session_state.chat_history = []
                st.rerun()

        # ── Handle send ───────────────────────────────────────────────────
        if st.session_state.last_query:
            user_query = st.session_state.last_query
            st.session_state.last_query = "" # Reset for next time
            
            uid = st.session_state.user_id_val.strip() or "0000000"
            now = datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append({
                "role": "user", "content": user_query.strip(), "time": now
            })
            with st.spinner("DentaFlow AI is thinking..."):
                try:
                    resp = requests.post(
                        API_URL,
                        json={"messages": user_query.strip(), "id_number": int(uid)},
                        timeout=60,
                        verify=False,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        msgs = data.get("messages", [])
                        reply = "I've processed your request."
                        for m in reversed(msgs):
                            if isinstance(m, dict):
                                t = m.get("type", m.get("role", ""))
                                if t in ("ai", "assistant"):
                                    reply = m.get("content", reply)
                                    break
                        low = reply.lower()
                        success_words = {"successfully", "confirmed", "booked", "cancelled", "rescheduled", "canceled", "moved"}
                        badge = ("✅ " if any(word in low for word in success_words)
                                 else "⚠️ " if "no availability" in low or "not available" in low
                                 else "❌ " if "error" in low or "failed" in low
                                 else "ℹ️ ")
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": badge + reply.replace("\n", "<br>"),
                            "time": datetime.now().strftime("%H:%M"),
                        })
                    else:
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"❌ Server error {resp.status_code}. Check FastAPI logs.",
                            "time": datetime.now().strftime("%H:%M"),
                        })
                except requests.exceptions.ConnectionError:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": "❌ Cannot reach backend. Make sure FastAPI is running on port 8003.",
                        "time": datetime.now().strftime("%H:%M"),
                    })
                except Exception as e:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"❌ {str(e)}",
                        "time": datetime.now().strftime("%H:%M"),
                    })
            st.rerun()

    # ── RIGHT: INFO PANELS ────────────────────────────────────────────────
    with right:
        specs_pills = "".join([
            f'<span style="background:#EFF6FF;color:#1D4ED8;border:1px solid #BFDBFE;'
            f'border-radius:50px;padding:5px 13px;font-size:0.78rem;font-weight:600;">{s}</span>'
            for s in SPECS
        ])
        st.markdown(f"""
        <div style="background:#fff;border:1px solid #E2E8F0;border-radius:16px;
                    padding:1.4rem 1.6rem;margin-bottom:1.2rem;box-shadow:0 2px 10px rgba(0,0,0,0.05);">
            <div style="font-size:0.95rem;font-weight:700;color:#0F172A;margin-bottom:1rem;">🏥 Our Specializations</div>
            <div style="display:flex;flex-wrap:wrap;gap:8px;">{specs_pills}</div>
        </div>""", unsafe_allow_html=True)

        doc_cards = "".join([
            f"""<div style="display:flex;align-items:center;gap:10px;background:#F8FAFC;
                            border:1px solid #E2E8F0;border-radius:12px;padding:10px 12px;">
                    <div style="width:36px;height:36px;min-width:36px;
                                background:linear-gradient(135deg,#0F172A,#1D4ED8);
                                border-radius:50%;display:flex;align-items:center;
                                justify-content:center;font-size:1rem;">{emoji}</div>
                    <div>
                        <div style="font-size:0.8rem;font-weight:700;color:#0F172A;">{name}</div>
                        <div style="font-size:0.72rem;color:#64748B;margin-top:1px;">{spec}</div>
                    </div>
                </div>"""
            for name, spec, emoji in DOCTORS[:8]
        ])
        st.markdown(f"""
        <div style="background:#fff;border:1px solid #E2E8F0;border-radius:16px;
                    padding:1.4rem 1.6rem;margin-bottom:1.2rem;box-shadow:0 2px 10px rgba(0,0,0,0.05);">
            <div style="font-size:0.95rem;font-weight:700;color:#0F172A;margin-bottom:1rem;">👨‍⚕️ Our Doctors</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">{doc_cards}</div>
        </div>""", unsafe_allow_html=True)

        steps_data = [
            (1, "Set your Patient ID in the sidebar",   "#EFF6FF", "#1D4ED8"),
            (2, "Type your query in the chat box",       "#F0FDF4", "#16A34A"),
            (3, "Use date format: MM-DD-YYYY",           "#FFF7ED", "#C2410C"),
            (4, "Specify doctor name or specialization", "#FAF5FF", "#7C3AED"),
        ]
        steps_html = "".join([
            f"""<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
                    <div style="width:28px;height:28px;min-width:28px;background:{bg};color:{fg};
                                border-radius:50%;display:flex;align-items:center;justify-content:center;
                                font-size:0.78rem;font-weight:800;">{n}</div>
                    <span style="font-size:0.84rem;color:#374151;font-weight:500;">{text}</span>
                </div>"""
            for n, text, bg, fg in steps_data
        ])
        st.markdown(f"""
        <div style="background:#fff;border:1px solid #E2E8F0;border-radius:16px;
                    padding:1.4rem 1.6rem;box-shadow:0 2px 10px rgba(0,0,0,0.05);">
            <div style="font-size:0.95rem;font-weight:700;color:#0F172A;margin-bottom:1rem;">📖 How to Use</div>
            {steps_html}
            <div style="margin-top:1rem;background:#F0F9FF;border:1px solid #BAE6FD;
                        border-radius:10px;padding:12px 14px;">
                <div style="font-size:0.75rem;font-weight:700;color:#0369A1;margin-bottom:5px;">💬 Example Query</div>
                <div style="font-size:0.82rem;color:#0C4A6E;line-height:1.55;font-style:italic;">
                    "Is Dr. Jane Smith available on 7/15/2026 8:00 AM? My ID is 1234567"
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2.5rem 0 0.5rem;font-size:0.8rem;color:#94A3B8;
            border-top:1px solid #E2E8F0;margin-top:2rem;">
    <strong style="color:#475569;">DentaFlow</strong> &nbsp;·&nbsp;
    AI-Powered Doctor Appointment System &nbsp;·&nbsp;
    Built with LangGraph + FastAPI + Streamlit
</div>
""", unsafe_allow_html=True)
