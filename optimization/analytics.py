import pandas as pd
import numpy as np
from typing import Dict

class InstitutionalAnalytics:
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate

    def calculate_sharpe_ratio(self, returns: pd.Series, periods_per_year: int = 252) -> float:
        """Calculate annualized Sharpe Ratio"""
        if returns.std() == 0:
            return 0.0
        excess_returns = returns - (self.risk_free_rate / periods_per_year)
        return float(np.sqrt(periods_per_year) * excess_returns.mean() / returns.std())

    def calculate_sortino_ratio(self, returns: pd.Series, periods_per_year: int = 252) -> float:
        """Calculate annualized Sortino Ratio"""
        excess_returns = returns - (self.risk_free_rate / periods_per_year)
        downside_returns = np.where(excess_returns < 0, excess_returns, 0)
        downside_std = np.std(downside_returns)
        if downside_std == 0:
            return 0.0
        return float(np.sqrt(periods_per_year) * excess_returns.mean() / downside_std)

    def calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate Maximum Drawdown"""
        rolling_max = prices.cummax()
        drawdown = prices / rolling_max - 1.0
        max_drawdown = drawdown.min()
        return float(max_drawdown)

    def calculate_var_historical(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate historical Value at Risk (VaR)"""
        return float(np.percentile(returns, 100 * (1 - confidence_level)))

    def get_all_metrics(self, prices: pd.Series) -> Dict[str, float]:
        """Calculate and return a dictionary of all performance metrics"""
        returns = prices.pct_change().dropna()
        return {
            "Total Return": float((prices.iloc[-1] / prices.iloc[0]) - 1.0),
            "Annualized Volatility": float(returns.std() * np.sqrt(252)),
            "Sharpe Ratio": self.calculate_sharpe_ratio(returns),
            "Sortino Ratio": self.calculate_sortino_ratio(returns),
            "Maximum Drawdown": self.calculate_max_drawdown(prices),
            "VaR (95%)": self.calculate_var_historical(returns)
        }
