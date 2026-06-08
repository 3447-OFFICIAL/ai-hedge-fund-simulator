import json
from agents.base import BaseAgent
from workflows.state import AgentState
from data.news_scraper import NewsScraper

class NewsAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.scraper = NewsScraper()

    def run(self, state: AgentState) -> AgentState:
        system_prompt = """You are the News Analyst Agent. 
Evaluate recent news headlines and determine market sentiment.
Return a sentiment score (-1.0 to 1.0), key catalysts, and risk alerts for each ticker.
Return ONLY valid JSON."""
        
        tickers = state.get('tickers', [])
        news_context = {}
        for t in tickers:
            headlines = self.scraper.scrape_yahoo_finance_news(t)
            news_context[t] = [h['title'] for h in headlines[:3]] # get top 3
            
        user_prompt = f"Tickers and News: {json.dumps(news_context)}. Provide news sentiment JSON."
        try:
            response = self.invoke_llm(system_prompt, user_prompt)
            response = response.replace('```json', '').replace('```', '').strip()
            data = json.loads(response)
        except Exception:
            data = {t: {"sentiment": 0.0, "catalysts": []} for t in tickers}
            
        return {"news_sentiment": data}
