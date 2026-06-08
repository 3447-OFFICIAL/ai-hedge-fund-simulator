import json
from agents.base import BaseAgent
from workflows.state import AgentState

class PortfolioAgent(BaseAgent):
    def run(self, state: AgentState) -> AgentState:
        system_prompt = """You are the Master Portfolio Manager Agent.
Aggregate outputs from Macro, Technical, News, Quant, and Risk agents.
Resolve conflicts and optimize portfolio allocation.
Provide final decisions (Buy/Sell/Hold), position sizes, and a detailed reasoning chain for explainable AI.
Return ONLY valid JSON."""
        
        inputs = {
            "macro": state.get("macro_outlook", {}),
            "technical": state.get("technical_analysis", {}),
            "news": state.get("news_sentiment", {}),
            "quant": state.get("quant_factors", {}),
            "risk": state.get("risk_limits", {})
        }
        
        user_prompt = f"Inputs: {json.dumps(inputs)}. Determine final allocations."
        
        try:
            response = self.invoke_llm(system_prompt, user_prompt)
            response = response.replace('```json', '').replace('```', '').strip()
            data = json.loads(response)
        except Exception:
            data = {"allocations": {t: 0.0 for t in state.get('tickers', [])}, "reasoning": "Fallback to cash due to error."}
            
        return {"portfolio_decision": data}
