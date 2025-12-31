import pandas as pd
from sklearn.ensemble import IsolationForest
import streamlit as st

# Load data
data = pd.read_csv("data.csv")

# Select features
features = data[["amount", "transactions_per_month"]]

# Train model
model = IsolationForest(contamination=0.2, random_state=42)
data["anomaly"] = model.fit_predict(features)

# Convert output
data["risk"] = data["anomaly"].apply(lambda x: "High" if x == -1 else "Low")

# Streamlit UI
st.title("AI Fraud & Anomaly Detection Prototype")
st.write("Flagged Transactions")

st.dataframe(data)
st.caption(
    "Transactions are flagged as High Risk when their spending pattern "
    "significantly deviates from typical behavior."
)
