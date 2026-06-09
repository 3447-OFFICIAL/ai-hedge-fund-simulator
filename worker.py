from celery import Celery
import os
import asyncio
from datetime import datetime
from workflows.graph import create_hedge_fund_graph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

celery_app = Celery(
    "hedge_fund_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minute hard timeout
)


async def _run_async_graph(tickers: list, portfolio_value: float, task_id: str):
    # Setup Postgres Saver for LangGraph State Durability
    db_uri = os.getenv(
        "POSTGRES_URI", "postgresql://postgres:postgres@localhost:5432/hedge_fund"
    )

    async with AsyncPostgresSaver.from_conn_string(db_uri) as checkpointer:
        await checkpointer.setup()
        graph = create_hedge_fund_graph(checkpointer=checkpointer)

        initial_state = {
            "messages": [],
            "tickers": tickers,
            "portfolio_value": portfolio_value,
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "macro_outlook": {},
            "technical_analysis": {},
            "news_sentiment": {},
            "quant_factors": {},
            "risk_limits": {},
            "portfolio_decision": {},
        }

        config = {"configurable": {"thread_id": task_id}}

        # Execute the workflow with persistent checkpointing
        result_state = await graph.ainvoke(initial_state, config=config)

        return {
            "status": "success",
            "task_id": task_id,
            "date": result_state["current_date"],
            "portfolio_decision": result_state["portfolio_decision"],
        }


@celery_app.task(bind=True, name="tasks.run_simulation")
def run_simulation_task(self, tickers: list, portfolio_value: float):
    # Bridge the sync celery worker to the async langgraph execution
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            _run_async_graph(tickers, portfolio_value, str(self.request.id))
        )
    finally:
        loop.close()
