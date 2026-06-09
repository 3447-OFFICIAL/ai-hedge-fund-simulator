from langgraph.graph import StateGraph, END
from workflows.state import AgentState
from agents.macro.agent import MacroAgent
from agents.technical.agent import TechnicalAgent
from agents.news.agent import NewsAgent
from agents.quant.agent import QuantAgent
from agents.risk.agent import RiskAgent
from agents.portfolio.agent import PortfolioAgent


def start_node(state: AgentState):
    """Dummy node to fan out to parallel agents."""
    return {}


def create_hedge_fund_graph():
    graph = StateGraph(AgentState)

    macro_agent = MacroAgent()
    technical_agent = TechnicalAgent()
    news_agent = NewsAgent()
    quant_agent = QuantAgent()
    risk_agent = RiskAgent()
    portfolio_agent = PortfolioAgent()

    # Add nodes
    graph.add_node("start", start_node)
    graph.add_node("macro", macro_agent.run)
    graph.add_node("technical", technical_agent.run)
    graph.add_node("news", news_agent.run)
    graph.add_node("quant", quant_agent.run)
    graph.add_node("risk", risk_agent.run)
    graph.add_node("portfolio", portfolio_agent.run)

    graph.set_entry_point("start")

    # Fan out to parallel analyst agents
    graph.add_edge("start", "macro")
    graph.add_edge("start", "technical")
    graph.add_edge("start", "news")
    graph.add_edge("start", "quant")

    # Fan in to risk manager
    graph.add_edge("macro", "risk")
    graph.add_edge("technical", "risk")
    graph.add_edge("news", "risk")
    graph.add_edge("quant", "risk")

    graph.add_edge("risk", "portfolio")
    graph.add_edge("portfolio", END)

    return graph.compile()
