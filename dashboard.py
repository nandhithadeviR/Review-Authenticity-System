import streamlit as st
import pandas as pd
import random
from datetime import datetime
from analyzer import calculate_trust_score
    
# Initialize session state for review logs if it doesn't exist
if "reviews_log" not in st.session_state:
    st.session_state.reviews_log = [
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "review_text": "This product is amazing! Highly recommended.",
            "trust_score": 92.5,
            "status": "Authentic"
        },
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "review_text": "Buy this now! Cheap product, best deal ever click link.",
            "trust_score": 15.0,
            "status": "Spam/Fake"
        }
    ]

st.set_page_config(page_title="Review Authenticity Dashboard", layout="wide")

st.title("🛡️ ReviewGaurd")
st.markdown("Real-time cloud monitoring pipeline for processed browser extension reviews.")
# Catch incoming automated streams from the ReviewGuard Browser Extension
query_params = st.query_params

if "incoming_review" in query_params:
    remote_text = query_params["incoming_review"]
    remote_platform = query_params.get("platform", "Extension")
    remote_domain = query_params.get("domain", "General")
    
    # Run the analysis engine immediately on the intercepted data
    score_results = calculate_trust_score(remote_text, remote_platform, remote_domain)
    
    # Log it straight to your dashboard visualizer screen
    new_log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "review_text": remote_text,
        "trust_score": score_results["trust_score"],
        "status": score_results["status"]
    }
    st.session_state.reviews_log.insert(0, new_log)
# --- API Endpoint Simulation for the Extension ---
# This allows the dashboard to display incoming requests
query_params = st.query_params
if "text" in query_params:
    incoming_text = query_params["text"]
    # Calculate score using your existing analyzer logic
    score, status, break_down = calculate_trust_score(incoming_text)
    
    # Save log row
    new_log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "review_text": incoming_text,
        "trust_score": round(score, 1),
        "status": status
    }
    st.session_state.reviews_log.insert(0, new_log)
    st.success("New review intercepted from browser extension!")

# --- Metric Cards ---
df = pd.DataFrame(st.session_state.reviews_log)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Reviews Intercepted", len(df))
with col2:
    st.metric("Average Trust Score", f"{round(df['trust_score'].mean(), 1)}%")
with col3:
    st.metric("Flagged Fake Reviews", len(df[df['status'] == "Spam/Fake"]))

st.write("---")

# --- Interactive Log Table ---
st.subheader("📋 Real-Time Analysis Logs")
st.dataframe(df, use_container_width=True)
