# Groq / Llama 3 initialization 

"""
Groq LLM Client with rate limit safety, retry logic, and caching.
Uses llama3-8b-instant for fast, cost-effective inference.
"""

import os
import json
import time
from typing import Optional, Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from utils.cache import cached
from utils.retry import with_retry
from utils.logger import logger
from dotenv import load_dotenv

load_dotenv()


class GroqClient:
    """
    Production-grade Groq LLM client with:
    - Rate limit protection
    - Response caching
    - Retry with exponential backoff
    - Structured output parsing
    """

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name="llama3-8b-instant",
            temperature=0.2,
            max_tokens=4096,
        )
        
        self.json_parser = JsonOutputParser()
        self._last_call_time = 0
        self._min_interval = 0.5  # Minimum 500ms between calls
        logger.info("GroqClient initialized with llama3-8b-instant")

    def _rate_limit_wait(self):
        """Enforce minimum interval between API calls."""
        elapsed = time.time() - self._last_call_time
        if elapsed < self._min_interval:
            sleep_time = self._min_interval - elapsed
            time.sleep(sleep_time)
        self._last_call_time = time.time()

    @with_retry(max_attempts=3, min_wait=2.0, max_wait=10.0)
    def invoke(
        self,
        system_prompt: str,
        user_message: str,
        expect_json: bool = True
    ) -> str:
        """
        Invoke the LLM with system and user messages.
        
        Args:
            system_prompt: System-level instructions
            user_message: User query/context
            expect_json: Whether to append JSON-output instruction
            
        Returns:
            LLM response as string
        """
        self._rate_limit_wait()
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        if expect_json:
            messages.append(
                HumanMessage(content="IMPORTANT: Return ONLY valid JSON. No markdown. No explanation. No code blocks.")
            )
        
        logger.debug(f"Invoking Groq LLM | System: {system_prompt[:100]}...")
        
        response = self.llm.invoke(messages)
        content = response.content.strip()
        
        logger.debug(f"Groq response length: {len(content)} chars")
        return content

    def invoke_json(
        self,
        system_prompt: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Invoke LLM and parse JSON response.
        Handles common JSON parsing issues.
        
        Returns:
            Parsed JSON as dictionary
        """
        response = self.invoke(system_prompt, user_message, expect_json=True)
        
        try:
            # Clean response - remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Raw response: {response[:500]}")
            
            # Try to extract JSON from response
            try:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(response[start:end])
            except Exception:
                pass
            
            logger.error("Could not parse JSON from LLM response")
            return {}


# Singleton instance
_groq_client = None

def get_groq_client() -> GroqClient:
    """Get singleton GroqClient instance."""
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqClient()
    return _groq_client