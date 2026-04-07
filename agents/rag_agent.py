"""
agents/rag_agent.py
RAG (Retrieval-Augmented Generation) Agent
Uses Apify's Google Search Scraper to pull live web context about
the prediction market event the user is asking about.
This enriches the Chat Agent's prompt with real-world information.
"""

import os
from apify_client import ApifyClient
from core.logger import get_logger

logger = get_logger(__name__)

MAX_RESULTS = 5
APIFY_ACTOR = "apify/google-search-scraper"


def apify_research(query: str) -> str:
    """
    Scrape the top search results for a given query using Apify.
    Returns a formatted string of titles + snippets for LLM context injection.
    """
    token = os.getenv("APIFY_TOKEN", "")
    if not token:
        logger.error("APIFY_TOKEN not set. RAG enrichment will be skipped.")
        return "[RAG Error] APIFY_TOKEN is missing. Add it to your .env file."

    logger.info(f"📰 [RAG Agent] Researching: '{query}' via Apify...")

    try:
        client = ApifyClient(token)
        run_input = {
            "queries": [query],
            "resultsPerPage": MAX_RESULTS,
            "maxDepth": 0,  # Only search results, no page crawling
            "outputFormats": ["captions"],
        }

        run = client.actor(APIFY_ACTOR).call(run_input=run_input)
        dataset_id = run.get("defaultDatasetId")
        if not dataset_id:
            logger.warning("Apify run returned no dataset ID.")
            return "[RAG Warning] Apify returned no results."

        results = []
        for item in client.dataset(dataset_id).iterate_items():
            title = item.get("title", "No title")
            snippet = item.get("description", item.get("snippet", "No snippet"))
            url = item.get("url", "")
            results.append(f"• {title}\n  {snippet}\n  Source: {url}")

        if not results:
            logger.warning(f"No Apify search results for query: '{query}'")
            return f"[RAG Warning] No web results found for '{query}'."

        context = f"=== Live Web Context for: '{query}' ===\n" + "\n\n".join(results)
        logger.info(f"✅ [RAG Agent] Retrieved {len(results)} results for enrichment.")
        return context

    except Exception as e:
        logger.error(f"Apify RAG agent failed: {e}", exc_info=True)
        return f"[RAG Error] Could not fetch web context: {str(e)}"
    