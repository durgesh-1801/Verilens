import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AI Fraud & Anomaly Detection",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# GLOBAL STYLES
# -------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: Inter, system-ui, sans-serif;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.section-title {
    font-size: 1.4rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
}

.subtle {
    color: #6b7280;
    font-size: 0.9rem;
}

.panel {
    background: #fafafa;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 1.25rem;
}

.upload-box {
    border: 2px dashed #c7d2fe;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    background: #f8fafc;
}

.footer {
    text-align: center;
    font-size: 0.8rem;
    color: #9ca3af;
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
for key in [
    "data", "original_data", "anomaly_count",
    "data_source", "data_filename", "detection_run"
]:
    if key not in st.session_state:
        st.session_state[key] = None

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.markdown("### 🛡️ AI Fraud Detection")
    st.markdown("<div class='subtle'>Public Sector Anomaly Monitoring</div>", unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navigation",
        ["Data Ingestion", "Preview", "Dashboard", "Detection", "Alerts", "Reports"],
        label_visibility="collapsed"
    )

    st.divider()
    if st.session_state.data is not None:
        st.success("Data Loaded")
        st.caption(f"{st.session_state.data_filename}")
    else:
        st.warning("No data loaded")

# -------------------------------------------------
# DATA GENERATION
# -------------------------------------------------
def generate_sample_data(n=1000, anomaly_rate=10, seed=42):
    np.random.seed(seed)
    base_date = datetime.now() - timedelta(days=365)

    df = pd.DataFrame({
        "transaction_id": [f"TXN{i:06d}" for i in range(n)],
        "date": [
            (base_date + timedelta(days=random.randint(0, 365))).date()
            for _ in range(n)
        ],
        "amount": np.round(np.random.lognormal(6, 1, n), 2),
        "department": np.random.choice(
            ["Finance", "IT", "HR", "Operations"], n
        ),
        "payment_method": np.random.choice(
            ["Wire", "ACH", "Card"], n
        )
    })

    anomaly_idx = np.random.choice(
        df.index, int(n * anomaly_rate / 100), replace=False
    )
    df.loc[anomaly_idx, "amount"] *= 20

    return df

# -------------------------------------------------
# PAGE: DATA INGESTION
# -------------------------------------------------
if page == "Data Ingestion":
    st.markdown("<div class='section-title'>Data Ingestion</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("**Upload Dataset**")
        file = st.file_uploader("CSV or Excel", type=["csv", "xlsx"])
        if file and st.button("Load File", use_container_width=True):
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            st.session_state.data = df
            st.session_state.original_data = df.copy()
            st.session_state.data_source = "Upload"
            st.session_state.data_filename = file.name
            st.success("File loaded successfully")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("**Generate Sample Data**")
        n = st.slider("Transactions", 500, 5000, 1000, 500)
        a = st.slider("Anomaly Rate (%)", 5, 30, 10)
        if st.button("Generate", use_container_width=True):
            df = generate_sample_data(n, a)
            st.session_state.data = df
            st.session_state.original_data = df.copy()
            st.session_state.data_source = "Sample"
            st.session_state.data_filename = "synthetic_data.csv"
            st.success("Sample data generated")
        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# PAGE: PREVIEW
# -------------------------------------------------
if page == "Preview" and st.session_state.data is not None:
    df = st.session_state.data

    st.markdown("<div class='section-title'>Data Preview</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", f"{len(df):,}")
    col2.metric("Columns", len(df.columns))
    col3.metric("Missing Values", int(df.isna().sum().sum()))

    st.divider()

    search = st.text_input("Search (any column)")
    view_df = df.copy()

    if search:
        view_df = view_df[
            view_df.astype(str).apply(
                lambda r: r.str.contains(search, case=False).any(), axis=1
            )
        ]

    rows = st.selectbox("Rows to display", [10, 25, 50, 100], 25)
    st.dataframe(view_df.head(rows), use_container_width=True, height=420)

# -------------------------------------------------
# EMPTY STATES FOR FUTURE MODULES
# -------------------------------------------------
for future_page in ["Dashboard", "Detection", "Alerts", "Reports"]:
    if page == future_page:
        st.markdown(f"<div class='section-title'>{future_page}</div>", unsafe_allow_html=True)
        st.info("Module connected. Logic pending.")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("""
<div class="footer">
AI Fraud & Anomaly Detection System • Streamlit Interface<br>
Built for auditability, clarity, and scale
</div>
""", unsafe_allow_html=True)
