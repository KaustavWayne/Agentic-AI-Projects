# LLM call retry logic 

"""
Retry logic with exponential backoff for API calls.
Handles rate limits and transient failures gracefully.
"""

import time
import functools
from typing import Callable, Tuple, Type, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError
)
import logging
from utils.logger import logger


def with_retry(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator that adds retry logic with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)
        exceptions: Exception types to retry on
    """
    def decorator(func: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            retry=retry_if_exception_type(exceptions),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True
        )
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default: Any = None, **kwargs) -> Any:
    """
    Safely execute a function and return default on failure.
    Logs the error without raising.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Safe execute failed for {func.__name__}: {str(e)}")
        return default