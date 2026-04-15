from __future__ import annotations
import streamlit as st
from app.rag import ingest_pdf, thread_has_document, thread_document_metadata
from app.frontend.session import (
    create_new_thread, ensure_active_thread, switch_to_thread,
)


def render_sidebar() -> None:
    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="padding:20px 4px 14px; border-bottom:1px solid #e5e5e5; margin-bottom:10px;">
            <span style="font-size:17px; font-weight:700; color:#111; letter-spacing:-0.3px;">
                ✦ Kaustav GPT
            </span>
        </div>
        """, unsafe_allow_html=True)

        # New Chat
        if st.button("＋  New Chat", key="new_chat_btn", use_container_width=True):
            create_new_thread()
            st.rerun()

        # Chat history
        chat_order: list = st.session_state.get("chat_order", [])
        chat_titles: dict = st.session_state.get("chat_titles", {})
        active_tid = st.session_state.get("current_thread_id")

        if chat_order:
            st.markdown('<div class="section-label">Recent</div>', unsafe_allow_html=True)
            # Scrollable container — shows ALL chats, scrollable
            chat_container = st.container(height=int(400), border=False)
            with chat_container:
                for tid in chat_order:
                    title = chat_titles.get(tid, "New chat")
                    is_active = tid == active_tid
                    btn_type = "primary" if is_active else "secondary"
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        if st.button(title, key=f"chat_{tid}", use_container_width=True, type=btn_type):
                            switch_to_thread(tid)
                            st.rerun()
                    with col2:
                        with st.popover("⋯"):
                            st.markdown(
                                "<div style='font-size:13px; font-weight:600; color:#111; padding:4px 0 8px;'>"
                                "Delete this chat?</div>",
                                unsafe_allow_html=True
                            )
                            if st.button("🗑 Delete", key=f"confirm_del_{tid}", use_container_width=True):
                                st.session_state["chat_order"].remove(tid)
                                st.session_state["chat_titles"].pop(tid, None)
                                st.session_state["message_history_per_thread"].pop(tid, None)
                                try:
                                    import sqlite3
                                    conn = sqlite3.connect("chatbot.db")
                                    conn.execute("DELETE FROM checkpoints WHERE thread_id = ?", (tid,))
                                    conn.execute("DELETE FROM writes WHERE thread_id = ?", (tid,))
                                    conn.commit()
                                    conn.close()
                                except Exception:
                                    pass
                                if tid == active_tid:
                                    remaining = st.session_state["chat_order"]
                                    if remaining:
                                        switch_to_thread(remaining[0])
                                    else:
                                        create_new_thread()
                                st.rerun()

        st.markdown("---")
        st.markdown('<div class="section-label">Document</div>', unsafe_allow_html=True)
        _render_pdf_uploader()


def _render_pdf_uploader() -> None:
    thread_id = ensure_active_thread()

    if thread_has_document(thread_id):
        meta = thread_document_metadata(thread_id)
        st.success(
            f"📄 **{meta.get('filename', 'document')}**\n\n"
            f"{meta.get('documents', '?')} pages · {meta.get('chunks', '?')} chunks"
        )
        if st.button("Replace PDF", key="replace_pdf", use_container_width=True):
            st.rerun()
        return

    uploaded = st.file_uploader(
        "Upload PDF", type="pdf",
        label_visibility="collapsed",
        key=f"pdf_upload_{thread_id}",
    )
    if uploaded is not None:
        with st.spinner("Indexing…"):
            try:
                meta = ingest_pdf(
                    file_bytes=uploaded.read(),
                    thread_id=thread_id,
                    filename=uploaded.name,
                )
                st.success(f"✅ **{meta['filename']}**\n\n{meta['documents']} pages · {meta['chunks']} chunks")
                st.rerun()
            except Exception as exc:
                st.error(f"Ingestion failed: {exc}")
