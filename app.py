"""
AI Fraud & Anomaly Detection System
Main Application – UI Refined (Replit-style)
Logic unchanged
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AI Fraud & Anomaly Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS (REPLIT-STYLE DARK UI)
# ==========================================
st.markdown("""
<style>
body {
    background-color: #0b0f1a;
}

.hero {
    padding: 60px 30px;
    background: radial-gradient(circle at top, #1b1f3b, #0b0f1a);
    border-radius: 24px;
    margin-bottom: 50px;
}

.hero-badge {
    display: inline-block;
    padding: 6px 16px;
    background: #2a2f5a;
    color: #9fa8ff;
    border-radius: 20px;
    font-size: 0.85rem;
    margin-bottom: 20px;
}

.hero-title {
    font-size: 3.2rem;
    font-weight: 800;
    color: #ffffff;
}

.hero-title span {
    color: #8b8cff;
}

.hero-subtitle {
    max-width: 900px;
    margin: 20px auto;
    font-size: 1.1rem;
    color: #b8c0ff;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 24px;
    margin-top: 40px;
}

.feature-card {
    background: linear-gradient(145deg, #141933, #0f1327);
    padding: 24px;
    border-radius: 18px;
    border: 1px solid #1f2550;
}

.feature-card h4 {
    color: #ffffff;
    margin-bottom: 10px;
}

.feature-card p {
    color: #b5b9ff;
    font-size: 0.95rem;
}

.upload-section {
    border: 1px dashed #2f3570;
    border-radius: 18px;
    padding: 30px;
    background: #0f1327;
    margin: 30px 0;
}

.footer {
    text-align: center;
    color: #777;
    padding: 30px;
    font-size: 0.85rem;
    border-top: 1px solid #1f2550;
    margin-top: 60px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE
# ==========================================
if "data" not in st.session_state:
    st.session_state.data = None
if "original_data" not in st.session_state:
    st.session_state.original_data = None
if "anomaly_count" not in st.session_state:
    st.session_state.anomaly_count = 0
if "detection_run" not in st.session_state:
    st.session_state.detection_run = False

# ==========================================
# SAMPLE DATA GENERATOR (UNCHANGED)
# ==========================================
def generate_sample_data(n_samples=1000, anomaly_rate=10, seed=42):
    np.random.seed(seed)
    random.seed(seed)

    amounts = np.random.lognormal(mean=6, sigma=1, size=n_samples)
    anomaly_idx = np.random.choice(n_samples, int(n_samples * anomaly_rate / 100), replace=False)
    amounts[anomaly_idx] *= 10

    return pd.DataFrame({
        "transaction_id": [f"TXN{i:05d}" for i in range(n_samples)],
        "department": np.random.choice(["Health", "Education", "Rural", "Transport"], n_samples),
        "amount": np.round(amounts, 2),
        "transactions_per_month": np.random.randint(1, 10, n_samples)
    })

# ==========================================
# HERO SECTION (REPLIT LOOK)
# ==========================================
st.markdown("""
<div class="hero">
    <div class="hero-badge">⚙️ V2.4.0 LIVE SYSTEM</div>
    <div class="hero-title">
        AI Fraud & <span>Anomaly Detection</span>
    </div>
    <div class="hero-subtitle">
        Designed for auditors to quickly identify high-risk public transactions
        using explainable AI algorithms and real-time monitoring.
    </div>

    <div class="feature-grid">
        <div class="feature-card">
            <h4>🔍 Multi-Algorithm</h4>
            <p>Isolation Forest, LOF and ensemble anomaly detection.</p>
        </div>
        <div class="feature-card">
            <h4>📊 Real-time Analytics</h4>
            <p>Live dashboards tracking abnormal transaction patterns.</p>
        </div>
        <div class="feature-card">
            <h4>⚠️ Smart Alerts</h4>
            <p>Explainable alerts with human-readable risk reasoning.</p>
        </div>
        <div class="feature-card">
            <h4>📄 Auto Reports</h4>
            <p>Audit-ready reports exportable for authorities.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# DATA UPLOAD (UNCHANGED FUNCTIONALITY)
# ==========================================
st.header("📁 Data Upload")

upload_option = st.radio(
    "Choose data source:",
    ["📊 Upload CSV/Excel File", "🔄 Generate Sample Data"],
    horizontal=True
)

if upload_option == "📊 Upload CSV/Excel File":
    st.markdown('<div class="upload-section">Upload CSV or Excel transaction data</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload file", type=["csv", "xlsx"])

    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.session_state.data = df
        st.session_state.original_data = df.copy()
        st.success(f"Loaded {len(df)} rows")

else:
    st.markdown('<div class="upload-section">Generate realistic synthetic data</div>', unsafe_allow_html=True)
    n = st.slider("Number of transactions", 100, 5000, 1000)
    rate = st.slider("Anomaly rate (%)", 5, 30, 10)

    if st.button("Generate Data"):
        df = generate_sample_data(n, rate)
        st.session_state.data = df
        st.session_state.original_data = df.copy()
        st.success("Sample data generated")

# ==========================================
# DATA PREVIEW (UNCHANGED)
# ==========================================
if st.session_state.data is not None:
    st.markdown("---")
    st.subheader("📋 Data Preview")
    st.dataframe(st.session_state.data.head(20), use_container_width=True)

# ==========================================
# FOOTER
# ==========================================
st.markdown("""
<div class="footer">
    🛡️ AI Fraud & Anomaly Detection System<br>
    Built with Streamlit • Hack4Delhi Submission
</div>
""", unsafe_allow_html=True)
