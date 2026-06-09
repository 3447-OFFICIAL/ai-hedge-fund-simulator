from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import os
import json
import asyncio

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from worker import run_simulation_task, celery_app
from celery.result import AsyncResult

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="AI Hedge Fund Simulator API (Event-Driven)",
    description="Enterprise API for the Multi-Agent Hedge Fund Simulator",
    version="2.0.0",
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Instrument for Observability
FastAPIInstrumentor.instrument_app(app)

# Secure CORS config
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key(api_key_header: str = Depends(api_key_header)):
    expected_key = os.getenv("HEDGE_FUND_API_KEY", "default-dev-key")
    if not api_key_header or api_key_header != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return api_key_header


class RunSimulationRequest(BaseModel):
    tickers: List[str] = Field(
        ..., max_length=20, description="List of stock tickers (max 20)"
    )
    portfolio_value: float = Field(..., gt=0, description="Initial portfolio value")


@app.get("/")
@limiter.limit("60/minute")
def read_root(request: Request):
    return {"message": "Welcome to the Enterprise AI Hedge Fund Simulator API"}


@app.post("/simulate")
@limiter.limit("20/minute")  # Increased capacity due to queue architecture
async def queue_simulation(
    request: Request,
    sim_request: RunSimulationRequest,
    api_key: str = Depends(get_api_key),
):
    """Queues a simulation task to Celery workers and returns immediately."""
    task = run_simulation_task.delay(sim_request.tickers, sim_request.portfolio_value)

    return {
        "status": "queued",
        "task_id": task.id,
        "message": "Simulation is processing. Poll /status/{task_id} or connect via WebSockets.",
    }


@app.get("/status/{task_id}")
async def get_task_status(task_id: str, api_key: str = Depends(get_api_key)):
    """Polls the status of an asynchronous simulation task."""
    task_result = AsyncResult(task_id, app=celery_app)

    response = {"task_id": task_id, "status": task_result.status}

    if task_result.status == "SUCCESS":
        response["result"] = task_result.result
    elif task_result.status == "FAILURE":
        response["error"] = str(task_result.result)

    return response


@app.websocket("/ws/status/{task_id}")
async def websocket_status_endpoint(websocket: WebSocket, task_id: str):
    """Streams task status updates over WebSocket until completion."""
    await websocket.accept()

    try:
        while True:
            task_result = AsyncResult(task_id, app=celery_app)

            payload = {"task_id": task_id, "status": task_result.status}

            if task_result.status == "SUCCESS":
                payload["result"] = task_result.result
                await websocket.send_json(payload)
                break
            elif task_result.status == "FAILURE":
                payload["error"] = str(task_result.result)
                await websocket.send_json(payload)
                break

            await websocket.send_json(payload)
            await asyncio.sleep(2)  # Poll interval

    except WebSocketDisconnect:
        print(f"Client disconnected from WebSocket for task: {task_id}")
