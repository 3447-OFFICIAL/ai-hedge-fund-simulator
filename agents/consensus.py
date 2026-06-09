from typing import Dict, Any, List
import numpy as np


class AgentConsensusEngine:
    def __init__(self):
        # In a real database, this would be dynamically fetched based on backtest performance
        self.historical_accuracy = {
            "macro_agent": 0.65,
            "technical_agent": 0.55,
            "news_agent": 0.60,
            "quant_agent": 0.75,
        }

    def _bayesian_update(
        self, prior: float, confidence: float, accuracy: float
    ) -> float:
        """
        Calculates the posterior probability (weight) of a signal being correct
        given the agent's historical accuracy and reported confidence.
        P(Correct | Signal) = [P(Signal | Correct) * P(Correct)] / P(Signal)
        """
        # Simplified Bayesian weighting approximation
        likelihood = accuracy * confidence
        evidence = likelihood + ((1 - accuracy) * (1 - confidence))
        if evidence == 0:
            return 0.0
        return likelihood / evidence

    def calculate_unified_signal(
        self, agent_outputs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Resolves conflicting agent recommendations into a single Black-Litterman view vector.
        Each agent provides: {"ticker": {"signal": 1 (Bull) / -1 (Bear), "confidence": 0.8}}
        """
        unified_views = {}
        unified_confidences = {}

        tickers = set()
        for agent_name, output in agent_outputs.items():
            for ticker in output.get("recommendations", {}).keys():
                tickers.add(ticker)

        for ticker in tickers:
            weighted_signal_sum = 0.0
            total_weight = 0.0

            for agent_name, output in agent_outputs.items():
                rec = output.get("recommendations", {}).get(ticker)
                if not rec:
                    continue

                raw_signal = rec.get("signal", 0.0)  # -1.0 to 1.0
                confidence = rec.get("confidence", 0.5)  # 0.0 to 1.0
                accuracy = self.historical_accuracy.get(agent_name, 0.5)

                weight = self._bayesian_update(
                    prior=0.5, confidence=confidence, accuracy=accuracy
                )

                weighted_signal_sum += raw_signal * weight
                total_weight += weight

            if total_weight > 0:
                final_signal = weighted_signal_sum / total_weight
                # Map signal (-1 to 1) to an expected return view (e.g., -5% to +5%)
                expected_return = final_signal * 0.05
                unified_views[ticker] = expected_return
                unified_confidences[ticker] = min(
                    total_weight / len(agent_outputs), 1.0
                )

        return unified_views, unified_confidences
