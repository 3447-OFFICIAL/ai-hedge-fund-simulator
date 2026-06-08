from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from workflows.graph import create_hedge_fund_graph
from datetime import datetime

app = FastAPI(
    title="AI Hedge Fund Simulator API",
    description="API for the Multi-Agent Hedge Fund Simulator",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RunSimulationRequest(BaseModel):
    tickers: List[str]
    portfolio_value: float

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Hedge Fund Simulator API"}

@app.post("/simulate")
def run_simulation(request: RunSimulationRequest):
    graph = create_hedge_fund_graph()
    
    initial_state = {
        "messages": [],
        "tickers": request.tickers,
        "portfolio_value": request.portfolio_value,
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "macro_outlook": {},
        "technical_analysis": {},
        "news_sentiment": {},
        "quant_factors": {},
        "risk_limits": {},
        "portfolio_decision": {}
    }
    
    # Run the graph
    result_state = graph.invoke(initial_state)
    
    return {
        "status": "success",
        "date": result_state["current_date"],
        "portfolio_decision": result_state["portfolio_decision"],
        "agent_outputs": {
            "macro": result_state["macro_outlook"],
            "technical": result_state["technical_analysis"],
            "news": result_state["news_sentiment"],
            "quant": result_state["quant_factors"],
            "risk": result_state["risk_limits"]
        }
    }
