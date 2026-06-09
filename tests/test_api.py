import pytest
from fastapi.testclient import TestClient
from api.main import app
import pandas as pd
from optimization.portfolio_optimizer import PortfolioOptimizer

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the AI Hedge Fund Simulator API"}


def test_simulate_unauthorized():
    response = client.post(
        "/simulate", json={"tickers": ["AAPL", "MSFT"], "portfolio_value": 100000}
    )
    # Should be 401 due to APIKeyHeader dependency
    assert response.status_code == 401


def test_simulate_authorized_but_invalid_payload():
    response = client.post(
        "/simulate",
        headers={"X-API-Key": "default-dev-key"},
        json={
            "tickers": ["AAPL"] * 25,  # Too many, should trigger max_length validation
            "portfolio_value": -100,  # Invalid value
        },
    )
    assert response.status_code == 422  # Unprocessable Entity (Pydantic Validation)


def test_portfolio_optimizer():
    optimizer = PortfolioOptimizer()

    # Create dummy historical data
    dates = pd.date_range("2023-01-01", periods=10)
    data = pd.DataFrame(
        {
            "AAPL": [150, 152, 151, 155, 156, 154, 158, 160, 159, 162],
            "MSFT": [250, 255, 252, 260, 262, 260, 265, 270, 268, 275],
        },
        index=dates,
    )

    weights, perf = optimizer.optimize_sharpe_ratio(data)

    assert "AAPL" in weights
    assert "MSFT" in weights
    assert sum(weights.values()) == pytest.approx(1.0)

    expected_return, volatility, sharpe = perf
    assert expected_return > 0
    assert volatility > 0
