import yfinance as yf
import pandas as pd
from typing import List, Optional


class MarketDataProvider:
    def __init__(self):
        pass

    def get_historical_data(
        self, tickers: List[str], start_date: str, end_date: str, interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical market data using yfinance.
        """
        # Download data for all tickers
        data = yf.download(tickers, start=start_date, end=end_date, interval=interval)
        return data

    def get_current_price(self, ticker: str) -> Optional[float]:
        """
        Fetch the most recent closing price for a single ticker.
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            todays_data = ticker_obj.history(period="1d")
            if not todays_data.empty:
                return float(todays_data["Close"].iloc[0])
        except Exception as e:
            print(f"Error fetching current price for {ticker}: {e}")
        return None
