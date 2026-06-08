from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.discrete_allocation import DiscreteAllocation
import pandas as pd
from typing import Dict, Tuple

class PortfolioOptimizer:
    def __init__(self):
        pass

    def optimize_sharpe_ratio(self, historical_prices: pd.DataFrame) -> Tuple[Dict[str, float], Tuple[float, float, float]]:
        """
        Optimizes the portfolio to maximize the Sharpe ratio using PyPortfolioOpt.
        historical_prices: DataFrame where index is date and columns are tickers.
        Returns: 
            cleaned_weights: Dict of ticker -> weight
            performance: Tuple of (expected_return, annual_volatility, sharpe_ratio)
        """
        # Calculate expected returns and sample covariance
        mu = mean_historical_return(historical_prices)
        S = CovarianceShrinkage(historical_prices).ledoit_wolf()

        # Optimize for maximal Sharpe ratio
        ef = EfficientFrontier(mu, S)
        raw_weights = ef.max_sharpe()
        cleaned_weights = ef.clean_weights()

        performance = ef.portfolio_performance(verbose=False)
        
        return cleaned_weights, performance

    def get_discrete_allocation(self, weights: Dict[str, float], latest_prices: pd.Series, portfolio_value: float) -> Tuple[Dict[str, int], float]:
        """
        Calculates the discrete number of shares to buy for each ticker given the weights and total portfolio value.
        """
        da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=portfolio_value)
        allocation, leftover = da.lp_portfolio()
        return allocation, leftover
