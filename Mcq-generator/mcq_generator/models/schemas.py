"""
Pydantic schemas for MCQ Generator.
All data contracts live here — single source of truth.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class MCQOption(BaseModel):
    """Single option for an MCQ question."""
    label: Literal["A", "B", "C", "D"]
    text: str = Field(..., min_length=1, description="Option text")


class MCQ(BaseModel):
    """A single multiple-choice question."""
    question: str = Field(..., min_length=10, description="The question text")
    options: List[MCQOption] = Field(..., min_length=4, max_length=4)
    correct_answer: Literal["A", "B", "C", "D"] = Field(
        ..., description="Label of the correct option"
    )
    explanation: str = Field(
        ..., min_length=10, description="Why the correct answer is correct"
    )
    question_type: Literal["conceptual", "application", "inference"] = Field(
        ..., description="Cognitive level of the question"
    )
    difficulty: Literal["easy", "medium", "hard"] = Field(default="medium")

    @field_validator("options")
    @classmethod
    def options_must_be_unique(cls, v: List[MCQOption]) -> List[MCQOption]:
        texts = [o.text.strip().lower() for o in v]
        if len(texts) != len(set(texts)):
            raise ValueError("All options must have unique text")
        return v

    @field_validator("correct_answer")
    @classmethod
    def correct_answer_must_exist_in_options(
        cls, v: str, info
    ) -> str:
        if "options" in (info.data or {}):
            labels = [o.label for o in info.data["options"]]
            if v not in labels:
                raise ValueError(
                    f"correct_answer '{v}' not found in option labels {labels}"
                )
        return v


class MCQSet(BaseModel):
    """A validated set of MCQs."""
    questions: List[MCQ] = Field(..., min_length=1)
    topic_summary: str = Field(
        ..., description="Brief summary of the topic covered"
    )
    total_questions: int = Field(..., ge=1)

    @field_validator("total_questions")
    @classmethod
    def total_must_match_questions(cls, v: int, info) -> int:
        if "questions" in (info.data or {}):
            actual = len(info.data["questions"])
            if v != actual:
                raise ValueError(
                    f"total_questions={v} doesn't match len(questions)={actual}"
                )
        return v


# ── LangGraph State ──────────────────────────────────────────────────────────

class GraphState(BaseModel):
    """Shared state passed between LangGraph nodes."""
    notes: str = Field(..., description="Raw user-provided notes")
    num_questions: int = Field(default=5, ge=1, le=20)
    raw_llm_output: Optional[str] = Field(default=None)
    parsed_mcqs: Optional[List[MCQ]] = Field(default=None)
    validation_errors: List[str] = Field(default_factory=list)
    formatted_output: Optional[MCQSet] = Field(default=None)
    error: Optional[str] = Field(default=None)
    attempts: int = Field(default=0)

    class Config:
        arbitrary_types_allowed = True
