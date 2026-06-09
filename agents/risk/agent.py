import json
from agents.base import BaseAgent
from workflows.state import AgentState


class RiskAgent(BaseAgent):
    def run(self, state: AgentState) -> AgentState:
        system_prompt = """You are the Risk Manager Agent. 
Determine position sizing limits, calculate VaR, and provide hedging recommendations.
Consider Macro, Technical, and News inputs.
Return risk rating, max allocation per ticker (0.0 to 1.0), and hedging advice.
Return ONLY valid JSON."""

        inputs = {
            "macro": state.get("macro_outlook", {}),
            "technical": state.get("technical_analysis", {}),
            "news": state.get("news_sentiment", {}),
        }

        user_prompt = f"Inputs: {json.dumps(inputs)}. Provide risk limits JSON."

        try:
            response = self.invoke_llm(system_prompt, user_prompt)
            response = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(response)
        except Exception:
            data = {
                "max_allocation": {t: 0.2 for t in state.get("tickers", [])},
                "risk_rating": "moderate",
            }

        return {"risk_limits": data}
