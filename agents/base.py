from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from workflows.state import AgentState
import os

class BaseAgent:
    def __init__(self, model_name: str = "gpt-4o"):
        api_key = os.getenv("OPENAI_API_KEY", "dummy-key-for-local-test")
        self.llm = ChatOpenAI(model=model_name, api_key=api_key, temperature=0.0)
        
    def invoke_llm(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = self.llm.invoke(messages)
        return response.content
