from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from workflows.state import AgentState
import os


class BaseAgent:
    def __init__(self, model_name: str = "gpt-4o"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is missing. Halting execution for security."
            )

        # Enforce native JSON output for robust parsing
        self.llm = ChatOpenAI(model=model_name, api_key=api_key, temperature=0.0).bind(
            response_format={"type": "json_object"}
        )

    def invoke_llm(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = self.llm.invoke(messages)
        return response.content
