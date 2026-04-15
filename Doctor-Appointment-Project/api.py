"""
FastAPI backend for the Dental Appointment System.

Exposes a single endpoint:
    POST /execute   — accepts a message + patient_id, runs the LangGraph agent,
                      and returns the full message list so the Streamlit UI can
                      pick the last AI message.

Run with:
    uv run uvicorn api:app --host 0.0.0.0 --port 8003 --reload
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Any
import logging

from langchain_core.messages import HumanMessage

from dental_agent.agent import dental_graph

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="DentaFlow API",
    description="AI-powered dental appointment management backed by LangGraph + Groq (llama-3.1-8b-instant)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response schemas ─────────────────────────────────────────────────
class ExecuteRequest(BaseModel):
    messages: str                  # The user's text message
    id_number: Optional[int] = None  # Patient ID (optional; can be embedded in message)


class ExecuteResponse(BaseModel):
    messages: list[dict[str, Any]]
    status: str = "ok"


# ── Helper: serialise LangChain messages to plain dicts ───────────────────────
def _serialise_messages(messages: list) -> list[dict]:
    """Convert LangChain BaseMessage objects → plain dicts the UI can consume."""
    result = []
    for msg in messages:
        # BaseMessage has .type and .content; tool messages have .tool_call_id etc.
        msg_type = getattr(msg, "type", "unknown")
        content   = getattr(msg, "content", "")
        # Skip empty tool messages and intermediate tool-call chunks
        if msg_type == "tool":
            continue
        result.append({"type": msg_type, "role": msg_type, "content": content})
    return result


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "model": "llama-3.1-8b-instant"}


# ── Main endpoint (Streamlit UI calls POST /execute) ──────────────────────────
@app.post("/execute", response_model=ExecuteResponse)
def execute(request: ExecuteRequest):
    """
    Accepts a natural-language message and optional patient_id,
    runs it through the LangGraph dental agent, and returns the
    full conversation history as serialised dicts.
    """
    user_text = request.messages.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="'messages' field must not be empty.")

    # Optionally prepend patient ID so the agent always has it in context
    if request.id_number:
        user_text = f"[Patient ID: {request.id_number}] {user_text}"

    logger.info("Received request: %s", user_text[:120])

    # Use the patient ID as the thread_id for conversation memory
    thread_id = str(request.id_number) if request.id_number else "guest_session"

    try:
        result = dental_graph.invoke(
            {"messages": [HumanMessage(content=user_text)]},
            config={"recursion_limit": 20, "configurable": {"thread_id": thread_id}},
        )
        serialised = _serialise_messages(result.get("messages", []))
        logger.info("Agent returned %d messages", len(serialised))
        return ExecuteResponse(messages=serialised)

    except Exception as exc:
        logger.exception("Agent error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
