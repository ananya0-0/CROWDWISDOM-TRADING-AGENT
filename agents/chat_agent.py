"""
agents/chat_agent.py
Chat Advisor Agent — Central Orchestrator
Synthesizes trader data, niche classifications, RAG context, and
the closed learning loop to deliver a personalized copy-trading recommendation.
"""

import json

from agents.polymarket_agent import get_top_polymarket_traders
from agents.kalshi_agent import get_top_kalshi_traders
from agents.niche_agent import map_all_niches
from agents.rag_agent import apify_research
from core.llm_client import call_llm
from core.memory import load_memory, add_lesson, build_memory_context
from core.logger import get_logger

logger = get_logger(__name__)

ADVISOR_SYSTEM_PROMPT = """You are an expert prediction market copy-trading advisor at CrowdWisdom.

Your role:
1. Analyze the live context scraped from the web about the user's event.
2. Review the mapped trader profiles (from Polymarket and Kalshi) and their niches.
3. Recommend the BEST trader(s) to copy for the user's specific query.
4. Explain your reasoning — win rate, recent relevant trades, and niche alignment.
5. Always note platform differences: Polymarket uses crypto wallets; Kalshi uses member IDs.

Format your response clearly:
- Start with your top recommendation and why.
- List 1-2 alternative traders if relevant.
- End with a brief risk note.
"""


def get_advice(user_query: str) -> tuple[str, list[dict]]:
    """
    Full agent pipeline:
    1. Scout Agents fetch traders from both platforms.
    2. Niche Agent classifies each trader.
    3. RAG Agent fetches live web context.
    4. Chat Agent synthesizes everything into a recommendation.

    Returns: (advice_text, all_traders)
    """
    logger.info(f"🚀 Starting full agent pipeline for query: '{user_query}'")

    # Step 1: Scout Agents
    polymarket_traders = get_top_polymarket_traders()
    kalshi_traders = get_top_kalshi_traders()
    all_traders = polymarket_traders + kalshi_traders

    if not all_traders:
        logger.error("No traders found from any platform.")
        return "Could not retrieve trader data at this time. Please try again.", []

    # Step 2: Niche Agent
    all_traders = map_all_niches(all_traders)

    # Step 3: RAG Agent
    rag_context = apify_research(user_query)

    # Step 4: Load learning loop memory and inject into prompt
    memory = load_memory()
    memory_context = build_memory_context(memory)

    system_prompt = ADVISOR_SYSTEM_PROMPT
    if memory_context:
        system_prompt += f"\n\n{memory_context}"

    user_prompt = f"""User Query: {user_query}

=== Trader Profiles (Polymarket + Kalshi) ===
{json.dumps(all_traders, indent=2)}

{rag_context}

Based on the above, who should the user copy-trade for their query?"""

    logger.info("🤖 [Chat Agent] Generating final recommendation...")
    advice = call_llm(system_prompt=system_prompt, user_prompt=user_prompt, max_tokens=1024)
    logger.info("✅ [Chat Agent] Recommendation generated.")

    return advice, all_traders


def record_feedback(user_query: str, advice: str, feedback: str) -> None:
    """Save user feedback to the closed learning loop memory."""
    memory = load_memory()
    add_lesson(memory, user_query, advice, feedback)
    logger.info(f"📚 [Learning Loop] Feedback recorded for future sessions.")