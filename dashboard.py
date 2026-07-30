import streamlit as st
import pandas as pd
import sqlite3
import requests
import json

# Page Config
st.set_page_config(
    page_title="Fraud Detection Engine",
    page_icon="💳",
    layout="wide"
)

st.title("💳 Real-Time Fraud Detection Dashboard")

# Backend Endpoint
API_URL = "http://127.0.0.1:8000/evaluate"

# Tab layout
tab1, tab2 = st.tabs(["🔍 Evaluate Transaction", "📊 Transaction History & Analytics"])

with tab1:
    st.subheader("Input Transaction Details")
    
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Transaction Amount ($)", min_value=0.0, value=150.0)
        distance_from_home = st.number_input("Distance from Home (miles)", min_value=0.0, value=5.0)
        distance_from_last = st.number_input("Distance from Last Transaction (miles)", min_value=0.0, value=1.0)
        ratio_median = st.number_input("Ratio to Median Purchase Price", min_value=0.0, value=1.2)
        
    with col2:
        repeat_retailer = st.selectbox("Repeat Retailer?", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
        used_chip = st.selectbox("Used Chip?", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
        used_pin = st.selectbox("Used PIN Number?", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
        online_order = st.selectbox("Online Order?", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")

    if st.button("Evaluate Risk"):
        payload = {
            "amount": amount,
            "distance_from_home": distance_from_home,
            "distance_from_last_transaction": distance_from_last,
            "ratio_to_median_purchase_price": ratio_median,
            "repeat_retailer": repeat_retailer,
            "used_chip": used_chip,
            "used_pin_number": used_pin,
            "online_order": online_order
        }
        
        try:
            res = requests.post(API_URL, json=payload)
            if res.status_code == 200:
                result = res.json()
                is_fraud = result.get("is_fraud", 0)
                prob = result.get("fraud_probability", 0.0)
                
                st.divider()
                if is_fraud == 1:
                    st.error(f"⚠️ HIGH RISK TRANSACTION DETECTED! Probability: {prob * 100:.2f}%")
                else:
                    st.success(f"✅ TRANSACTION LEGITIMATE. Probability: {prob * 100:.2f}%")
            else:
                st.warning(f"Backend Returned Code {res.status_code}")
        except Exception as e:
            st.error(f"Failed to connect to FastAPI backend: {e}")

with tab2:
    st.subheader("Database Records & Risk Metrics")
    
    try:
        conn = sqlite3.connect("transactions.db")
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY id DESC", conn)
        conn.close()
        
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Transactions Evaluated", len(df))
            c2.metric("Total Flagged Frauds", int(df['prediction'].sum()))
            c3.metric("Average Fraud Probability", f"{df['fraud_probability'].mean() * 100:.1f}%")
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No transaction records logged in SQLite database yet.")
    except Exception as e:
        st.info("Database not initialized yet or empty.")