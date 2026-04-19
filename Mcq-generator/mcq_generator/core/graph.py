"""
LangGraph Workflow: MCQ Generator Pipeline
Rate-limit-safe + robust JSON extraction.
"""
import json
import re
import time
import logging
from typing import Any

from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.graph import StateGraph, END

from models.schemas import GraphState, MCQ, MCQSet
from core.llm_client import get_llm, get_plain_llm, invoke_with_retry
from prompts.mcq_prompts import MCQ_GENERATION_PROMPT, REPAIR_PROMPT
from tools.validation_tool import validate_mcqs

logger = logging.getLogger(__name__)

MAX_RETRIES = 2


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> str:
    """
    Robustly extract the first complete {...} JSON block from LLM output.
    Handles markdown fences, extra prose before/after, nested braces.
    """
    if not text:
        return "{}"

    # Strip markdown fences
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE)
    text = text.strip().strip("`").strip()

    # Find outermost { ... }
    start = text.find("{")
    if start == -1:
        return "{}"

    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start: i + 1]

    # Unclosed brace — return what we have and let json.loads error gracefully
    return text[start:]


def _parse_mcqs(raw: str) -> tuple[list[MCQ] | None, list[str]]:
    """Parse raw LLM output into MCQ objects. Returns (mcqs, errors)."""
    errors: list[str] = []

    if not raw or not raw.strip():
        return None, ["LLM returned empty response"]

    json_str = _extract_json(raw)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error("JSON decode failed. Raw output:\n%s", raw[:500])
        return None, [f"JSON parse error: {e}. Raw snippet: {raw[:200]}"]

    questions_data = data.get("questions", [])

    if not questions_data:
        logger.error("Parsed JSON has no 'questions' key. Data keys: %s", list(data.keys()))
        return None, [f"No 'questions' key in LLM output. Got keys: {list(data.keys())}"]

    mcqs: list[MCQ] = []
    for idx, q in enumerate(questions_data):
        try:
            for opt in q.get("options", []):
                opt["label"] = opt.get("label", "").upper()
            q["correct_answer"] = q.get("correct_answer", "").upper()
            mcqs.append(MCQ(**q))
        except Exception as e:
            errors.append(f"Q{idx + 1} schema error: {e}")

    if not mcqs:
        return None, errors or ["All questions failed schema validation"]

    return mcqs, errors


# ── Nodes ─────────────────────────────────────────────────────────────────────

def generator_node(state: GraphState) -> dict[str, Any]:
    """
    Calls Groq LLM. Uses tool-bound LLM first; falls back to plain LLM
    if tool-call loop produces empty content (common with instant models).
    """
    state_dict = state.model_dump()

    if state_dict["attempts"] == 0 or not state_dict["raw_llm_output"]:
        prompt = MCQ_GENERATION_PROMPT.format(
            notes=state_dict["notes"],
            num_questions=state_dict["num_questions"],
        )
    else:
        prompt = REPAIR_PROMPT.format(
            errors="\n".join(state_dict["validation_errors"]),
            raw_json=state_dict["raw_llm_output"] or "{}",
        )

    messages = [HumanMessage(content=prompt)]
    raw_output = ""

    # ── Strategy 1: tool-bound LLM ──
    try:
        llm = get_llm()
        response = invoke_with_retry(llm, messages)
        messages.append(response)

        tool_calls = getattr(response, "tool_calls", []) or []

        if tool_calls:
            # Execute tool locally and feed result back
            for tc in tool_calls:
                if tc["name"] == "validate_mcqs":
                    try:
                        tool_result = validate_mcqs.invoke(tc["args"])
                    except Exception as e:
                        tool_result = json.dumps({"valid": False, "errors": [str(e)]})
                    messages.append(
                        ToolMessage(content=tool_result, tool_call_id=tc["id"])
                    )

            # One more call to get final text after tool result
            final_response = invoke_with_retry(llm, messages)
            raw_output = final_response.content or ""
        else:
            raw_output = response.content or ""

    except Exception as e:
        logger.warning("Tool-bound LLM failed: %s. Falling back to plain LLM.", e)
        raw_output = ""

    # ── Strategy 2: plain LLM fallback if output is empty ──
    if not raw_output or not raw_output.strip() or "{" not in raw_output:
        logger.warning("Tool-bound LLM returned empty/invalid output. Using plain LLM fallback.")
        try:
            plain_llm = get_plain_llm()
            plain_messages = [HumanMessage(content=prompt)]
            plain_response = invoke_with_retry(plain_llm, plain_messages)
            raw_output = plain_response.content or ""
        except Exception as e:
            logger.error("Plain LLM fallback also failed: %s", e)
            raw_output = ""

    logger.info("Raw LLM output (first 300 chars): %s", raw_output[:300])

    return {
        "raw_llm_output": raw_output,
        "attempts": state_dict["attempts"] + 1,
        "validation_errors": [],
    }


def validator_node(state: GraphState) -> dict[str, Any]:
    """Pure-Python validation — zero API calls."""
    raw = state.raw_llm_output or ""
    mcqs, errors = _parse_mcqs(raw)

    if not mcqs:
        return {
            "parsed_mcqs": None,
            "validation_errors": errors or ["No questions parsed"],
        }

    # Local tool validation
    questions_dicts = [
        {
            "question": q.question,
            "options": [{"label": o.label, "text": o.text} for o in q.options],
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "question_type": q.question_type,
            "difficulty": q.difficulty,
        }
        for q in mcqs
    ]

    try:
        tool_result = json.loads(validate_mcqs.invoke({"questions": questions_dicts}))
        if not tool_result["valid"]:
            return {
                "parsed_mcqs": mcqs,
                "validation_errors": tool_result["errors"],
            }
    except Exception as e:
        logger.warning("Local validation tool error (non-fatal): %s", e)

    return {"parsed_mcqs": mcqs, "validation_errors": []}


def formatter_node(state: GraphState) -> dict[str, Any]:
    """Assemble final MCQSet. No API call."""
    mcqs = state.parsed_mcqs or []
    raw = state.raw_llm_output or "{}"

    topic_summary = "Summary of the provided notes."
    try:
        data = json.loads(_extract_json(raw))
        topic_summary = data.get("topic_summary", topic_summary)
    except Exception:
        pass

    return {
        "formatted_output": MCQSet(
            questions=mcqs,
            topic_summary=topic_summary,
            total_questions=len(mcqs),
        )
    }


# ── Conditional Edge ──────────────────────────────────────────────────────────

def should_retry(state: GraphState) -> str:
    if state.validation_errors and state.attempts < MAX_RETRIES:
        logger.warning(
            "Retry %d/%d — errors: %s",
            state.attempts, MAX_RETRIES, state.validation_errors,
        )
        time.sleep(3)
        return "generator"
    if state.validation_errors:
        logger.error("Max retries reached. Partial results will be used.")
    return "formatter"


# ── Graph ─────────────────────────────────────────────────────────────────────

def build_graph() -> Any:
    builder = StateGraph(GraphState)
    builder.add_node("generator", generator_node)
    builder.add_node("validator", validator_node)
    builder.add_node("formatter", formatter_node)
    builder.set_entry_point("generator")
    builder.add_edge("generator", "validator")
    builder.add_conditional_edges(
        "validator",
        should_retry,
        {"generator": "generator", "formatter": "formatter"},
    )
    builder.add_edge("formatter", END)
    return builder.compile()


mcq_graph = build_graph()
