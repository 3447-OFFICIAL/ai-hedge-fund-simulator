import numpy as np
import pandas as pd
from pypfopt import (
    expected_returns,
    risk_models,
    black_litterman,
    EfficientFrontier,
    HRPOpt,
    objective_functions,
)
from typing import Dict, Any, List, Tuple


class InstitutionalPortfolioOptimizer:
    def __init__(self):
        self.risk_free_rate = 0.04

    def _calculate_sortino_ratio(
        self, returns: pd.Series, target_return: float = 0.0
    ) -> float:
        downside_returns = returns[returns < target_return]
        downside_deviation = np.sqrt(np.mean(downside_returns**2)) * np.sqrt(252)
        if downside_deviation == 0:
            return 0.0
        annualized_return = returns.mean() * 252
        return (annualized_return - self.risk_free_rate) / downside_deviation

    def _calculate_information_ratio(
        self, returns: pd.Series, benchmark_returns: pd.Series
    ) -> float:
        tracking_error = (returns - benchmark_returns).std() * np.sqrt(252)
        if tracking_error == 0:
            return 0.0
        active_return = (returns.mean() - benchmark_returns.mean()) * 252
        return active_return / tracking_error

    def optimize_black_litterman(
        self,
        prices: pd.DataFrame,
        llm_views: Dict[str, float],
        confidences: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Implements the Black-Litterman model.
        Blends market equilibrium priors (CAPM) with subjective LLM views,
        weighted by the Bayesian confidence score of the agents.
        """
        # Calculate market priors
        S = risk_models.sample_cov(prices)
        market_prices = prices.mean(axis=1)  # Proxy for marketcap weight if unavailable
        delta = black_litterman.market_implied_risk_aversion(market_prices)
        market_prior = black_litterman.market_implied_prior_returns(
            market_prices.mean(), S, delta
        )

        # Format views
        viewdict = llm_views

        # Format confidences (omega matrix proxy)
        confidences_list = [confidences.get(t, 0.5) for t in prices.columns]

        # Black Litterman model
        bl = black_litterman.BlackLittermanModel(
            S,
            pi=market_prior,
            absolute_views=viewdict,
            omega="idzorek",
            view_confidences=confidences_list,
        )
        bl_returns = bl.bl_returns()
        bl_cov = bl.bl_cov()

        # Optimize using Efficient Frontier based on BL returns and Cov
        ef = EfficientFrontier(bl_returns, bl_cov)
        ef.add_objective(objective_functions.L2_reg, gamma=0.1)  # Reduce concentration
        raw_weights = ef.max_sharpe(risk_free_rate=self.risk_free_rate)

        cleaned_weights = ef.clean_weights()
        return dict(cleaned_weights)

    def optimize_risk_parity(self, prices: pd.DataFrame) -> Dict[str, float]:
        """
        Implements Hierarchical Risk Parity (HRP) for absolute downside protection.
        """
        returns = expected_returns.returns_from_prices(prices)
        hrp = HRPOpt(returns)
        raw_weights = hrp.optimize()
        return dict(raw_weights)
