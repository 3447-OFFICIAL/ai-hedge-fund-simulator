import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import datetime


class NewsScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def scrape_yahoo_finance_news(self, ticker: str) -> List[Dict[str, str]]:
        """
        Scrape recent news headlines for a ticker from Yahoo Finance via RSS.
        """
        return self.fetch_rss_news(ticker)

    def fetch_rss_news(self, ticker: str) -> List[Dict[str, str]]:
        """
        Fetch news from Yahoo Finance RSS feed.
        """
        rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
        try:
            response = requests.get(rss_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return []

            # Use 'xml' parser for RSS
            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")

            news_list = []
            for item in items:
                title = item.title.text if item.title else ""
                link = item.link.text if item.link else ""
                pubDate = item.pubDate.text if item.pubDate else ""
                description = item.description.text if item.description else ""

                news_list.append(
                    {
                        "title": title,
                        "link": link,
                        "published_at": pubDate,
                        "description": description,
                        "source": "Yahoo Finance RSS",
                    }
                )

            return news_list
        except Exception as e:
            print(f"Error fetching RSS news for {ticker}: {e}")
            return []
