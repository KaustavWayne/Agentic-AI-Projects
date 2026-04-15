SIDEBAR_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #ffffff !important;
    color: #111111 !important;
    font-family: 'Inter', sans-serif !important;
}

#MainMenu, footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

[data-testid="stSidebar"] {
    background-color: #f7f7f8 !important;
    border-right: 1px solid #e5e5e5 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 12px 12px 12px !important;
}

.stButton > button {
    background: #ffffff !important;
    color: #111 !important;
    border: 1px solid #d9d9d9 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 7px 12px !important;
    width: 100% !important;
    text-align: left !important;
    transition: background 0.15s !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: #f0f0f0 !important;
    border-color: #bbb !important;
}
button[kind="primary"] {
    background: #efefef !important;
    border-color: #333 !important;
    font-weight: 600 !important;
    color: #000 !important;
}

.section-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: #999;
    padding: 12px 2px 6px;
}

hr { border: none !important; border-top: 1px solid #e5e5e5 !important; margin: 8px 0 !important; }

.chat-wrapper { max-width: 680px; margin: 0 auto; padding: 16px 8px 100px; }

.user-row { display: flex; justify-content: flex-end; margin-bottom: 16px; }
.user-bubble {
    background: #111111; color: #ffffff;
    padding: 10px 16px;
    border-radius: 18px 18px 4px 18px;
    max-width: 75%; font-size: 14px; line-height: 1.6; word-wrap: break-word;
}

.bot-row { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 16px; }
.bot-avatar {
    width: 28px; height: 28px; border-radius: 50%;
    background: #111; color: #fff;
    font-size: 11px; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; margin-top: 2px;
}
.bot-bubble {
    background: #f7f7f8; border: 1px solid #e8e8e8; color: #111111;
    padding: 10px 16px;
    border-radius: 4px 18px 18px 18px;
    max-width: 80%; font-size: 14px; line-height: 1.7; word-wrap: break-word;
}

.thinking-row { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; padding: 8px 0; }
.thinking-dots { display: flex; gap: 4px; align-items: center; }
.thinking-dot { width: 7px; height: 7px; border-radius: 50%; background: #999; animation: bounce 1.2s ease infinite; }
.thinking-dot:nth-child(2) { animation-delay: 0.2s; }
.thinking-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%, 80%, 100% { transform: scale(0.75); opacity: 0.4; }
    40% { transform: scale(1.1); opacity: 1; }
}
.thinking-label { font-size: 13px; color: #888; font-style: italic; }

.empty-state { text-align: center; padding: 80px 20px 40px; }
.empty-state .big-icon { font-size: 36px; margin-bottom: 12px; }
.empty-state .big-title { font-size: 22px; font-weight: 700; color: #111; margin-bottom: 8px; }
.empty-state .big-sub { font-size: 13px; color: #999; line-height: 1.7; }

[data-testid="stChatInput"] {
    padding: 12px 0 !important;
}
[data-testid="stChatInput"] > div {
    background: #ffffff !important;
    border: 1.5px solid #c8c8c8 !important;
    border-radius: 999px !important;
    max-width: 780px !important;
    width: 100% !important;
    margin: 0 auto !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08) !important;
    min-height: 52px !important;
    padding: 6px 16px !important;
    display: flex !important;
    align-items: center !important;
}
[data-testid="stChatInput"] textarea {
    color: #111111 !important;
    background: transparent !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    min-height: 36px !important;
    max-height: 200px !important;
    padding: 8px 0 !important;
    line-height: 1.5 !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #aaa !important; }
[data-testid="stChatInput"] button {
    border-radius: 50% !important;
    background: #111 !important;
    color: #fff !important;
    width: 32px !important;
    height: 32px !important;
}

[data-testid="stFileUploader"] {
    background: #f7f7f8 !important;
    border: 1.5px dashed #d0d0d0 !important;
    border-radius: 10px !important;
}

.stSuccess { background: #f0faf4 !important; border-color: #34d399 !important; color: #065f46 !important; }
.stInfo    { background: #eff6ff !important; border-color: #60a5fa !important; color: #1e40af !important; }
.stWarning { background: #fffbeb !important; border-color: #fbbf24 !important; color: #92400e !important; }
.stError   { background: #fef2f2 !important; border-color: #f87171 !important; color: #991b1b !important; }
[data-testid="stAlert"] { border-radius: 10px !important; font-size: 13px !important; }

/* ── Scrollable chat history ── */
.chat-scroll-area {
    max-height: calc(100vh - 280px);
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 2px;
}
.chat-scroll-area::-webkit-scrollbar { width: 3px; }
.chat-scroll-area::-webkit-scrollbar-thumb { background: #ddd; border-radius: 4px; }
.chat-scroll-area::-webkit-scrollbar-track { background: transparent; }

/* ── Three dot button ── */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
    gap: 0px !important;
    margin-bottom: 2px !important;
    align-items: center !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child button {
    background: transparent !important;
    border: none !important;
    color: #999 !important;
    font-size: 18px !important;
    font-weight: 900 !important;
    padding: 2px 6px !important;
    min-height: 34px !important;
    width: 32px !important;
    box-shadow: none !important;
    line-height: 1 !important;
    letter-spacing: 1px !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child button:hover {
    color: #333 !important;
    background: #ececec !important;
    border-radius: 6px !important;
}
/* Chat title button */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:first-child button {
    border-radius: 8px !important;
    text-align: left !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}

/* ── Popover panel ── */
div[data-testid="stPopover"] div[role="dialog"] {
    padding: 8px !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.12) !important;
    border: 1px solid #eee !important;
    min-width: 160px !important;
}
[data-testid="stPopoverBody"] { padding: 6px !important; }

/* Delete button inside popover */
div[data-testid="stPopover"] button {
    background: #fff5f5 !important;
    color: #e53e3e !important;
    border: 1px solid #fca5a5 !important;
    border-radius: 7px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 6px 12px !important;
    width: 100% !important;
    text-align: left !important;
}
div[data-testid="stPopover"] button:hover {
    background: #e53e3e !important;
    color: #fff !important;
    border-color: #e53e3e !important;
}
</style>
"""
