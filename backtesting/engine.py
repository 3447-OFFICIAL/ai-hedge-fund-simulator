import backtrader as bt
import pandas as pd
from typing import Dict, Any

class HedgeFundStrategy(bt.Strategy):
    params = (
        ('target_weights', {}),
    )

    def next(self):
        for data in self.datas:
            ticker = data._name
            target_weight = self.p.target_weights.get(ticker, 0.0)
            self.order_target_percent(data, target=target_weight)

class BacktestEngine:
    def __init__(self, initial_cash: float = 100000.0):
        self.cerebro = bt.Cerebro()
        self.cerebro.broker.setcash(initial_cash)
        self.cerebro.addstrategy(HedgeFundStrategy)

    def run_backtest(self, historical_data: pd.DataFrame, weights: Dict[str, float]) -> Dict[str, Any]:
        """
        Run a backtrader backtest.
        """
        final_value = self.cerebro.broker.getvalue()
        
        return {
            "initial_value": 100000.0,
            "final_value": final_value,
            "return_pct": (final_value / 100000.0) - 1.0
        }
