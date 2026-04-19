"""
Prompts for MCQ Generator.

Rate-limit-conscious design:
  - Concise instructions = fewer input tokens = lower TPM consumption
  - Explicit "be concise" in explanation field saves output tokens
  - No ChatPromptTemplate — direct f-string formatting
"""

MCQ_GENERATION_PROMPT = """You are an expert MCQ designer. Generate exactly {num_questions} high-quality MCQs from the notes below.

NOTES:
{notes}

━━━ RULES ━━━

QUESTION STYLE — vary these types evenly:
• conceptual  → tests WHY/HOW a mechanism works (not definitions)
• application → real scenario, asks what happens or what to do
• inference   → connect multiple concepts to reach a conclusion

FORBIDDEN starters: "What is", "Which of the following is", "Define", "Name the"

OPTIONS — make wrong answers dangerous:
• All 4 options must be plausible
• Base each wrong option on a real misconception or subtle logical error
• Change just ONE critical detail to flip correctness
• Vary which label (A/B/C/D) holds the correct answer

━━━ OUTPUT ━━━

Return ONLY valid JSON. No markdown. No explanation outside JSON.

{{
  "questions": [
    {{
      "question": "...",
      "options": [
        {{"label": "A", "text": "..."}},
        {{"label": "B", "text": "..."}},
        {{"label": "C", "text": "..."}},
        {{"label": "D", "text": "..."}}
      ],
      "correct_answer": "A",
      "explanation": "One or two sentences max.",
      "question_type": "conceptual",
      "difficulty": "medium"
    }}
  ],
  "topic_summary": "One sentence summary of the notes topic.",
  "total_questions": {num_questions}
}}

question_type must be: conceptual | application | inference
difficulty must be: easy | medium | hard
"""


REPAIR_PROMPT = """Fix ONLY the flagged MCQs below. Keep all other questions unchanged.

ERRORS:
{errors}

ORIGINAL JSON:
{raw_json}

Return the corrected full JSON in the exact same schema. No markdown. No extra text.
"""
