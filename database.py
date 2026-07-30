import sqlite3
from datetime import datetime

DB_NAME = "transactions.db"

def init_db():
    """Create the transactions table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            amount REAL,
            distance_from_home REAL,
            distance_from_last_transaction REAL,
            ratio_to_median_purchase_price REAL,
            repeat_retailer INTEGER,
            used_chip INTEGER,
            used_pin_number INTEGER,
            online_order INTEGER,
            prediction INTEGER,
            fraud_probability REAL
        )
    """)
    conn.commit()
    conn.close()

def log_transaction(data: dict, prediction: int, probability: float):
    """Log prediction result and parameters to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (
            timestamp, amount, distance_from_home, distance_from_last_transaction,
            ratio_to_median_purchase_price, repeat_retailer, used_chip,
            used_pin_number, online_order, prediction, fraud_probability
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        data.get("amount", 0.0),
        data.get("distance_from_home", 0.0),
        data.get("distance_from_last_transaction", 0.0),
        data.get("ratio_to_median_purchase_price", 0.0),
        data.get("repeat_retailer", 0),
        data.get("used_chip", 0),
        data.get("used_pin_number", 0),
        data.get("online_order", 0),
        int(prediction),
        float(probability)
    ))
    conn.commit()
    conn.close()