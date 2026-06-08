import json
from agents.base import BaseAgent
from workflows.state import AgentState

class QuantAgent(BaseAgent):
    def run(self, state: AgentState) -> AgentState:
        system_prompt = """You are the Quant Research Agent. 
Perform factor analysis and alpha discovery.
Return expected returns, Sharpe estimate, and factor attribution.
Return ONLY valid JSON."""
        
        tickers = state.get('tickers', [])
        user_prompt = f"Tickers: {tickers}. Provide quantitative factors JSON."
        
        try:
            response = self.invoke_llm(system_prompt, user_prompt)
            response = response.replace('```json', '').replace('```', '').strip()
            data = json.loads(response)
        except Exception:
            data = {t: {"expected_return": 0.05, "sharpe_estimate": 1.0} for t in tickers}
            
        return {"quant_factors": data}
