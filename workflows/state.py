from typing import TypedDict, Annotated, Sequence, Dict, Any, List
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    tickers: List[str]
    portfolio_value: float
    current_date: str
    
    # Agent specific outputs
    macro_outlook: Dict[str, Any]
    technical_analysis: Dict[str, Any]
    news_sentiment: Dict[str, Any]
    quant_factors: Dict[str, Any]
    risk_limits: Dict[str, Any]
    
    # Final decision
    portfolio_decision: Dict[str, Any]
