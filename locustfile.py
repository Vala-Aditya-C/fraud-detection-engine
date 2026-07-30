from locust import HttpUser, task, between

class TransactionUser(HttpUser):
    wait_time = between(0.01, 0.05)

    @task
    def evaluate_transaction(self):
        self.client.post("/v1/evaluate-transaction", json={
            "user_id": "USR_BENCHMARK",
            "amount": 150.00,
            "time_delta": 10.0,
            "geo_distance": 5.0,
            "is_foreign": 0
        })