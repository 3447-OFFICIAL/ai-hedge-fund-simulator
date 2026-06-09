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
        
        # Realistic friction models
        self.cerebro.broker.setcommission(commission=0.001)
        self.cerebro.broker.set_slippage_perc(0.0005) # 5 bps slippage

        # Attach Analyzers
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    def run_backtest(self, historical_data: pd.DataFrame, weights: Dict[str, float]) -> Dict[str, Any]:
        """
        Run a backtrader backtest dynamically based on strategy weights.
        """
        self.cerebro.addstrategy(HedgeFundStrategy, target_weights=weights)
        
        # Inject data feeds
        if isinstance(historical_data.columns, pd.MultiIndex):
            for ticker in weights.keys():
                if 'Close' in historical_data.columns.levels[0] and ticker in historical_data.columns.levels[1]:
                    ticker_df = historical_data.xs(ticker, level=1, axis=1)
                    data_feed = bt.feeds.PandasData(dataname=ticker_df, name=ticker)
                    self.cerebro.adddata(data_feed)
        else:
            ticker = list(weights.keys())[0] if weights else "Asset"
            data_feed = bt.feeds.PandasData(dataname=historical_data, name=ticker)
            self.cerebro.adddata(data_feed)
            
        initial_value = self.cerebro.broker.getvalue()
        
        # Execute the simulation
        results = self.cerebro.run()
        strat = results[0]
        
        final_value = self.cerebro.broker.getvalue()
        
        sharpe = strat.analyzers.sharpe.get_analysis().get('sharperatio', 0.0)
        drawdown = strat.analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 0.0)
        cagr = strat.analyzers.returns.get_analysis().get('rnorm100', 0.0)
        
        return {
            "initial_value": initial_value,
            "final_value": final_value,
            "return_pct": (final_value / initial_value) - 1.0,
            "sharpe_ratio": sharpe,
            "max_drawdown": drawdown,
            "cagr": cagr
        }
