from __future__ import annotations
import time
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from app.graph import chatbot
from app.database import checkpointer
from app.frontend.session import (
    append_message, ensure_active_thread, get_messages,
    init_session_state, set_title_from_first_message,
)
from app.frontend.styles import SIDEBAR_CSS
from app.frontend.components import render_sidebar, render_chat_history, render_thinking_indicator

_MAX_RETRIES = 4
_BASE_WAIT   = 8


def _load_thread_from_db(thread_id: str) -> None:
    """
    Restore message history from SQLite checkpointer into session state.
    Called once per thread when switching or on page reload.
    """
    history = st.session_state["message_history_per_thread"]
    # Only load if not already in memory
    if thread_id in history and history[thread_id]:
        return
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state  = chatbot.get_state(config)
        if not state or not state.values:
            return
        msgs = state.values.get("messages", [])
        loaded = []
        for m in msgs:
            if isinstance(m, HumanMessage):
                loaded.append({"role": "user", "content": m.content})
            elif isinstance(m, AIMessage):
                content = m.content
                if isinstance(content, list):
                    content = " ".join(
                        b.get("text", "") if isinstance(b, dict) else str(b)
                        for b in content
                    )
                if content:  # skip empty tool-call messages
                    loaded.append({"role": "assistant", "content": str(content)})
        if loaded:
            history[thread_id] = loaded
            # Restore title from first human message
            first_user = next((m["content"] for m in loaded if m["role"] == "user"), None)
            if first_user:
                words = first_user.split()
                title = " ".join(words[:6]) + ("…" if len(words) > 6 else "")
                st.session_state["chat_titles"][thread_id] = title
    except Exception:
        pass  # silently skip if checkpoint not found


def _load_all_threads_from_db() -> None:
    if st.session_state.get("_db_loaded"):
        return
    st.session_state["_db_loaded"] = True  # set FIRST — prevents blank screen loop on crash
    try:
        seen_order = []
        checkpoints = list(checkpointer.list(None))
        for cp in checkpoints:
            try:
                tid = cp.config["configurable"]["thread_id"]
            except Exception:
                continue
            if tid in seen_order:
                continue
            seen_order.append(tid)

            if tid not in st.session_state["message_history_per_thread"]:
                st.session_state["message_history_per_thread"][tid] = []

            # Restore real title immediately from checkpoint
            if st.session_state["chat_titles"].get(tid, "New chat") == "New chat":
                try:
                    state = chatbot.get_state({"configurable": {"thread_id": tid}})
                    if state and state.values:
                        msgs = state.values.get("messages", [])
                        first_human = next(
                            (m.content for m in msgs if isinstance(m, HumanMessage)),
                            None,
                        )
                        if first_human and isinstance(first_human, str):
                            words = first_human.split()
                            title = " ".join(words[:6]) + ("…" if len(words) > 6 else "")
                            st.session_state["chat_titles"][tid] = title
                        else:
                            st.session_state["chat_titles"][tid] = "New chat"
                except Exception:
                    st.session_state["chat_titles"][tid] = "New chat"

        existing = st.session_state["chat_order"]
        merged = seen_order + [t for t in existing if t not in seen_order]
        st.session_state["chat_order"] = merged
    except Exception:
        pass


def _invoke_with_retry(thread_id: str, user_message: str) -> str:
    config      = {"configurable": {"thread_id": thread_id}}
    messages_in = [HumanMessage(content=user_message)]
    for attempt in range(_MAX_RETRIES):
        try:
            result = chatbot.invoke({"messages": messages_in}, config=config)
            last = result["messages"][-1]
            if hasattr(last, "content"):
                content = last.content
                if isinstance(content, list):
                    return " ".join(
                        b.get("text", "") if isinstance(b, dict) else str(b)
                        for b in content
                    )
                return str(content)
            return str(last)
        except Exception as exc:
            err = str(exc).lower()
            if "rate_limit" in err or "rate limit" in err or "429" in err:
                if attempt < _MAX_RETRIES - 1:
                    wait = _BASE_WAIT * (2 ** attempt)
                    st.warning(f"⚠️ Rate limit — retrying in {wait}s… ({attempt+1}/{_MAX_RETRIES})")
                    time.sleep(wait)
                else:
                    return "⚠️ Rate limit reached. Please wait a moment."
            else:
                return f"❌ Error: {exc}"
    return "❌ Failed after retries."


def _typewriter(text: str, container) -> None:
    import re
    from app.frontend.components.chat import _render_bot_message

    if "```" in text:
        # For code: show a brief "writing code..." animation then render
        for label in ["Writing code .", "Writing code ..", "Writing code ..."]:
            container.markdown(
                f"""
                <div class="thinking-row">
                    <div class="bot-avatar" style="background:#111;color:#fff;font-size:11px;
                         font-weight:700;width:28px;height:28px;border-radius:50%;
                         display:flex;align-items:center;justify-content:center;">K</div>
                    <span class="thinking-label">{label}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            time.sleep(0.4)
        container.empty()
        with container:
            _render_bot_message(text)
        return

    # Pure text — word by word typewriter
    displayed = ""
    words = text.split(" ")
    for i, word in enumerate(words):
        displayed += ("" if i == 0 else " ") + word
        container.markdown(
            f"""
            <div class="bot-row">
                <div class="bot-avatar">K</div>
                <div class="bot-bubble">{displayed}▌</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        time.sleep(0.025)
    container.markdown(
        f"""
        <div class="bot-row">
            <div class="bot-avatar">K</div>
            <div class="bot-bubble">{displayed}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="Kaustav GPT",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)
    init_session_state()

    # ── Restore persisted threads on first load ────────────────────────────
    _load_all_threads_from_db()

    render_sidebar()

    thread_id = ensure_active_thread()

    # ── Load this thread's messages from DB if needed ──────────────────────
    _load_thread_from_db(thread_id)

    messages = get_messages(thread_id)
    # title    = st.session_state["chat_titles"].get(thread_id, "New chat")

    # # Header
    # st.markdown(f"""
    # <div style="padding:16px 0 12px; border-bottom:1px solid #eee; margin-bottom:4px;
    #             max-width:780px; margin-left:auto; margin-right:auto;">
    #     <span style="font-size:14px; font-weight:600; color:#555;">{title}</span>
    # </div>
    # """, unsafe_allow_html=True)
    # Header — always show brand quote, not chat title
    st.markdown("""
    <div style="padding:16px 0 12px; border-bottom:1px solid #eee; margin-bottom:4px;
                max-width:780px; margin-left:auto; margin-right:auto;
                display:flex; align-items:baseline; gap:10px;">
        <span style="font-size:15px; font-weight:700; color:#111;">Kaustav GPT</span>
        <span style="font-size:13px; color:#aaa; font-style:italic;">— here to change your world, one answer at a time</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Render existing messages ───────────────────────────────────────────
    render_chat_history(messages)

    # ── STEP 2: pending message → run LLM + stream response ───────────────
    if st.session_state.get("pending_message"):
        pending = st.session_state.pop("pending_message")

        # Show thinking indicator
        thinking_slot = st.empty()
        with thinking_slot:
            render_thinking_indicator("Thinking…")

        response = _invoke_with_retry(thread_id, pending)
        thinking_slot.empty()

        # Typewriter effect in a dedicated slot
        stream_slot = st.empty()
        _typewriter(response, stream_slot)

        append_message(thread_id, "assistant", response)
        st.rerun()

    # ── Chat input ─────────────────────────────────────────────────────────
    user_input = st.chat_input("Message Kaustav GPT…")

    if user_input and user_input.strip():
        user_text = user_input.strip()
        set_title_from_first_message(thread_id, user_text)
        append_message(thread_id, "user", user_text)
        st.session_state["pending_message"] = user_text
        st.rerun()
