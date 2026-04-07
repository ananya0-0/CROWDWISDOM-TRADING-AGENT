"""
main.py
Entry point for the CrowdWisdom Trading Agent.
Starts the FastAPI server using uvicorn.

Usage:
    python main.py                      # Start API server (default)
    python main.py --cli                # Run interactive CLI instead

API will be available at: http://localhost:8000
Interactive docs at:      http://localhost:8000/docs
"""

import sys
import argparse
from dotenv import load_dotenv

# Load environment variables from .env BEFORE any agent imports
load_dotenv()

from core.logger import get_logger

logger = get_logger(__name__)


def run_api():
    """Start the FastAPI server with uvicorn."""
    import uvicorn
    logger.info("🚀 Starting CrowdWisdom Trading Agent API...")
    logger.info("📖 Interactive docs: http://localhost:8000/docs")
    uvicorn.run(
        "api.routes:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


def run_cli():
    """Interactive CLI mode — legacy interface kept for quick testing."""
    from agents.chat_agent import get_advice, record_feedback

    print("=" * 50)
    print("  CrowdWisdom Trading Advisor — CLI Mode")
    print("  (For full API, run without --cli flag)")
    print("=" * 50)
    print("Type 'exit' to quit.\n")

    last_query = ""
    last_advice = ""

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        last_query = user_input
        advice, traders = get_advice(user_input)
        last_advice = advice

        print(f"\n{'─'*50}")
        print(f"Advisor:\n{advice}")
        print(f"{'─'*50}")
        print(f"(Analyzed {len(traders)} traders from Polymarket + Kalshi)")

        # Closed Learning Loop feedback
        feedback = input(
            "\nFeedback (press Enter to skip, or tell me what to improve): "
        ).strip()
        if feedback:
            record_feedback(last_query, last_advice, feedback)
            print("[✅ Feedback saved — I'll apply this next time.]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CrowdWisdom Trading Agent")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in interactive CLI mode instead of starting the API server.",
    )
    args = parser.parse_args()

    if args.cli:
        run_cli()
    else:
        run_api()