"""
agents/llm.py
Groq LLM singleton with rate-limit handling for free tier.
"""

import os
import time
from functools import lru_cache
from langchain_groq import ChatGroq

# Free-tier Groq: llama-3.1-8b-instant — 30 req/min, 6000 tokens/min
_LAST_CALL_TIME: float = 0.0
_MIN_INTERVAL: float = 2.5  # seconds between calls (safe for free tier)


def rate_limited_call(fn, *args, **kwargs):
    global _LAST_CALL_TIME
    elapsed = time.time() - _LAST_CALL_TIME
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)
    result = fn(*args, **kwargs)
    _LAST_CALL_TIME = time.time()
    return result


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
        max_tokens=1024,
    )
