# Project Structure

This document outlines the architectural layout of the AI Hedge Fund Simulator repository.

```text
ai-hedge-fund-simulator/
├── agents/                 # LangGraph nodes and AI agent logic
│   ├── base.py             # Base agent class with LLM initialization
│   ├── macro/              # Macro Analyst Agent
│   ├── technical/          # Technical Analyst Agent
│   ├── news/               # News Analyst Agent
│   ├── quant/              # Quant Research Agent
│   ├── risk/               # Risk Manager Agent
│   └── portfolio/          # Portfolio Manager Agent
│
├── api/                    # FastAPI backend
│   └── main.py             # Core REST API and LangGraph execution endpoint
│
├── backtesting/            # Historical simulation engines
│   └── engine.py           # Backtrader and FinRL integrations
│
├── dashboard/              # Streamlit frontend
│   └── app.py              # Interactive user interface and XAI visualization
│
├── data/                   # Data pipelines and APIs
│   ├── market_data.py      # yfinance integrations
│   └── news_scraper.py     # Web scraping for financial news
│
├── optimization/           # Quantitative analytics
│   ├── analytics.py        # Sharpe, VaR, Max Drawdown calculations
│   └── portfolio_optimizer.py # PyPortfolioOpt integrations
│
├── workflows/              # LangGraph orchestration
│   ├── graph.py            # Directed acyclic graph definition
│   └── state.py            # AgentState schema definition
│
├── tests/                  # Pytest suite
│
├── docs/                   # Documentation and architectural records
│
├── infrastructure/         # Deployment manifests (Docker, K8s)
│
├── .github/workflows/      # GitHub Actions CI/CD
│   └── ci.yml              # Linting and testing pipelines
│
├── docker-compose.yml      # Local infrastructure setup (Postgres, Redis)
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
├── README.md               # Main project documentation
├── LICENSE                 # MIT License
└── CONTRIBUTING.md         # Guidelines for open-source contributors
```
