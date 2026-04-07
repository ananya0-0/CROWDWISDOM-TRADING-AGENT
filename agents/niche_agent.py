"""
agents/niche_agent.py
Niche Mapping Agent
Uses the LLM to classify each trader's portfolio into a market niche
based on their recent trade history (e.g., Sports, Politics, Weather, Crypto).
"""

from core.llm_client import call_llm
from core.logger import get_logger

logger = get_logger(__name__)

KNOWN_NICHES = [
    "NBA", "NFL", "Soccer", "Sports",
    "US Politics", "Global Politics",
    "Weather", "Climate",
    "Crypto", "Stocks", "Economics",
    "Entertainment", "Technology",
    "Other",
]

NICHE_SYSTEM_PROMPT = f"""You are a financial market classifier agent.
Your job is to analyze a prediction market trader's recent trade history
and assign them ONE niche category from this list: {', '.join(KNOWN_NICHES)}.

Rules:
- Respond with ONLY the niche name. No explanation, no punctuation.
- If the trades clearly span two areas (e.g., NBA + NFL), use "Sports".
- If you cannot determine the niche, respond with "Other".
"""


def map_trader_niche(trader: dict) -> str:
    """
    Classify a single trader's niche based on their recent trades.
    Returns the niche string (e.g., "NBA", "US Politics").
    """
    recent = trader.get("recent_trades", [])
    if not recent:
        logger.debug(f"Trader {trader['wallet']} has no trade history. Defaulting to 'Other'.")
        return "Other"

    trade_list = "\n".join(f"- {trade}" for trade in recent)
    user_prompt = f"Recent trades:\n{trade_list}\n\nWhat is this trader's niche?"

    niche = call_llm(
        system_prompt=NICHE_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=20,  # We only need one word
    ).strip()

    # Validate the response is a known niche
    if niche not in KNOWN_NICHES:
        logger.warning(f"LLM returned unknown niche '{niche}' for {trader['wallet']}. Defaulting to 'Other'.")
        niche = "Other"

    logger.debug(f"Trader {trader['wallet']} classified as: {niche}")
    return niche


def map_all_niches(traders: list[dict]) -> list[dict]:
    """
    Run niche classification for all traders.
    Mutates each trader dict in-place and returns the updated list.
    """
    logger.info(f"🗂️  [Niche Agent] Classifying {len(traders)} traders into niches...")
    for trader in traders:
        trader["niche"] = map_trader_niche(trader)
    logger.info("✅ [Niche Agent] Niche classification complete.")
    return traders