import json
from agents.base import BaseAgent
from workflows.state import AgentState


class MacroAgent(BaseAgent):
    def run(self, state: AgentState) -> AgentState:
        system_prompt = """You are the Macro Analyst Agent. 
Analyze current economic indicators (interest rates, inflation, GDP).
Provide a bullish/bearish/neutral outlook, a confidence score (0-100), and economic regime.
Return ONLY a valid JSON object matching the requested schema.
"""
        user_prompt = f"Date: {state.get('current_date')}. Evaluate macro environment."

        try:
            response = self.invoke_llm(system_prompt, user_prompt)
            # Simple json extraction
            response = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(response)
        except Exception:
            data = {"outlook": "neutral", "confidence": 50, "regime": "unknown"}

        return {"macro_outlook": data}
