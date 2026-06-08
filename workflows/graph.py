from langgraph.graph import StateGraph, END
from workflows.state import AgentState
from agents.macro.agent import MacroAgent
from agents.technical.agent import TechnicalAgent
from agents.news.agent import NewsAgent
from agents.quant.agent import QuantAgent
from agents.risk.agent import RiskAgent
from agents.portfolio.agent import PortfolioAgent

def create_hedge_fund_graph():
    graph = StateGraph(AgentState)
    
    macro_agent = MacroAgent()
    technical_agent = TechnicalAgent()
    news_agent = NewsAgent()
    quant_agent = QuantAgent()
    risk_agent = RiskAgent()
    portfolio_agent = PortfolioAgent()
    
    # Add nodes
    graph.add_node("macro", macro_agent.run)
    graph.add_node("technical", technical_agent.run)
    graph.add_node("news", news_agent.run)
    graph.add_node("quant", quant_agent.run)
    graph.add_node("risk", risk_agent.run)
    graph.add_node("portfolio", portfolio_agent.run)
    
    graph.set_entry_point("macro")
    graph.add_edge("macro", "technical")
    graph.add_edge("technical", "news")
    graph.add_edge("news", "quant")
    graph.add_edge("quant", "risk")
    graph.add_edge("risk", "portfolio")
    graph.add_edge("portfolio", END)
    
    return graph.compile()
