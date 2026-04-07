"""
agents/polymarket_agent.py
Scout Agent #1 — Polymarket
Fetches top-performing, consistent wallets from the Polymarket Gamma REST API.
Polymarket's public API requires no authentication for read operations.
Docs: https://docs.polymarket.com/
"""

import os
import requests
from core.logger import get_logger

logger = get_logger(__name__)

GAMMA_API_BASE = "https://gamma-api.polymarket.com"
CLOB_API_BASE = "https://clob.polymarket.com"

# How many top traders to surface
TOP_N = 5


def _fetch_active_markets(limit: int = 20) -> list[dict]:
    """Pull recently active markets to identify which events are live."""
    url = f"{GAMMA_API_BASE}/markets"
    params = {"limit": limit, "active": "true", "closed": "false"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        markets = resp.json()
        logger.debug(f"Fetched {len(markets)} active Polymarket markets.")
        return markets
    except requests.RequestException as e:
        logger.error(f"Failed to fetch Polymarket markets: {e}")
        return []


def _fetch_leaderboard() -> list[dict]:
    """
    Fetch top traders from Polymarket CLOB leaderboard endpoint.
    Falls back to mocked data with a clear warning if the API is unreachable.
    """
    url = f"{GAMMA_API_BASE}/leaderboard"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        logger.debug(f"Raw leaderboard response keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
        # API returns a list or dict with 'data' key depending on version
        if isinstance(data, list):
            return data
        return data.get("data", data.get("leaderboard", []))
    except requests.RequestException as e:
        logger.warning(f"Polymarket leaderboard unavailable ({e}). Using mock data for demonstration.")
        return _mock_traders()


def _mock_traders() -> list[dict]:
    """
    Fallback mock data — clearly labelled.
    Used when the live API is unreachable (e.g., rate limits or network issues).
    In production, replace this with a database cache of last-known-good data.
    """
    logger.warning("⚠️  MOCK DATA IN USE — Polymarket API was unreachable.")
    return [
        {
            "proxyWallet": "0x89a...21c",
            "profit": 45000,
            "pnl": 0.73,
            "volume": 120000,
            "tradesWon": 18,
            "tradesLost": 5,
            "recentMarkets": ["NBA Finals Winner 2025", "Super Bowl LIX Winner"],
        },
        {
            "proxyWallet": "0x12b...99e",
            "profit": 12000,
            "pnl": 0.61,
            "volume": 45000,
            "tradesWon": 9,
            "tradesLost": 4,
            "recentMarkets": ["US Presidential Election 2024", "Fed Rate Cut Dec 2024"],
        },
        {
            "proxyWallet": "0xf3c...77a",
            "profit": 8200,
            "pnl": 0.58,
            "volume": 30000,
            "tradesWon": 7,
            "tradesLost": 4,
            "recentMarkets": ["Champions League Winner 2025", "Ballon d'Or 2025"],
        },
    ]


def get_top_polymarket_traders() -> list[dict]:
    """
    Main entry point for the Polymarket Scout Agent.
    Returns a normalized list of top trader profiles ready for niche mapping.
    """
    logger.info("🔍 [Polymarket Scout Agent] Fetching top traders...")
    raw_traders = _fetch_leaderboard()

    if not raw_traders:
        logger.warning("No trader data returned from Polymarket.")
        return []

    # Normalize the response — field names vary by API version
    normalized = []
    for t in raw_traders[:TOP_N]:
        wallet = (
            t.get("proxyWallet")
            or t.get("address")
            or t.get("wallet")
            or "unknown"
        )
        profit = t.get("profit") or t.get("pnl_usd") or t.get("totalProfit") or 0
        win_rate = t.get("pnl") or t.get("winRate") or 0
        recent_markets = (
            t.get("recentMarkets")
            or t.get("markets")
            or t.get("recent_trades")
            or []
        )

        normalized.append({
            "platform": "Polymarket",
            "wallet": wallet,
            "profit_usd": profit,
            "win_rate": win_rate,
            "recent_trades": recent_markets,
            "niche": None,  # Populated later by Niche Agent
        })

    logger.info(f"✅ [Polymarket Scout Agent] Found {len(normalized)} traders.")
    return normalized