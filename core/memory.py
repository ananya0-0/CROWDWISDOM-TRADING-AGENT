"""
core/memory.py
Manages the Closed Learning Loop — persisting structured feedback across sessions.
Each memory entry stores the original query, the advice given, and user feedback,
giving the LLM full context to improve over time.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from core.logger import get_logger

logger = get_logger(__name__)

MEMORY_FILE = Path("data/learning_loop_memory.json")


def load_memory() -> dict:
    """Load memory from disk. Returns empty structure if file doesn't exist."""
    MEMORY_FILE.parent.mkdir(exist_ok=True)
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"Loaded {len(data.get('lessons', []))} lessons from memory.")
            return data
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load memory file: {e}. Starting fresh.")
    return {"lessons": []}


def save_memory(memory: dict) -> None:
    """Persist memory to disk."""
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2)
        logger.debug("Memory saved to disk.")
    except IOError as e:
        logger.error(f"Failed to save memory: {e}")


def add_lesson(memory: dict, query: str, advice: str, feedback: str) -> dict:
    """
    Add a structured lesson to the learning loop.
    Stores the query context so the agent knows *why* feedback was given.
    """
    lesson = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_query": query,
        "advice_given": advice[:500],  # Truncate to avoid massive prompts
        "user_feedback": feedback,
    }
    memory["lessons"].append(lesson)
    save_memory(memory)
    logger.info(f"New lesson recorded: '{feedback[:80]}'")
    return memory


def build_memory_context(memory: dict) -> str:
    """
    Formats recent lessons into a string to be injected into the LLM system prompt.
    Only uses the last 5 lessons to keep the context window manageable.
    """
    lessons = memory.get("lessons", [])
    if not lessons:
        return ""

    recent = lessons[-5:]
    lines = ["PAST USER FEEDBACK (apply these lessons to your current advice):"]
    for i, lesson in enumerate(recent, 1):
        lines.append(
            f"{i}. Query was: '{lesson['user_query']}' | "
            f"Feedback: '{lesson['user_feedback']}'"
        )
    return "\n".join(lines)