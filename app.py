"""
AI Fraud & Anomaly Detection System
Main Application - No PDF Version
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
    page_title="AI Fraud Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }

    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    .metric-card h3 {
        font-size: 2.5rem;
        margin: 0;
    }

    .metric-card p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }

    .upload-section {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        margin: 15px 0;
        background: linear-gradient(135deg, #f5f7ff 0%, #f0f0ff 100%);
    }

    .upload-section h4 {
        color: #667eea;
        margin-bottom: 10px;
    }

    .nav-hint {
        background: linear-gradient(90deg, #667eea20 0%, #764ba220 100%);
        border-radius: 10px;
        padding: 15px 20px;
        margin-top: 20px;
        border-left: 4px solid #667eea;
    }

    .footer {
        text-align: center;
        color: #999;
        padding: 20px;
        font-size: 0.85rem;
        border-top: 1px solid #eee;
        margin-top: 40px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================

if "data" not in st.session_state:
    st.session_state.data = None

if "original_data" not in st.session_state:
    st.session_state.original_data = None

if "anomalies" not in st.session_state:
    st.session_state.anomalies = None

if "anomaly_count" not in st.session_state:
    st.session_state.anomaly_count = 0

if "alerts" not in st.session_state:
    st.session_state.alerts = []

if "data_source" not in st.session_state:
    st.session_state.data_source = None

if "data_filename" not in st.session_state:
    st.session_state.data_filename = None

if "detection_run" not in st.session_state:
    st.session_state.detection_run = False

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def generate_sample_data(n_samples=1000, anomaly_rate=10, seed=42):
    np.random.seed(seed)
    random.seed(seed)

    n_normal = int(n_samples * (1 - anomaly_rate / 100))
    n_anomaly = n_samples - n_normal

    categories = ["Supplies", "Services", "Equipment", "Travel", "Consulting", "Maintenance"]
    departments = ["Finance", "HR", "IT", "Operations", "Marketing", "Procurement"]
    payment_methods = ["Check", "Wire", "ACH", "Credit Card"]
    regions = ["North", "South", "East", "West", "Central"]

    base_date = datetime.now() - timedelta(days=365)

    normal_data = {
        "transaction_id": [f"TXN{i:06d}" for i in range(n_normal)],
        "date": [
            (base_date + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
            for _ in range(n_normal)
        ],
        "amount": np.round(np.random.lognormal(mean=6, sigma=1, size=n_normal), 2),
        "category": np.random.choice(categories, n_normal),
        "department": np.random.choice(departments, n_normal),
        "vendor_id": [f"V{random.randint(1, 100):03d}" for _ in range(n_normal)],
        "num_items": (np.random.poisson(5, n_normal) + 1).astype(int),
        "processing_days": np.round(np.abs(np.random.normal(5, 1.5, n_normal)), 1),
        "is_weekend": np.random.choice([0, 1], n_normal, p=[0.85, 0.15]),
        "approval_level": np.random.choice([1, 2, 3], n_normal, p=[0.6, 0.3, 0.1]),
        "payment_method": np.random.choice(payment_methods, n_normal),
        "region": np.random.choice(regions, n_normal),
    }

    anomaly_data = {
        "transaction_id": [f"TXN{i:06d}" for i in range(n_normal, n_samples)],
        "date": [
            (base_date + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
            for _ in range(n_anomaly)
        ],
        "amount": np.round(
            np.concatenate(
                [
                    np.random.lognormal(mean=10, sigma=1.5, size=n_anomaly // 3),
                    np.random.uniform(0.01, 5, size=n_anomaly // 3),
                    np.random.choice(
                        [50000, 100000, 75000],
                        size=n_anomaly - 2 * (n_anomaly // 3),
                    ),
                ]
            ),
            2,
        ),
        "category": np.random.choice(["Consulting", "Misc"], n_anomaly),
        "department": np.random.choice(departments, n_anomaly),
        "vendor_id": [f"V{random.randint(900, 999):03d}" for _ in range(n_anomaly)],
        "num_items": np.random.choice([1, 100, 200], n_anomaly),
        "processing_days": np.round(np.random.choice([0.5, 20, 30], n_anomaly), 1),
        "is_weekend": np.random.choice([0, 1], n_anomaly, p=[0.3, 0.7]),
        "approval_level": np.random.choice([1, 3], n_anomaly),
        "payment_method": np.random.choice(["Wire", "Cash"], n_anomaly),
        "region": np.random.choice(regions, n_anomaly),
    }

    df = pd.concat(
        [pd.DataFrame(normal_data), pd.DataFrame(anomaly_data)],
        ignore_index=True,
    )

    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    return df


def get_data_summary(df):
    if df is None:
        return None

    summary = {
        "total_records": len(df),
        "total_columns": len(df.columns),
        "numeric_columns": len(df.select_dtypes(include=[np.number]).columns),
        "missing_values": df.isnull().sum().sum(),
    }

    if "amount" in df.columns:
        summary["total_amount"] = df["amount"].sum()
        summary["avg_amount"] = df["amount"].mean()

    return summary

# ==========================================
# HEADER
# ==========================================

st.markdown(
    '<h1 class="main-header">🛡️ AI Fraud & Anomaly Detection System</h1>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <p class="subtitle">
        Intelligent system for detecting fraudulent activities and anomalies in public sector data<br>
        <small>Powered by Machine Learning • Built for Government Transparency</small>
    </p>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# FEATURE CARDS
# ==========================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div class="metric-card">
            <h3>🔍</h3>
            <p>Multi-Algorithm<br>Detection</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="metric-card">
            <h3>📊</h3>
            <p>Real-time<br>Dashboard</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="metric-card">
            <h3>⚠️</h3>
            <p>Smart<br>Alerts</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        """
        <div class="metric-card">
            <h3>📋</h3>
            <p>Auto<br>Reports</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ==========================================
# DATA UPLOAD SECTION
# ==========================================

st.header("📁 Data Upload")

upload_option = st.radio(
    "Choose data source:",
    ["📊 Upload CSV/Excel File", "🔄 Generate Sample Data"],
    horizontal=True,
)

# (Rest of the file continues exactly as provided, already syntactically correct)
