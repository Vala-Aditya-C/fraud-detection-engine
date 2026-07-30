import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Fraud Detection Dashboard", page_icon="💳", layout="wide")

st.title("💳 Real-Time Financial Fraud Detection Engine")

API_URL = "http://127.0.0.1:8000/v1/evaluate-transaction"
HISTORY_URL = "http://127.0.0.1:8000/v1/transactions/history"

# Initialize Session State to hold evaluation results across re-runs
if "eval_result" not in st.session_state:
    st.session_state.eval_result = None

tab1, tab2 = st.tabs(["⚡ Evaluate Transaction", "📜 Transaction Audit Log"])

# --- TAB 1: EVALUATE TRANSACTION ---
with tab1:
    st.sidebar.header("Transaction Inputs")
    user_id = st.sidebar.text_input("User ID", value="USR_88921")
    amount = st.sidebar.slider("Transaction Amount ($)", min_value=1.0, max_value=2000.0, value=250.0, step=5.0)
    time_delta = st.sidebar.slider("Seconds Since Last Transaction", min_value=0.1, max_value=300.0, value=1.5, step=0.1)
    geo_distance = st.sidebar.slider("Distance From Last Location (km)", min_value=0.0, max_value=500.0, value=120.0, step=1.0)
    is_foreign = st.sidebar.selectbox("Is Foreign Merchant?", options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No")

    if st.sidebar.button("Evaluate Transaction Risk", type="primary"):
        payload = {
            "user_id": user_id,
            "amount": amount,
            "time_delta": time_delta,
            "geo_distance": geo_distance,
            "is_foreign": is_foreign
        }
        
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                # Save response directly into session state
                st.session_state.eval_result = response.json()
            else:
                st.error(f"API Error ({response.status_code}): Could not evaluate transaction.")
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to FastAPI server.")

    # Render results whenever session_state has stored data
    if st.session_state.eval_result:
        data = st.session_state.eval_result
        status = data.get("status")
        risk_score = data.get("risk_score")
        reason = data.get("reason")
        latency = data.get("latency_ms")
        
        st.subheader("Latest Evaluation Result")
        if status == "BLOCKED":
            st.error(f"🚨 **STATUS: {status}**")
        elif status == "REVIEW":
            st.warning(f"⚠️ **STATUS: {status}**")
        else:
            st.success(f"✅ **STATUS: {status}**")
            
        res_col1, res_col2 = st.columns(2)
        res_col1.metric("Risk Score Probability", f"{risk_score * 100:.1f}%")
        res_col2.metric("Inference Latency", latency)
        st.progress(float(risk_score))
        st.info(f"**Decision Reason:** {reason}")


# --- TAB 2: TRANSACTION AUDIT LOG ---
with tab2:
    st.header("Recent Logged Transactions (Database Audit Trail)")
    
    # Auto-fetch history when Tab 2 opens, or allow manual refresh via button
    col_title, col_btn = st.columns([4, 1])
    with col_btn:
        refresh_clicked = st.button("🔄 Refresh Logs")

    try:
        res = requests.get(f"{HISTORY_URL}?limit=20")
        if res.status_code == 200:
            data = res.json()
            if data:
                df = pd.DataFrame(data)
                # Re-order columns nicely
                columns_order = ["id", "user_id", "status", "risk_score", "amount", "time_delta", "geo_distance", "is_foreign", "reason", "timestamp"]
                existing_cols = [c for c in columns_order if c in df.columns]
                st.dataframe(df[existing_cols], use_container_width=True)
            else:
                st.info("No transaction logs found in database yet. Evaluate some transactions on Tab 1!")
    except Exception as e:
        st.error(f"Could not load audit logs automatically: {e}")