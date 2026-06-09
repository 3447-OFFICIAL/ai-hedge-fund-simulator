from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from workflows.graph import create_hedge_fund_graph
from datetime import datetime
import os

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="AI Hedge Fund Simulator API",
    description="API for the Multi-Agent Hedge Fund Simulator",
    version="1.0.0"
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Instrument for Observability
FastAPIInstrumentor.instrument_app(app)

# Secure CORS config
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key_header: str = Depends(api_key_header)):
    expected_key = os.getenv("HEDGE_FUND_API_KEY", "default-dev-key")
    if not api_key_header or api_key_header != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return api_key_header

class RunSimulationRequest(BaseModel):
    tickers: List[str] = Field(..., max_length=20, description="List of stock tickers (max 20)")
    portfolio_value: float = Field(..., gt=0, description="Initial portfolio value")

@app.get("/")
@limiter.limit("60/minute")
def read_root(request: Request):
    return {"message": "Welcome to the AI Hedge Fund Simulator API"}

@app.post("/simulate")
@limiter.limit("5/minute")
async def run_simulation(request: Request, sim_request: RunSimulationRequest, api_key: str = Depends(get_api_key)):
    graph = create_hedge_fund_graph()
    
    initial_state = {
        "messages": [],
        "tickers": sim_request.tickers,
        "portfolio_value": sim_request.portfolio_value,
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "macro_outlook": {},
        "technical_analysis": {},
        "news_sentiment": {},
        "quant_factors": {},
        "risk_limits": {},
        "portfolio_decision": {}
    }
    
    # Run the graph asynchronously for better performance
    result_state = await graph.ainvoke(initial_state)
    
    return {
        "status": "success",
        "date": result_state["current_date"],
        "portfolio_decision": result_state["portfolio_decision"],
        "agent_outputs": {
            "macro": result_state.get("macro_outlook", {}),
            "technical": result_state.get("technical_analysis", {}),
            "news": result_state.get("news_sentiment", {}),
            "quant": result_state.get("quant_factors", {}),
            "risk": result_state.get("risk_limits", {})
        }
    }
