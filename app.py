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
st.markdown("""
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
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if 'data' not in st.session_state:
    st.session_state.data = None
if 'original_data' not in st.session_state:
    st.session_state.original_data = None
if 'anomalies' not in st.session_state:
    st.session_state.anomalies = None
if 'anomaly_count' not in st.session_state:
    st.session_state.anomaly_count = 0
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'data_source' not in st.session_state:
    st.session_state.data_source = None
if 'data_filename' not in st.session_state:
    st.session_state.data_filename = None
if 'detection_run' not in st.session_state:
    st.session_state.detection_run = False

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def generate_sample_data(n_samples=1000, anomaly_rate=10, seed=42):
    """Generate realistic sample transaction data with anomalies"""
    np.random.seed(seed)
    random.seed(seed)
    
    n_normal = int(n_samples * (1 - anomaly_rate/100))
    n_anomaly = n_samples - n_normal
    
    categories = ['Supplies', 'Services', 'Equipment', 'Travel', 'Consulting', 'Maintenance']
    departments = ['Finance', 'HR', 'IT', 'Operations', 'Marketing', 'Procurement']
    payment_methods = ['Check', 'Wire', 'ACH', 'Credit Card']
    regions = ['North', 'South', 'East', 'West', 'Central']
    
    base_date = datetime.now() - timedelta(days=365)
    
    # Normal transactions
    normal_data = {
        'transaction_id': [f'TXN{i:06d}' for i in range(n_normal)],
        'date': [(base_date + timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d') for _ in range(n_normal)],
        'amount': np.round(np.random.lognormal(mean=6, sigma=1, size=n_normal), 2),
        'category': np.random.choice(categories, n_normal),
        'department': np.random.choice(departments, n_normal),
        'vendor_id': [f'V{random.randint(1, 100):03d}' for _ in range(n_normal)],
        'num_items': (np.random.poisson(5, n_normal) + 1).astype(int),
        'processing_days': np.round(np.abs(np.random.normal(5, 1.5, n_normal)), 1),
        'is_weekend': np.random.choice([0, 1], n_normal, p=[0.85, 0.15]),
        'approval_level': np.random.choice([1, 2, 3], n_normal, p=[0.6, 0.3, 0.1]),
        'payment_method': np.random.choice(payment_methods, n_normal),
        'region': np.random.choice(regions, n_normal),
    }
    
    # Anomaly transactions
    anomaly_data = {
        'transaction_id': [f'TXN{i:06d}' for i in range(n_normal, n_samples)],
        'date': [(base_date + timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d') for _ in range(n_anomaly)],
        'amount': np.round(np.concatenate([
            np.random.lognormal(mean=10, sigma=1.5, size=n_anomaly//3),
            np.random.uniform(0.01, 5, size=n_anomaly//3),
            np.random.choice([50000, 100000, 75000], size=n_anomaly - 2*(n_anomaly//3))
        ]), 2),
        'category': np.random.choice(['Consulting', 'Misc'], n_anomaly),
        'department': np.random.choice(departments, n_anomaly),
        'vendor_id': [f'V{random.randint(900, 999):03d}' for _ in range(n_anomaly)],
        'num_items': np.random.choice([1, 100, 200], n_anomaly),
        'processing_days': np.round(np.random.choice([0.5, 20, 30], n_anomaly), 1),
        'is_weekend': np.random.choice([0, 1], n_anomaly, p=[0.3, 0.7]),
        'approval_level': np.random.choice([1, 3], n_anomaly),
        'payment_method': np.random.choice(['Wire', 'Cash'], n_anomaly),
        'region': np.random.choice(regions, n_anomaly),
    }
    
    normal_df = pd.DataFrame(normal_data)
    anomaly_df = pd.DataFrame(anomaly_data)
    df = pd.concat([normal_df, anomaly_df], ignore_index=True)
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    
    return df

def get_data_summary(df):
    """Get summary statistics"""
    if df is None:
        return None
    
    summary = {
        'total_records': len(df),
        'total_columns': len(df.columns),
        'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
        'missing_values': df.isnull().sum().sum(),
    }
    
    if 'amount' in df.columns:
        summary['total_amount'] = df['amount'].sum()
        summary['avg_amount'] = df['amount'].mean()
    
    return summary

# ==========================================
# HEADER
# ==========================================
st.markdown('<h1 class="main-header">🛡️ AI Fraud & Anomaly Detection System</h1>', unsafe_allow_html=True)
st.markdown("""
<p class="subtitle">
    Intelligent system for detecting fraudulent activities and anomalies in public sector data<br>
    <small>Powered by Machine Learning • Built for Government Transparency</small>
</p>
""", unsafe_allow_html=True)

# ==========================================
# FEATURE CARDS
# ==========================================
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

# ==========================================
# DATA UPLOAD SECTION
# ==========================================
st.header("📁 Data Upload")

upload_option = st.radio(
    "Choose data source:",
    ["📊 Upload CSV/Excel File", "🔄 Generate Sample Data"],
    horizontal=True
)

# ==========================================
# CSV/EXCEL UPLOAD
# ==========================================
if upload_option == "📊 Upload CSV/Excel File":
    st.markdown("""
    <div class="upload-section">
        <h4>📊 CSV / Excel Data Upload</h4>
        <p>Upload transaction data in CSV or Excel format</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Supported formats: CSV, XLSX, XLS"
    )
    
    if uploaded_file is not None:
        st.markdown(f"**📄 File:** {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        
        # CSV options
        with st.expander("⚙️ Import Options"):
            col1, col2 = st.columns(2)
            with col1:
                delimiter = st.selectbox("Delimiter (for CSV)", [",", ";", "\t", "|"])
            with col2:
                encoding = st.selectbox("Encoding", ["utf-8", "latin-1", "cp1252"])
        
        if st.button("📥 Load Data", type="primary", use_container_width=True):
            with st.spinner("Loading data..."):
                try:
                    if uploaded_file.name.endswith('.csv'):
                        try:
                            df = pd.read_csv(uploaded_file, delimiter=delimiter, encoding=encoding)
                        except:
                            uploaded_file.seek(0)
                            df = pd.read_csv(uploaded_file, delimiter=delimiter, encoding='latin-1')
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    st.session_state.data = df
                    st.session_state.original_data = df.copy()
                    st.session_state.data_source = "CSV" if uploaded_file.name.endswith('.csv') else "Excel"
                    st.session_state.data_filename = uploaded_file.name
                    st.session_state.anomaly_count = 0
                    st.session_state.alerts = []
                    st.session_state.detection_run = False
                    
                    st.success(f"✅ Loaded **{len(df)}** rows × **{len(df.columns)}** columns")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ==========================================
# SAMPLE DATA GENERATION
# ==========================================
elif upload_option == "🔄 Generate Sample Data":
    st.markdown("""
    <div class="upload-section">
        <h4>🔄 Generate Sample Data</h4>
        <p>Create realistic sample transaction data with embedded anomalies for testing</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        n_samples = st.slider("Number of transactions", 100, 5000, 1000, 100)
    with col2:
        anomaly_rate = st.slider("Anomaly rate (%)", 5, 30, 10)
    with col3:
        random_seed = st.number_input("Random seed", 1, 9999, 42)
    
    # Data schema preview
    with st.expander("📋 Data Schema Preview"):
        st.markdown("""
| Column | Type | Description |
|--------|------|-------------|
| transaction_id | String | Unique ID (TXN000001) |
| date | Date | Transaction date |
| amount | Float | Transaction amount |
| category | String | Category |
| department | String | Department |
| vendor_id | String | Vendor ID |
| num_items | Integer | Number of items |
| processing_days | Float | Days to process |
| is_weekend | Integer | 1=weekend, 0=weekday |
| approval_level | Integer | Level 1-3 |
| payment_method | String | Payment method |
| region | String | Region |

**Anomaly patterns:** High/low amounts, weekend processing, unknown vendors, rush approvals
        """)
    
    if st.button("🔄 Generate Sample Data", type="primary", use_container_width=True):
        with st.spinner("Generating data..."):
            df = generate_sample_data(n_samples, anomaly_rate, random_seed)
            st.session_state.data = df
            st.session_state.original_data = df.copy()
            st.session_state.data_source = "Sample"
            st.session_state.data_filename = f"sample_{n_samples}_{anomaly_rate}pct.csv"
            st.session_state.anomaly_count = 0
            st.session_state.alerts = []
            st.session_state.detection_run = False
            
            st.success(f"✅ Generated **{len(df)}** transactions with ~**{anomaly_rate}%** anomalies")
            st.balloons()

# ==========================================
# DATA PREVIEW
# ==========================================
if st.session_state.data is not None:
    st.markdown("---")
    st.header("📋 Data Preview")
    
    df = st.session_state.data
    summary = get_data_summary(df)
    
    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📊 Records", f"{summary['total_records']:,}")
    with col2:
        st.metric("📋 Columns", summary['total_columns'])
    with col3:
        st.metric("❓ Missing", summary['missing_values'])
    with col4:
        st.metric("📁 Source", st.session_state.data_source)
    with col5:
        if st.session_state.detection_run:
            st.metric("🔍 Anomalies", st.session_state.anomaly_count)
        else:
            st.metric("🔍 Status", "Pending")
    
    # Amount stats
    if 'amount' in df.columns:
        st.markdown("#### 💰 Amount Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", f"₹{summary['total_amount']:,.0f}")
        with col2:
            st.metric("Average", f"₹{summary['avg_amount']:,.0f}")
        with col3:
            st.metric("Max", f"₹{df['amount'].max():,.0f}")
        with col4:
            st.metric("Min", f"₹{df['amount'].min():,.2f}")
    
    # Column info
    with st.expander("📋 Column Information"):
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes.astype(str),
            'Non-Null': df.notna().sum().values,
            'Unique': df.nunique().values
        })
        st.dataframe(col_info, use_container_width=True, hide_index=True)
    
    # Data preview table
    st.markdown("#### 📊 Data Table")
    col1, col2 = st.columns([1, 3])
    with col1:
        n_rows = st.selectbox("Show rows:", [10, 25, 50, 100], index=0)
    
    display_df = df.head(n_rows)
    st.dataframe(display_df, use_container_width=True, height=400)
    
    # Download
    st.download_button(
        "📥 Download CSV",
        data=df.to_csv(index=False),
        file_name=f"data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# ==========================================
# NAVIGATION HINT
# ==========================================
st.markdown("---")

if st.session_state.data is not None:
    st.markdown("""
    <div class="nav-hint">
        <strong>✅ Data loaded successfully!</strong><br>
        👈 Use the <strong>sidebar</strong> to navigate to:<br>
        • <strong>📊 Dashboard</strong> - View metrics and charts<br>
        • <strong>🔍 Anomaly Detection</strong> - Run AI detection<br>
        • <strong>📈 Analytics</strong> - Deep analysis<br>
        • <strong>⚠️ Alerts</strong> - Manage alerts<br>
        • <strong>📋 Reports</strong> - Export reports
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="nav-hint">
        <strong>📁 No data loaded yet</strong><br>
        Upload a CSV/Excel file or generate sample data to begin.
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# QUICK START GUIDE
# ==========================================
with st.expander("📖 Quick Start Guide"):
    st.markdown("""
### How to Use

**Step 1: Load Data**
- Upload CSV/Excel file, OR
- Generate sample data for testing

**Step 2: Review Data**
- Check data preview
- Verify columns and types

**Step 3: Run Detection**
- Go to 🔍 Anomaly Detection
- Select features and algorithm
- Click Run Detection

**Step 4: Review Results**
- Check 📊 Dashboard for overview
- Review ⚠️ Alerts for flagged items

**Step 5: Export**
- Go to 📋 Reports
- Download CSV or Excel report
    """)

# ==========================================
# FOOTER
# ==========================================
st.markdown("""
<div class="footer">
    🛡️ <strong>AI Fraud Detection System</strong> v2.0<br>
    Built with Streamlit • Powered by ML<br>
    <small>© 2024 - For Government Transparency</small>
</div>
""", unsafe_allow_html=True)
