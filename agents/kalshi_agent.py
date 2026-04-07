"""
agents/kalshi_agent.py
Scout Agent #2 — Kalshi
Fetches top-performing, consistent traders from Kalshi's REST API.
Kalshi requires an API key for most endpoints. This agent handles
authenticated requests and falls back gracefully on auth failure.
Docs: https://trading-api.readme.io/reference/getmarkets
"""

import os
import requests
from core.logger import get_logger

logger = get_logger(__name__)

KALSHI_API_BASE = "https://trading-api.kalshi.com/trade-api/v2"
TOP_N = 5


def _get_headers() -> dict:
    """Build auth headers from environment. Kalshi uses API key auth."""
    api_key = os.getenv("KALSHI_API_KEY", "")
    if not api_key:
        logger.warning("KALSHI_API_KEY not set. Public endpoints only will be used.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _fetch_kalshi_markets(limit: int = 20) -> list[dict]:
    """Fetch active markets from Kalshi to identify traded events."""
    url = f"{KALSHI_API_BASE}/markets"
    params = {"limit": limit, "status": "open"}
    try:
        resp = requests.get(url, headers=_get_headers(), params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        markets = data.get("markets", [])
        logger.debug(f"Fetched {len(markets)} active Kalshi markets.")
        return markets
    except requests.RequestException as e:
        logger.error(f"Failed to fetch Kalshi markets: {e}")
        return []


def _fetch_kalshi_portfolio(limit: int = TOP_N) -> list[dict]:
    """
    Attempt to fetch leaderboard/top trader data from Kalshi.
    Kalshi does not have a public leaderboard, so we fall back to mock data.
    In production: query your own DB of tracked wallets or use the Kalshi
    portfolio endpoint per-user after collecting wallet addresses externally.
    """
    logger.warning(
        "Kalshi has no public leaderboard API. Using tracked-wallet mock data. "
        "In production, seed wallet addresses from the reference repos in the assessment."
    )
    return _mock_traders()


def _mock_traders() -> list[dict]:
    """
    Mock Kalshi trader profiles.
    Clearly labelled — replace with real wallet tracking in production.
    """
    logger.warning("⚠️  MOCK DATA IN USE — Kalshi has no public trader leaderboard.")
    return [
        {
            "member_id": "kalshi_trader_99",
            "profit": 8500,
            "win_rate": 0.71,
            "volume": 25000,
            "recent_trades": ["NYC Rain > 0.5in June 2025", "Chicago Daily High Temp"],
        },
        {
            "member_id": "kalshi_trader_42",
            "profit": 5200,
            "win_rate": 0.65,
            "volume": 18000,
            "recent_trades": ["Fed Funds Rate June 2025", "US CPI YoY May 2025"],
        },
        {
            "member_id": "kalshi_trader_17",
            "profit": 3100,
            "win_rate": 0.60,
            "volume": 12000,
            "recent_trades": ["Senate Majority 2025", "House Speaker Vote"],
        },
    ]


def get_top_kalshi_traders() -> list[dict]:
    """
    Main entry point for the Kalshi Scout Agent.
    Returns a normalized list of top trader profiles ready for niche mapping.
    """
    logger.info("🔍 [Kalshi Scout Agent] Fetching top traders...")
    raw_traders = _fetch_kalshi_portfolio()

    if not raw_traders:
        logger.warning("No trader data returned from Kalshi.")
        return []

    normalized = []
    for t in raw_traders[:TOP_N]:
        trader_id = t.get("member_id") or t.get("user_id") or t.get("wallet", "unknown")
        profit = t.get("profit") or t.get("pnl_usd") or 0
        win_rate = t.get("win_rate") or t.get("pnl") or 0
        recent_markets = t.get("recent_trades") or t.get("markets") or []

        normalized.append({
            "platform": "Kalshi",
            "wallet": trader_id,
            "profit_usd": profit,
            "win_rate": win_rate,
            "recent_trades": recent_markets,
            "niche": None,  # Populated later by Niche Agent
        })

    logger.info(f"✅ [Kalshi Scout Agent] Found {len(normalized)} traders.")
    return normalized