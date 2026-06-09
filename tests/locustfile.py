from locust import HttpUser, task, between
import random


class HedgeFundAPIUser(HttpUser):
    wait_time = between(1, 5)  # wait 1 to 5 seconds between tasks

    @task(3)
    def trigger_simulation(self):
        tickers = random.sample(
            ["AAPL", "MSFT", "GOOG", "TSLA", "NVDA", "AMZN", "META"], 3
        )

        headers = {"X-API-Key": "default-dev-key"}
        payload = {"tickers": tickers, "portfolio_value": 1000000.0}

        # We expect a task_id to be returned immediately
        response = self.client.post("/simulate", json=payload, headers=headers)

        if response.status_code == 200:
            task_id = response.json().get("task_id")
            if task_id:
                # Poll the status endpoint once to verify it exists
                self.client.get(f"/status/{task_id}", headers=headers)

    @task(1)
    def read_root(self):
        self.client.get("/")
