"""
AI Fraud & Anomaly Detection System
Main Application - UI Refined (Logic Preserved)
Day 2 Updates: Department Filter, Button Wording, UX Cleanup
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
# CUSTOM CSS (DARK UI – REPLIT STYLE)
# ==========================================
st.markdown("""
<style>
body {
    background-color: #0b0f1a;
}
.main-title {
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #7c7cff, #9f7cff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.subtitle {
    text-align: center;
    color: #b8c1ec;
    margin-bottom: 2.5rem;
    font-size: 1.1rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.2rem;
    margin-top: 2rem;
}
.feature-card {
    background: linear-gradient(145deg, #12172a, #0d1220);
    border-radius: 16px;
    padding: 1.4rem;
    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    transition: all 0.3s ease;
}
.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(124,124,255,0.25);
}
.feature-card h4 {
    color: #ffffff;
    margin-bottom: 0.4rem;
}
.feature-card p {
    color: #aab1d6;
    font-size: 0.95rem;
}

.section-box {
    background: #0f1424;
    padding: 1.5rem;
    border-radius: 16px;
    margin-top: 2rem;
    border: 1px solid #1c2340;
}

.department-selector {
    background: linear-gradient(145deg, #1a1f3a, #0f1424);
    padding: 1.5rem;
    border-radius: 12px;
    border: 2px solid #7c7cff;
    margin: 2rem 0;
}

.footer {
    text-align: center;
    color: #7a83b8;
    font-size: 0.85rem;
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE
# ==========================================
if 'data' not in st.session_state:
    st.session_state.data = None
if 'detection_run' not in st.session_state:
    st.session_state.detection_run = False
if 'selected_department' not in st.session_state:
    st.session_state.selected_department = 'All Departments'

# ==========================================
# SAMPLE DATA GENERATOR (UNCHANGED)
# ==========================================
def generate_sample_data(n_samples=1000, anomaly_rate=10):
    np.random.seed(42)
    data = {
        "transaction_id": range(1, n_samples + 1),
        "department": np.random.choice(["Finance", "Health", "Education", "Procurement", "Operations", "IT", "HR", "Marketing"], n_samples),
        "amount": np.random.lognormal(6, 1, n_samples).round(2),
        "transactions_per_month": np.random.randint(1, 10, n_samples),
        "date": pd.date_range(start="2024-01-01", periods=n_samples, freq="H").strftime("%Y-%m-%d"),
        "vendor": np.random.choice(["Vendor A", "Vendor B", "Vendor C", "Unknown Vendor", "Supplier X"], n_samples),
        "purpose": np.random.choice(["Office Supplies", "Software License", "Consulting", "Equipment", "Services"], n_samples),
        "payment_method": np.random.choice(["Credit Card", "Wire Transfer", "Purchase Order", "Check"], n_samples),
        "approval_status": np.random.choice(["Approved", "Pending", "Approved", "Approved"], n_samples)
    }
    return pd.DataFrame(data)

# ==========================================
# HEADER
# ==========================================
st.markdown('<div class="main-title">AI Fraud & Anomaly Detection</div>', unsafe_allow_html=True)
st.markdown("""
<div class="subtitle">
Designed for auditors to identify high-risk public transactions using explainable AI and real-time monitoring.
</div>
""", unsafe_allow_html=True)

# ==========================================
# GLOBAL DEPARTMENT SELECTOR (NEW)
# ==========================================
st.markdown('<div class="department-selector">', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    department_filter = st.selectbox(
        "🏛️ Select Department for Analysis",
        ["All Departments", "Finance", "Health", "Education", "Procurement", "Operations", "IT", "HR", "Marketing"],
        key="global_department_filter",
        help="Filter all views by department"
    )
    st.session_state['selected_department'] = department_filter

with col2:
    if department_filter == "All Departments":
        st.metric("Active Filter", "All Depts", delta="Global View")
    else:
        st.metric("Active Filter", department_filter, delta="Filtered")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# FEATURE CARDS
# ==========================================
st.markdown("""
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
""", unsafe_allow_html=True)

# ==========================================
# DATA UPLOAD SECTION
# ==========================================
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.header("📁 Data Upload")

option = st.radio(
    "Choose data source:",
    ["Upload CSV/Excel File", "Load Test Dataset"],
    horizontal=True
)

if option == "Upload CSV/Excel File":
    file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    if file:
        if file.name.endswith(".csv"):
            st.session_state.data = pd.read_csv(file)
        else:
            st.session_state.data = pd.read_excel(file)
        st.success("✓ Data loaded successfully")

else:
    rows = st.slider("Number of records", 100, 5000, 1000)
    if st.button("📊 Load Test Dataset", use_container_width=True):
        st.session_state.data = generate_sample_data(rows)
        st.success("✓ Test dataset loaded successfully")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# DATA PREVIEW
# ==========================================
if st.session_state.data is not None:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.header("📋 Data Preview")
    
    # Apply department filter to preview
    preview_data = st.session_state.data
    if st.session_state.selected_department != "All Departments":
        if 'department' in preview_data.columns:
            preview_data = preview_data[preview_data['department'] == st.session_state.selected_department]
            st.info(f"🏛️ Showing {len(preview_data)} transactions from {st.session_state.selected_department} department")
        else:
            st.warning("⚠️ Department column not found in data")
    
    st.dataframe(preview_data.head(50), use_container_width=True)
    
    # Data Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", len(preview_data))
    with col2:
        if 'amount' in preview_data.columns:
            st.metric("Avg Amount", f"${preview_data['amount'].mean():,.2f}")
    with col3:
        if 'department' in preview_data.columns:
            st.metric("Departments", preview_data['department'].nunique())
    with col4:
        if 'vendor' in preview_data.columns:
            st.metric("Unique Vendors", preview_data['vendor'].nunique())
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# QUICK ACTIONS
# ==========================================
if st.session_state.data is not None:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.header("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Run AI Risk Scan", use_container_width=True, type="primary"):
            st.info("Navigate to 'Anomaly Detection' page to run AI risk scan")
    
    with col2:
        if st.button("📊 View Dashboard", use_container_width=True):
            st.info("Navigate to 'Dashboard' page to view analytics")
    
    with col3:
        if st.button("⚠️ View Alerts", use_container_width=True):
            st.info("Navigate to 'Alerts' page to manage flagged transactions")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# FOOTER
# ==========================================
st.markdown("""
<div class="footer">
🛡️ AI Fraud Detection System · Hack4Delhi · Verilens Team<br>
Built with Streamlit · Explainable AI · Department-Based Risk Analysis
</div>
""", unsafe_allow_html=True)
