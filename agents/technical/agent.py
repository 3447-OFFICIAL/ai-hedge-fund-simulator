import json
from agents.base import BaseAgent
from workflows.state import AgentState
from data.market_data import MarketDataProvider


class TechnicalAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.market_data = MarketDataProvider()

    def run(self, state: AgentState) -> AgentState:
        system_prompt = """You are the Technical Analyst Agent. 
Evaluate trends, moving averages, RSI, MACD.
Return a buy/sell/hold recommendation, entry/exit zones, and confidence score (0-100) for each ticker.
Return ONLY valid JSON."""

        tickers = state.get("tickers", [])
        date = state.get("current_date", "")

        user_prompt = (
            f"Date: {date}. Tickers: {tickers}. Provide technical analysis JSON."
        )
        try:
            response = self.invoke_llm(system_prompt, user_prompt)
            response = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(response)
        except Exception:
            data = {t: {"recommendation": "hold", "confidence": 50} for t in tickers}

        return {"technical_analysis": data}
