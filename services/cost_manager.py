import os
import redis
import json
import hashlib
from fastapi import HTTPException


class CostGovernanceManager:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/1")
        )
        self.daily_budget_usd = float(os.getenv("DAILY_LLM_BUDGET_USD", "50.0"))

        # Approximate gpt-4o pricing
        self.cost_per_1k_input = 0.005
        self.cost_per_1k_output = 0.015

    def _generate_cache_key(self, prompt: str) -> str:
        return f"llm_cache:{hashlib.sha256(prompt.encode()).hexdigest()}"

    def check_semantic_cache(self, prompt: str) -> str:
        """Returns cached LLM output to save money if identical query was made recently."""
        cached = self.redis_client.get(self._generate_cache_key(prompt))
        if cached:
            return cached.decode("utf-8")
        return None

    def set_cache(self, prompt: str, response: str, ttl_seconds: int = 3600):
        self.redis_client.setex(self._generate_cache_key(prompt), ttl_seconds, response)

    def log_token_usage(self, user_id: str, input_tokens: int, output_tokens: int):
        """Records token usage and trips circuit breaker if budget exceeded."""
        cost = ((input_tokens / 1000.0) * self.cost_per_1k_input) + (
            (output_tokens / 1000.0) * self.cost_per_1k_output
        )

        budget_key = f"budget:{user_id}"
        current_spend = self.redis_client.incrbyfloat(budget_key, cost)

        # Set expiry for daily budget tracking
        if self.redis_client.ttl(budget_key) == -1:
            self.redis_client.expire(budget_key, 86400)  # 24 hours

        if current_spend > self.daily_budget_usd:
            raise HTTPException(
                status_code=429, detail="Daily LLM budget circuit breaker tripped."
            )
