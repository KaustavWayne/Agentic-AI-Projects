"""
Groq LLM client — with rate-limit-safe exponential backoff.

Free tier limits for llama-3.1-8b-instant:
  - 30 requests/minute (RPM)
  - 131,072 tokens/minute (TPM)
  - 14,400 requests/day

Strategy:
  - Catch HTTP 429 (rate limit) and retry with exponential backoff
  - Reduce max_tokens to consume fewer TPM per call
  - Single cached LLM instance (no re-init per request)
"""
import os
import time
import logging
from functools import lru_cache
from langchain_groq import ChatGroq
from tools.validation_tool import MCQ_TOOLS

logger = logging.getLogger(__name__)

# Correct model name for Groq
MODEL_NAME   = "llama-3.1-8b-instant"
MAX_TOKENS   = 2048   # Reduced from 4096 — saves TPM, still enough for MCQs
TEMPERATURE  = 0.7


def _make_llm(temperature: float = TEMPERATURE, bind_tools: bool = True) -> ChatGroq:
    """Create a ChatGroq instance, optionally with tools bound."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. Get a free key at https://console.groq.com"
        )
    llm = ChatGroq(
        model=MODEL_NAME,
        temperature=temperature,
        groq_api_key=api_key,
        max_tokens=MAX_TOKENS,
    )
    return llm.bind_tools(MCQ_TOOLS) if bind_tools else llm


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    """Cached LLM with validation tool bound. Used in generator node."""
    return _make_llm(bind_tools=True)


@lru_cache(maxsize=1)
def get_plain_llm() -> ChatGroq:
    """Cached plain LLM without tools. Used in formatter node."""
    return _make_llm(bind_tools=False)


def invoke_with_retry(llm, messages: list, max_retries: int = 4) -> object:
    """
    Invoke the LLM with exponential backoff on rate-limit errors (HTTP 429).

    Backoff schedule (seconds): 10 → 20 → 40 → 80
    Covers burst rate limits (per-minute) gracefully.
    """
    delay = 10  # start with 10s — enough to clear a 30 RPM window burst

    for attempt in range(max_retries):
        try:
            return llm.invoke(messages)

        except Exception as e:
            err_str = str(e).lower()

            # Detect rate limit — Groq returns 429 or "rate_limit_exceeded"
            is_rate_limit = (
                "429" in err_str
                or "rate limit" in err_str
                or "rate_limit" in err_str
                or "too many requests" in err_str
            )

            if is_rate_limit and attempt < max_retries - 1:
                logger.warning(
                    "Rate limit hit (attempt %d/%d). Waiting %ds before retry...",
                    attempt + 1, max_retries, delay,
                )
                time.sleep(delay)
                delay = min(delay * 2, 90)  # cap at 90s
                continue

            # Not a rate limit error, or final attempt — re-raise
            raise

    raise RuntimeError("Max retries exceeded due to rate limiting.")
