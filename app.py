import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="AI Fraud Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin: 0.5rem;
}
.metric-card h3 {
    font-size: 2rem;
    margin: 0;
}
.metric-card p {
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'anomalies' not in st.session_state:
    st.session_state.anomalies = None
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'anomaly_count' not in st.session_state:
    st.session_state.anomaly_count = 0

# Header
st.markdown('<h1 class="main-header">🛡️ AI Fraud & Anomaly Detection System</h1>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <p style="font-size: 1.2rem; color: #666;">
        Intelligent system for detecting fraudulent activities and anomalies in public sector data
    </p>
</div>
""", unsafe_allow_html=True)

# Feature Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>🔍</h3>
        <p>Multi-Algorithm<br>Detection</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>📊</h3>
        <p>Real-time<br>Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3>⚠️</h3>
        <p>Smart<br>Alerts</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <h3>📋</h3>
        <p>Auto<br>Reports</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Data Upload Section
st.header("📁 Data Upload")

upload_option = st.radio(
    "Choose data source:",
    ["Upload CSV File", "Use Sample Data"],
    horizontal=True
)

if upload_option == "Upload CSV File":
    uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])
    if uploaded_file:
        st.session_state.data = pd.read_csv(uploaded_file)
        st.success(f"✅ Data loaded successfully! Shape: {st.session_state.data.shape}")

elif upload_option == "Use Sample Data":
    if st.button("🔄 Generate Sample Data", type="primary"):
        # Generate sample data
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'transaction_id': [f'TXN{i:06d}' for i in range(n_samples)],
            'amount': np.concatenate([
                np.random.lognormal(mean=6, sigma=1, size=int(n_samples*0.9)),
                np.random.lognormal(mean=10, sigma=1.5, size=int(n_samples*0.1))
            ]),
            'category': np.random.choice(['Supplies', 'Services', 'Equipment', 'Travel', 'Consulting'], n_samples),
            'department': np.random.choice(['Finance', 'HR', 'IT', 'Operations', 'Marketing'], n_samples),
            'vendor_id': [f'V{np.random.randint(1, 100):03d}' for _ in range(n_samples)],
            'num_items': np.random.poisson(5, n_samples) + 1,
            'processing_days': np.concatenate([
                np.random.normal(5, 1, size=int(n_samples*0.9)),
                np.random.choice([0.5, 15, 20], size=int(n_samples*0.1))
            ]),
            'is_weekend': np.random.choice([0, 1], n_samples, p=[0.85, 0.15]),
            'approval_level': np.random.choice([1, 2, 3], n_samples, p=[0.6, 0.3, 0.1]),
        }
        
        st.session_state.data = pd.DataFrame(data)
        st.success("✅ Sample data generated successfully!")

# Display data preview
if st.session_state.data is not None:
    st.subheader("📋 Data Preview")
    st.dataframe(st.session_state.data.head(10), use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", f"{len(st.session_state.data):,}")
    with col2:
        st.metric("Features", len(st.session_state.data.columns))
    with col3:
        st.metric("Missing Values", st.session_state.data.isnull().sum().sum())

st.markdown("---")
st.info("👈 Use the sidebar to navigate to: **Dashboard, Anomaly Detection, Analytics, Alerts, and Reports**")
