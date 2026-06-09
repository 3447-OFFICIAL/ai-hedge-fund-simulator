from typing import TypedDict, Annotated, Sequence, Dict, Any, List
from langchain_core.messages import BaseMessage
import operator

def update_dict(d1: Dict, d2: Dict) -> Dict:
    if not d1: return d2
    if not d2: return d1
    d = d1.copy()
    d.update(d2)
    return d

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    tickers: List[str]
    portfolio_value: float
    current_date: str
    
    # Agent specific outputs using robust reducers for parallel fan-in
    macro_outlook: Annotated[Dict[str, Any], update_dict]
    technical_analysis: Annotated[Dict[str, Any], update_dict]
    news_sentiment: Annotated[Dict[str, Any], update_dict]
    quant_factors: Annotated[Dict[str, Any], update_dict]
    risk_limits: Annotated[Dict[str, Any], update_dict]
    
    # Final decision
    portfolio_decision: Annotated[Dict[str, Any], update_dict]
