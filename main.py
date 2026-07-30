import time
import joblib
import pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import init_db, get_db, TransactionLog, AsyncSessionLocal

# Global model variable
model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern FastAPI lifespan handler replacing legacy on_event startup/shutdown handlers."""
    global model
    try:
        model = joblib.load("fraud_model.joblib")
    except Exception:
        model = None
    await init_db()
    yield


app = FastAPI(
    title="Real-Time Financial Fraud Detection Engine",
    version="1.0.0",
    description="Low-latency REST API evaluating payment transaction risk scores using XGBoost.",
    lifespan=lifespan
)


# Pydantic V2 compliant request model
class TransactionRequest(BaseModel):
    user_id: str = Field(..., json_schema_extra={"example": "USR_10492"})
    amount: float = Field(..., json_schema_extra={"example": 420.50})
    time_delta: float = Field(..., json_schema_extra={"example": 1.8}, description="Seconds since last transaction")
    geo_distance: float = Field(..., json_schema_extra={"example": 85.0}, description="Distance in km from last location")
    is_foreign: int = Field(..., json_schema_extra={"example": 1}, description="1 if foreign merchant, 0 otherwise")


async def log_transaction_to_db(payload: dict, status: str, risk_score: float, reason: str):
    """Background task to record transaction audit log without blocking inference response."""
    async with AsyncSessionLocal() as session:
        log_entry = TransactionLog(
            user_id=payload["user_id"],
            amount=payload["amount"],
            time_delta=payload["time_delta"],
            geo_distance=payload["geo_distance"],
            is_foreign=payload["is_foreign"],
            status=status,
            risk_score=risk_score,
            reason=reason
        )
        session.add(log_entry)
        await session.commit()


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }


@app.post("/v1/evaluate-transaction")
async def evaluate_transaction(txn: TransactionRequest, background_tasks: BackgroundTasks):
    if model is None:
        raise HTTPException(status_code=500, detail="ML model is not loaded.")

    start_time = time.perf_counter()

    features = pd.DataFrame([{
        "amount": txn.amount,
        "time_delta": txn.time_delta,
        "geo_distance": txn.geo_distance,
        "is_foreign": txn.is_foreign
    }])

    # ML Inference
    risk_prob = float(model.predict_proba(features)[0][1])

    # Rule-Based Decision Logic
    if risk_prob >= 0.70:
        status = "BLOCKED"
        reason = f"High Risk Probability ({risk_prob:.2%}) exceeded safety threshold (0.70)"
    elif risk_prob >= 0.40:
        status = "REVIEW"
        reason = f"Moderate Risk Probability ({risk_prob:.2%}) requires secondary verification"
    else:
        status = "APPROVED"
        reason = "Transaction within normal behavioral limits"

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # Trigger Async DB Logging Task
    background_tasks.add_task(
        log_transaction_to_db,
        payload=txn.model_dump(),
        status=status,
        risk_score=risk_prob,
        reason=reason
    )

    return {
        "status": status,
        "risk_score": round(risk_prob, 4),
        "reason": reason,
        "latency_ms": f"{latency_ms} ms"
    }


@app.get("/v1/transactions/history")
async def get_transaction_history(limit: int = Query(default=20, le=100), db: AsyncSession = Depends(get_db)):
    """Retrieve recent transaction audit logs from SQLite database."""
    result = await db.execute(
        select(TransactionLog).order_by(TransactionLog.id.desc()).limit(limit)
    )
    logs = result.scalars().all()

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "amount": log.amount,
            "time_delta": log.time_delta,
            "geo_distance": log.geo_distance,
            "is_foreign": log.is_foreign,
            "status": log.status,
            "risk_score": log.risk_score,
            "reason": log.reason,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None
        }
        for log in logs
    ]