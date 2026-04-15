import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver

# ── Persistent SQLite checkpointer ───────────────────────────────────────────
_conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=_conn)


def retrieve_all_threads() -> list[str]:
    """Return all thread IDs stored in the checkpointer."""
    return list(
        {cp.config["configurable"]["thread_id"] for cp in checkpointer.list(None)}
    )
