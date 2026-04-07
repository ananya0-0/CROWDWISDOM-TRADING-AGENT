import sys
import argparse
from dotenv import load_dotenv

# 1. Load env vars first
load_dotenv()

from core.logger import get_logger

logger = get_logger(__name__)

def run_api():
    """Start the FastAPI server with uvicorn."""
    import uvicorn
    logger.info("🚀 Starting CrowdWisdom Trading Agent API...")
    logger.info("📖 Interactive docs: http://localhost:8000/docs")
    # Use the string "api.routes:app" so uvicorn can find it after the spawn
    uvicorn.run(
        "api.routes:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

def run_cli():
    """Interactive CLI mode."""
    # Move this import inside the function to avoid circular import issues
    try:
        from agents.chat_agent import get_advice, record_feedback
    except ImportError as e:
        logger.error(f"❌ Failed to import chat_agent functions: {e}")
        print("\nERROR: Please ensure agents/chat_agent.py has 'get_advice' and 'record_feedback' functions.")
        return

    print("=" * 50)
    print("  CrowdWisdom Trading Advisor — CLI Mode")
    print("=" * 50)

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input or user_input.lower() == "exit":
            break

        # Assuming get_advice returns (str, list)
        advice, traders = get_advice(user_input)
        
        print(f"\n{'─'*50}\nAdvisor:\n{advice}\n{'─'*50}")
        print(f"(Analyzed {len(traders)} traders)")

        feedback = input("\nFeedback (Enter to skip): ").strip()
        if feedback:
            record_feedback(user_input, advice, feedback)

if __name__ == "__main__":
    # This block is MANDATORY on Windows for uvicorn reload to work
    parser = argparse.ArgumentParser(description="CrowdWisdom Trading Agent")
    parser.add_argument("--cli", action="store_true")
    args = parser.parse_args()

    if args.cli:
        run_cli()
    else:
        run_api()