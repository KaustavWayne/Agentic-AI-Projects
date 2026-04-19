"""
MCQ Validation Tool — bound to the Groq LLM via tool calling.

This tool is the quality gate. The LLM calls it internally to self-validate
each question before the output leaves the generator node.
"""
import json
from typing import List
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class MCQValidationInput(BaseModel):
    """Input schema for the MCQ validation tool."""
    questions: List[dict] = Field(
        ...,
        description=(
            "List of MCQ dicts. Each must have: question, options (list of "
            "{label, text}), correct_answer, explanation, question_type, difficulty."
        ),
    )


@tool(args_schema=MCQValidationInput)
def validate_mcqs(questions: List[dict]) -> str:
    """
    Validates a list of MCQs for structural correctness.

    Checks performed:
    1. Each question has exactly 4 options labelled A–D.
    2. The correct_answer label exists in the options.
    3. No two options have identical text (case-insensitive).
    4. No two questions are identical.
    5. explanation, question_type, and difficulty fields are present.

    Returns a JSON object with 'valid' (bool), 'errors' (list), and
    'valid_questions' (list of indices that passed).
    """
    errors: List[str] = []
    valid_indices: List[int] = []
    seen_questions: set = set()

    required_labels = {"A", "B", "C", "D"}

    for idx, q in enumerate(questions):
        q_errors = []

        # Check required top-level keys
        for key in ["question", "options", "correct_answer", "explanation",
                    "question_type", "difficulty"]:
            if key not in q:
                q_errors.append(f"Missing field: '{key}'")

        if q_errors:
            errors.append(f"Q{idx + 1}: {'; '.join(q_errors)}")
            continue

        # Duplicate question check
        q_text = q["question"].strip().lower()
        if q_text in seen_questions:
            q_errors.append("Duplicate question text detected")
        seen_questions.add(q_text)

        # Options validation
        opts = q.get("options", [])
        if len(opts) != 4:
            q_errors.append(f"Expected 4 options, got {len(opts)}")
        else:
            labels = {o.get("label", "").upper() for o in opts}
            if labels != required_labels:
                q_errors.append(f"Option labels must be A/B/C/D, got {labels}")

            # Duplicate option text
            texts = [o.get("text", "").strip().lower() for o in opts]
            if len(texts) != len(set(texts)):
                q_errors.append("Duplicate option texts found")

            # Correct answer exists
            correct = q.get("correct_answer", "").upper()
            if correct not in labels:
                q_errors.append(
                    f"correct_answer='{correct}' not in option labels {labels}"
                )

        # question_type check
        valid_types = {"conceptual", "application", "inference"}
        if q.get("question_type") not in valid_types:
            q_errors.append(
                f"question_type must be one of {valid_types}, "
                f"got '{q.get('question_type')}'"
            )

        if q_errors:
            errors.append(f"Q{idx + 1}: {'; '.join(q_errors)}")
        else:
            valid_indices.append(idx)

    result = {
        "valid": len(errors) == 0,
        "total_checked": len(questions),
        "valid_count": len(valid_indices),
        "errors": errors,
        "valid_question_indices": valid_indices,
    }
    return json.dumps(result, indent=2)


# Export tools list for LLM binding
MCQ_TOOLS = [validate_mcqs]
