from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

import streamlit as st


# ── Initialise all session state keys ────────────────────────────────────────
def init_session_state() -> None:
    defaults = {
        "current_thread_id": None,
        # {thread_id: "Chat title"}
        "chat_titles": {},
        # Ordered list of thread_ids — index 0 = most recent
        "chat_order": [],
        # {thread_id: [{"role": "user"|"assistant", "content": "..."}]}
        "message_history_per_thread": {},
        # Rate-limit flag
        "rate_limited": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ── Thread helpers ────────────────────────────────────────────────────────────
def create_new_thread() -> str:
    """Create a new thread_id, register it, and make it active."""
    thread_id = str(uuid.uuid4())
    st.session_state["current_thread_id"] = thread_id
    st.session_state["message_history_per_thread"][thread_id] = []
    # Prepend so it appears at the top of the sidebar
    st.session_state["chat_order"].insert(0, thread_id)
    # Placeholder title until the first message arrives
    st.session_state["chat_titles"][thread_id] = "New chat"
    return thread_id


def switch_to_thread(thread_id: str) -> None:
    """Switch the active thread and bubble it to the top of chat_order."""
    st.session_state["current_thread_id"] = thread_id
    order: list = st.session_state["chat_order"]
    if thread_id in order:
        order.remove(thread_id)
    order.insert(0, thread_id)


def ensure_active_thread() -> str:
    """Return the active thread_id, creating one if none exists."""
    if not st.session_state["current_thread_id"]:
        return create_new_thread()
    return st.session_state["current_thread_id"]


# ── Title helpers ─────────────────────────────────────────────────────────────
def _truncate_to_words(text: str, max_words: int = 6) -> str:
    words = text.split()
    truncated = " ".join(words[:max_words])
    if len(words) > max_words:
        truncated += "…"
    return truncated


def set_title_from_first_message(thread_id: str, message: str) -> None:
    """Generate and save a title from the user's first message."""
    current_title = st.session_state["chat_titles"].get(thread_id, "New chat")
    if current_title == "New chat":
        st.session_state["chat_titles"][thread_id] = _truncate_to_words(message)


# ── Message helpers ───────────────────────────────────────────────────────────
def get_messages(thread_id: str) -> list[dict]:
    return st.session_state["message_history_per_thread"].get(thread_id, [])


def append_message(thread_id: str, role: str, content: str) -> None:
    history = st.session_state["message_history_per_thread"]
    if thread_id not in history:
        history[thread_id] = []
    history[thread_id].append({"role": role, "content": content})
