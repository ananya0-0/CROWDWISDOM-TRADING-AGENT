"""
core/llm_client.py
Thin wrapper around the OpenRouter API (OpenAI-compatible).
Centralizes model config, retry logic, and error handling.
"""

import os
import time

from openai import OpenAI, APIError, RateLimitError
from core.logger import get_logger

logger = get_logger(__name__)

# Free model on OpenRouter — swap this for any other free model if needed
DEFAULT_MODEL = "meta-llama/llama-3.3-70b-instruct:free"
MAX_RETRIES = 3


def get_client() -> OpenAI:
    """Initialize the OpenRouter client."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENROUTER_API_KEY is not set in environment variables.")
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1024,
) -> str:
    """
    Execute an LLM call with retry logic for rate limits.
    Returns the assistant's text response.
    """
    client = get_client()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.debug(f"LLM call attempt {attempt}/{MAX_RETRIES} | model={model}")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            logger.debug(f"LLM response received ({len(content)} chars).")
            return content

        except RateLimitError:
            wait = 2 ** attempt
            logger.warning(f"Rate limited. Waiting {wait}s before retry...")
            time.sleep(wait)

        except APIError as e:
            logger.error(f"OpenRouter API error: {e}")
            return f"[LLM Error] {str(e)}"

    logger.error("All LLM retries exhausted.")
    return "[LLM Error] Max retries exceeded. Please try again later."