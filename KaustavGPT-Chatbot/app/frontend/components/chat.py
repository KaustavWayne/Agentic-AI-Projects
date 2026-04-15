from __future__ import annotations
import re
import streamlit as st


def render_chat_history(messages: list[dict]) -> None:
    if not messages:
        _render_empty_state()
        return

    for msg in messages:
        role    = msg["role"]
        content = msg["content"]

        if role == "user":
            st.markdown(
                f"""
                <div class="user-row">
                    <div class="user-bubble">{content}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            _render_bot_message(content)


def _render_bot_message(content: str) -> None:
    """Render assistant message — prose as bubble, code as st.code, math as st.latex."""
    
    # Pattern order matters: check math first, then code
    # Split on ```code```, $latex$, $$latex$$
    segments = _parse_segments(content)
    
    has_special = any(s["type"] != "text" for s in segments)
    
    if not has_special:
        st.markdown(
            f"""
            <div class="bot-row">
                <div class="bot-avatar">K</div>
                <div class="bot-bubble">{_safe(content)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Has code/math — show avatar then render segments
    st.markdown(
        '<div class="bot-avatar" style="margin-bottom:6px;">K</div>',
        unsafe_allow_html=True,
    )
    for seg in segments:
        if seg["type"] == "text" and seg["content"].strip():
            st.markdown(
                f'<div class="bot-bubble" style="margin-bottom:8px;">{_safe(seg["content"])}</div>',
                unsafe_allow_html=True,
            )
        elif seg["type"] == "code":
            st.code(seg["content"], language=seg.get("lang") or "python")
        elif seg["type"] == "math_block":
            st.latex(seg["content"])
        elif seg["type"] == "math_inline":
            st.latex(seg["content"])


def _parse_segments(content: str) -> list[dict]:
    """Parse content into text, code, and math segments."""
    segments = []
    # Match ```code```, $$math$$, $math$
    pattern = r"(```(\w*)\n?([\s\S]*?)```|\$\$([\s\S]*?)\$\$|\$([^\$\n]+?)\$)"
    last_end = 0

    for match in re.finditer(pattern, content):
        start = match.start()
        # Text before this match
        if start > last_end:
            segments.append({"type": "text", "content": content[last_end:start]})

        full = match.group(0)
        if full.startswith("```"):
            lang = match.group(2) or "python"
            code = match.group(3)
            segments.append({"type": "code", "content": code, "lang": lang})
        elif full.startswith("$$"):
            segments.append({"type": "math_block", "content": match.group(4)})
        elif full.startswith("$"):
            segments.append({"type": "math_inline", "content": match.group(5)})

        last_end = match.end()

    # Remaining text
    if last_end < len(content):
        segments.append({"type": "text", "content": content[last_end:]})

    return segments

def _safe(text: str) -> str:
    """Escape HTML but preserve line breaks."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
    )


def render_thinking_indicator(label: str = "Thinking…") -> None:
    st.markdown(f"""
    <div class="thinking-row">
        <div class="bot-avatar" style="background:#111;color:#fff;font-size:11px;font-weight:700;
             width:28px;height:28px;border-radius:50%;display:flex;align-items:center;
             justify-content:center;flex-shrink:0;">K</div>
        <div class="thinking-dots">
            <div class="thinking-dot"></div>
            <div class="thinking-dot"></div>
            <div class="thinking-dot"></div>
        </div>
        <span class="thinking-label">{label}</span>
    </div>
    """, unsafe_allow_html=True)


def _render_empty_state() -> None:
    st.markdown("""
    <div class="empty-state">
        <div class="big-icon">✦</div>
        <div class="big-title">Kaustav GPT</div>
        <div class="big-sub">
            Ask me anything. Upload a PDF to chat with your documents.<br>
            I can search the web, look up stock prices, and calculate.
        </div>
    </div>
    """, unsafe_allow_html=True)