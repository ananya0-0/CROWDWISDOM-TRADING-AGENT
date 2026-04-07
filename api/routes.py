"""
api/routes.py
FastAPI application — REST API backend for CrowdWisdom Trading Agent.

Endpoints:
  POST /advice          — Run the full agent pipeline and get a recommendation
  POST /feedback        — Submit feedback to the closed learning loop
  GET  /traders         — Get raw trader data from both platforms
  GET  /memory          — View the current learning loop memory
  DELETE /memory        — Reset the learning loop memory
  GET  /health          — Health check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agents.chat_agent import get_advice, record_feedback
from agents.polymarket_agent import get_top_polymarket_traders
from agents.kalshi_agent import get_top_kalshi_traders
from agents.niche_agent import map_all_niches
from core.memory import load_memory, save_memory
from core.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="CrowdWisdom Trading Agent API",
    description=(
        "Multi-agent AI system for prediction market analysis. "
        "Analyzes Polymarket and Kalshi traders and recommends copy-trading strategies."
    ),
    version="1.0.0",
)

# CORS — allow all origins for development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request / Response Models 
class AdviceRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=5,
        example="Who should I copy for the NBA Finals prediction?",
        description="The prediction market question or event to research.",
    )


class AdviceResponse(BaseModel):
    query: str
    advice: str
    traders_analyzed: int


class FeedbackRequest(BaseModel):
    query: str = Field(..., description="The original query the advice was given for.")
    advice: str = Field(..., description="The advice that was given (used for context).")
    feedback: str = Field(
        ...,
        min_length=3,
        example="Prefer traders with higher win rates, not just profit.",
        description="User feedback on how to improve future recommendations.",
    )


class FeedbackResponse(BaseModel):
    status: str
    lessons_total: int


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health_check():
    """Simple health check to verify the API is running."""
    return {"status": "ok", "service": "CrowdWisdom Trading Agent"}


@app.post("/advice", response_model=AdviceResponse, tags=["Agent"])
def get_trading_advice(request: AdviceRequest):
    """
    **Main Agent Pipeline**

    Triggers the full multi-agent flow:
    1. Polymarket Scout Agent fetches top traders
    2. Kalshi Scout Agent fetches top traders
    3. Niche Agent classifies each trader
    4. RAG Agent enriches context via Apify
    5. Chat Agent synthesizes a recommendation

    Closed learning loop memory is automatically applied.
    """
    logger.info(f"POST /advice | query='{request.query}'")
    try:
        advice, all_traders = get_advice(request.query)
        return AdviceResponse(
            query=request.query,
            advice=advice,
            traders_analyzed=len(all_traders),
        )
    except Exception as e:
        logger.error(f"Error in /advice endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent pipeline failed: {str(e)}")


@app.post("/feedback", response_model=FeedbackResponse, tags=["Learning Loop"])
def submit_feedback(request: FeedbackRequest):
    """
    **Closed Learning Loop**

    Submit feedback on a recommendation. This is stored persistently and
    injected into future agent prompts to improve recommendations over time.
    """
    logger.info(f"POST /feedback | feedback='{request.feedback[:80]}'")
    try:
        record_feedback(request.query, request.advice, request.feedback)
        memory = load_memory()
        return FeedbackResponse(
            status="Feedback recorded. Agent will apply this lesson in future sessions.",
            lessons_total=len(memory.get("lessons", [])),
        )
    except Exception as e:
        logger.error(f"Error in /feedback endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")


@app.get("/traders", tags=["Data"])
def get_traders(include_niches: bool = False):
    """
    **Raw Trader Data**

    Returns the current top traders from both Polymarket and Kalshi.
    Set `include_niches=true` to run LLM niche classification on each trader.
    Note: niche classification makes one LLM call per trader — use sparingly.
    """
    logger.info(f"GET /traders | include_niches={include_niches}")
    try:
        poly = get_top_polymarket_traders()
        kalshi = get_top_kalshi_traders()
        all_traders = poly + kalshi

        if include_niches:
            all_traders = map_all_niches(all_traders)

        return {
            "polymarket_count": len(poly),
            "kalshi_count": len(kalshi),
            "traders": all_traders,
        }
    except Exception as e:
        logger.error(f"Error in /traders endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch traders: {str(e)}")


@app.get("/memory", tags=["Learning Loop"])
def get_memory():
    """
    **View Learning Loop Memory**

    Returns all lessons stored in the closed learning loop memory.
    """
    logger.info("GET /memory")
    memory = load_memory()
    return {
        "lessons_total": len(memory.get("lessons", [])),
        "lessons": memory.get("lessons", []),
    }


@app.delete("/memory", tags=["Learning Loop"])
def reset_memory():
    """
    **Reset Learning Loop Memory**

    Clears all stored lessons. The agent will start fresh with no prior feedback.
    """
    logger.info("DELETE /memory — resetting learning loop")
    save_memory({"lessons": []})
    return {"status": "Memory cleared. Agent reset to default behavior."}