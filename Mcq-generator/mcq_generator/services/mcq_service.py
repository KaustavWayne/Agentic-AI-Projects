"""
Service layer — single public entry point for MCQ generation.
Streamlit calls this; knows nothing about LangGraph internals.
"""
import logging
from typing import Optional
from models.schemas import GraphState, MCQSet
from core.graph import mcq_graph

logger = logging.getLogger(__name__)


class MCQGenerationError(Exception):
    """Raised when generation fails after all retries."""


def generate_mcqs(notes: str, num_questions: int = 5) -> MCQSet:
    """
    Generate MCQs from user notes.

    Args:
        notes: Raw study notes / text content.
        num_questions: Number of questions to generate (1–20).

    Returns:
        MCQSet with validated questions.

    Raises:
        MCQGenerationError: If generation fails entirely.
        ValueError: If inputs are invalid.
    """
    notes = notes.strip()
    if len(notes) < 50:
        raise ValueError("Notes are too short. Provide at least 50 characters.")
    if not 1 <= num_questions <= 20:
        raise ValueError("num_questions must be between 1 and 20.")

    initial_state = GraphState(notes=notes, num_questions=num_questions)

    try:
        final_state = mcq_graph.invoke(initial_state)
    except Exception as e:
        logger.exception("LangGraph execution failed")
        raise MCQGenerationError(f"MCQ generation pipeline failed: {e}") from e

    # final_state is a dict when returned from LangGraph
    if isinstance(final_state, dict):
        formatted = final_state.get("formatted_output")
        errors = final_state.get("validation_errors", [])
    else:
        formatted = getattr(final_state, "formatted_output", None)
        errors = getattr(final_state, "validation_errors", [])

    if formatted is None:
        raise MCQGenerationError(
            f"No output produced. Last errors: {errors}"
        )

    if not formatted.questions:
        raise MCQGenerationError("Generated MCQ set is empty.")

    logger.info(
        "Successfully generated %d MCQs in %d attempt(s)",
        len(formatted.questions),
        final_state.get("attempts", "?") if isinstance(final_state, dict) else "?",
    )
    return formatted
