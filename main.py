from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import time

app = FastAPI(
    title="Real-Time Fraud Detection Engine",
    description="High-throughput API scoring card transactions against ML risk models.",
    version="1.0.0"
)

try:
    model = joblib.load('fraud_model.joblib')
except Exception:
    model = None

class TransactionRequest(BaseModel):
    user_id: str = Field(..., example="USR_10492")
    amount: float = Field(..., example=420.50)
    time_delta: float = Field(..., example=1.8, description="Seconds since last transaction")
    geo_distance: float = Field(..., example=85.0, description="Distance in km from last transaction")
    is_foreign: int = Field(..., example=1, description="1 if foreign merchant, 0 otherwise")

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/v1/evaluate-transaction")
async def evaluate_transaction(txn: TransactionRequest):
    if not model:
        raise HTTPException(status_code=500, detail="ML model is not loaded.")
    
    start_time = time.perf_counter()

    features = pd.DataFrame([{
        'amount': txn.amount,
        'time_delta': txn.time_delta,
        'geo_distance': txn.geo_distance,
        'is_foreign': txn.is_foreign
    }])

    fraud_probability = float(model.predict_proba(features)[0][1])

    if fraud_probability >= 0.70:
        status = "BLOCKED"
        reason = "High anomaly risk: Rapid succession & geographic anomaly detected."
    elif fraud_probability >= 0.35:
        status = "REVIEW"
        reason = "Medium risk: Step-up authentication required."
    else:
        status = "APPROVED"
        reason = "Transaction clear."

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "user_id": txn.user_id,
        "status": status,
        "risk_score": round(fraud_probability, 4),
        "reason": reason,
        "latency_ms": f"{latency_ms}ms"
    }