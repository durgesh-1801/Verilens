"""
AI Fraud & Anomaly Detection System
Enhanced Professional UI/UX Version - Final
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
# ENHANCED CUSTOM CSS
# ==========================================
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main Container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Animated Header */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.8s ease-out;
        letter-spacing: -1px;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2.5rem;
        animation: fadeIn 1s ease-out;
        line-height: 1.6;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Feature Cards - Enhanced */
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1.5rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.25);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.4);
    }
    
    .feature-card:hover::before {
        opacity: 1;
    }
    
    .feature-card h3 {
        font-size: 3rem;
        margin: 0 0 0.5rem 0;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    
    .feature-card p {
        margin: 0;
        opacity: 0.95;
        font-weight: 500;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    
    /* Upload Section - Modern Design */
    .upload-section {
        border: 3px dashed #667eea;
        border-radius: 20px;
        padding: 35px;
        text-align: center;
        margin: 20px 0;
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .upload-section:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, #f0f4ff 0%, #e8f0ff 100%);
        transform: scale(1.01);
    }
    
    .upload-section h4 {
        color: #667eea;
        margin-bottom: 15px;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .upload-section p {
        color: #64748b;
        font-size: 1rem;
        margin: 0;
    }
    
    /* Success Box */
    .success-box {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 20px 25px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        animation: slideInRight 0.5s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 20px 25px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    /* Warning Box */
    .warning-box {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 20px 25px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
    }
    
    /* Navigation Hint - Enhanced */
    .nav-hint {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
        border-radius: 16px;
        padding: 25px 30px;
        margin-top: 30px;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .nav-hint:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
    }
    
    .nav-hint strong {
        color: #667eea;
        font-size: 1.1rem;
    }
    
    /* Metric Cards - Enhanced with Gradient Background */
    .metric-container {
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .metric-container:hover {
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
        transform: translateY(-4px);
        background: linear-gradient(135deg, #f0f4ff 0%, #e8f0ff 100%);
        border-color: rgba(102, 126, 234, 0.4);
    }
    
    /* Data Table Styling */
    .dataframe {
        font-size: 0.9rem;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Button Enhancements */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.9rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(16, 185, 129, 0.3);
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
        border-radius: 10px;
        font-weight: 600;
        padding: 15px;
        border: 1px solid #e2e8f0;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8f0ff 100%);
        border-color: #667eea;
    }
    
    /* Selectbox & Slider Styling */
    .stSelectbox > div > div {
        border-radius: 8px;
        border-color: #cbd5e1;
    }
    
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Footer - Enhanced */
    .footer {
        text-align: center;
        color: #94a3b8;
        padding: 30px 20px;
        font-size: 0.9rem;
        border-top: 2px solid #e2e8f0;
        margin-top: 50px;
        background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
        border-radius: 16px 16px 0 0;
    }
    
    .footer strong {
        color: #667eea;
        font-size: 1.1rem;
    }
    
    /* Badge Styling */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0 4px;
    }
    
    .badge-success {
        background: #10b981;
        color: white;
    }
    
    .badge-info {
        background: #3b82f6;
        color: white;
    }
    
    .badge-warning {
        background: #f59e0b;
        color: white;
    }
    
    /* Progress Indicator */
    .progress-bar {
        width: 100%;
        height: 4px;
        background: #e2e8f0;
        border-radius: 2px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        animation: progress 2s ease-out;
    }
    
    @keyframes progress {
        from { width: 0%; }
        to { width: 100%; }
    }
    
    /* File Upload Area */
    .uploadedFile {
        border-radius: 10px;
        background: #f8f9ff;
        border: 1px solid #cbd5e1;
    }
    
    /* Radio Button Styling */
    .stRadio > div {
        background: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    
    /* Section Headers */
    h1, h2, h3, h4 {
        color: #1e293b;
        font-weight: 700;
    }
    
    /* Divider Enhancement */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
    }
    
    /* Tooltip Styling */
    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted #667eea;
        cursor: help;
    }
    
    /* Loading Animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Card Grid */
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .feature-card {
            padding: 1.5rem 1rem;
        }
        
        .upload-section {
            padding: 25px;
        }
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
# HEADER SECTION
# ==========================================
st.markdown('<h1 class="main-header">🛡️ AI Fraud & Anomaly Detection System</h1>', unsafe_allow_html=True)
st.markdown("""
<p class="subtitle">
    <strong>Intelligent system for detecting fraudulent activities and anomalies in public sector data</strong><br>
    <span class="badge badge-info">Machine Learning Powered</span>
    <span class="badge badge-success">Real-time Detection</span>
    <span class="badge badge-warning">Government Grade</span>
</p>
""", unsafe_allow_html=True)

# ==========================================
# FEATURE CARDS
# ==========================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>🔍</h3>
        <p><strong>Multi-Algorithm</strong><br>Detection Engine</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>📊</h3>
        <p><strong>Real-time</strong><br>Analytics Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>⚠️</h3>
        <p><strong>Smart Alert</strong><br>System</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <h3>📋</h3>
        <p><strong>Automated</strong><br>Report Generation</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# DATA UPLOAD SECTION
# ==========================================
st.header("📁 Data Input & Configuration")

upload_option = st.radio(
    "Select your data source:",
    ["📊 Upload CSV/Excel File", "🔄 Generate Sample Dataset"],
    horizontal=True,
    help="Choose to upload your own data or generate sample data for testing"
)

# ==========================================
# CSV/EXCEL UPLOAD
# ==========================================
if upload_option == "📊 Upload CSV/Excel File":
    st.markdown("""
    <div class="upload-section">
        <h4>📊 Import Your Transaction Data</h4>
        <p>Upload transaction data in CSV or Excel format for fraud analysis</p>
        <div class="progress-bar"><div class="progress-fill" style="width: 0%"></div></div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls'],
        help="Supported formats: CSV, XLSX, XLS (Max size: 200MB)",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        # File info display
        file_size_kb = uploaded_file.size / 1024
        file_size_display = f"{file_size_kb:.1f} KB" if file_size_kb < 1024 else f"{file_size_kb/1024:.1f} MB"
        
        st.markdown(f"""
        <div class="info-box">
            📄 <strong>File Selected:</strong> {uploaded_file.name}<br>
            📦 <strong>Size:</strong> {file_size_display}<br>
            🔖 <strong>Type:</strong> {uploaded_file.type}
        </div>
        """, unsafe_allow_html=True)
        
        # Import options in expandable section
        with st.expander("⚙️ Advanced Import Options", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                delimiter = st.selectbox(
                    "CSV Delimiter",
                    [",", ";", "\t", "|"],
                    help="Select the delimiter used in your CSV file"
                )
            with col2:
                encoding = st.selectbox(
                    "File Encoding",
                    ["utf-8", "latin-1", "cp1252"],
                    help="Select the character encoding of your file"
                )
        
        # Load button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📥 Load Data", type="primary", use_container_width=True):
                with st.spinner("🔄 Processing your data..."):
                    try:
                        # Load data based on file type
                        if uploaded_file.name.endswith('.csv'):
                            try:
                                df = pd.read_csv(uploaded_file, delimiter=delimiter, encoding=encoding)
                            except:
                                uploaded_file.seek(0)
                                df = pd.read_csv(uploaded_file, delimiter=delimiter, encoding='latin-1')
                        else:
                            df = pd.read_excel(uploaded_file)
                        
                        # Update session state
                        st.session_state.data = df
                        st.session_state.original_data = df.copy()
                        st.session_state.data_source = "CSV" if uploaded_file.name.endswith('.csv') else "Excel"
                        st.session_state.data_filename = uploaded_file.name
                        st.session_state.anomaly_count = 0
                        st.session_state.alerts = []
                        st.session_state.detection_run = False
                        
                        # Success message
                        st.markdown(f"""
                        <div class="success-box">
                            ✅ <strong>Data Loaded Successfully!</strong><br>
                            📊 Imported <strong>{len(df):,}</strong> rows × <strong>{len(df.columns)}</strong> columns<br>
                            🎯 Ready for analysis
                        </div>
                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.markdown(f"""
                        <div class="warning-box">
                            ❌ <strong>Error Loading File</strong><br>
                            {str(e)}
                        </div>
                        """, unsafe_allow_html=True)

# ==========================================
# SAMPLE DATA GENERATION
# ==========================================
elif upload_option == "🔄 Generate Sample Dataset":
    st.markdown("""
    <div class="upload-section">
        <h4>🔄 Generate Synthetic Transaction Data</h4>
        <p>Create realistic sample transaction data with embedded anomalies for testing and demonstration</p>
        <div class="progress-bar"><div class="progress-fill" style="width: 0%"></div></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        n_samples = st.slider(
            "📊 Number of Transactions",
            min_value=100,
            max_value=5000,
            value=1000,
            step=100,
            help="Total number of transactions to generate"
        )
    
    with col2:
        anomaly_rate = st.slider(
            "⚠️ Anomaly Rate (%)",
            min_value=5,
            max_value=30,
            value=10,
            help="Percentage of transactions that will be anomalous"
        )
    
    with col3:
        random_seed = st.number_input(
            "🎲 Random Seed",
            min_value=1,
            max_value=9999,
            value=42,
            help="Seed for reproducible results"
        )
    
    # Preview expected data
    with st.expander("📋 Data Schema & Anomaly Patterns", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Data Schema**")
            schema_data = {
                'Column': ['transaction_id', 'date', 'amount', 'category', 'department', 'vendor_id', 
                          'num_items', 'processing_days', 'is_weekend', 'approval_level', 'payment_method', 'region'],
                'Type': ['String', 'Date', 'Float', 'String', 'String', 'String', 
                        'Integer', 'Float', 'Integer', 'Integer', 'String', 'String'],
                'Description': ['Unique ID', 'Transaction date', 'Amount', 'Category', 'Department', 'Vendor ID',
                              'Item count', 'Processing time', 'Weekend flag', 'Approval level', 'Payment type', 'Region']
            }
            st.dataframe(pd.DataFrame(schema_data), use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("**⚠️ Anomaly Patterns**")
            st.markdown("""
            - 💰 **Unusual Amounts**: Extremely high or suspiciously low
            - 📅 **Weekend Processing**: Non-standard timing
            - 🏢 **Unknown Vendors**: Vendor IDs 900-999
            - ⚡ **Rush Approvals**: Very fast processing
            - 🔢 **Bulk Items**: Unusually high item counts
            - 💳 **Payment Methods**: Wire transfers, cash
            """)
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Generate Sample Data", type="primary", use_container_width=True):
            with st.spinner("🔄 Generating synthetic transaction data..."):
                # Generate data
                df = generate_sample_data(n_samples, anomaly_rate, random_seed)
                
                # Update session state
                st.session_state.data = df
                st.session_state.original_data = df.copy()
                st.session_state.data_source = "Sample"
                st.session_state.data_filename = f"sample_{n_samples}_{anomaly_rate}pct.csv"
                st.session_state.anomaly_count = 0
                st.session_state.alerts = []
                st.session_state.detection_run = False
                
                # Success message
                expected_anomalies = int(n_samples * anomaly_rate / 100)
                st.markdown(f"""
                <div class="success-box">
                    ✅ <strong>Sample Data Generated Successfully!</strong><br>
                    📊 Created <strong>{len(df):,}</strong> transactions<br>
                    ⚠️ Approximately <strong>{expected_anomalies}</strong> anomalies embedded (~{anomaly_rate}%)<br>
                    🎲 Random seed: {random_seed}
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# DATA PREVIEW SECTION
# ==========================================
if st.session_state.data is not None:
    st.markdown("---")
    st.header("📋 Data Overview & Statistics")
    
    df = st.session_state.data
    summary = get_data_summary(df)
    
    # Top-level metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: #667eea; margin: 0;">📊</h3>
            <h2 style="margin: 10px 0;">{:,}</h2>
            <p style="color: #64748b; margin: 0;">Total Records</p>
        </div>
        """.format(summary['total_records']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: #10b981; margin: 0;">📋</h3>
            <h2 style="margin: 10px 0;">{}</h2>
            <p style="color: #64748b; margin: 0;">Columns</p>
        </div>
        """.format(summary['total_columns']), unsafe_allow_html=True)
    
    with col3:
        missing_color = "#ef4444" if summary['missing_values'] > 0 else "#10b981"
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: {}; margin: 0;">❓</h3>
            <h2 style="margin: 10px 0;">{}</h2>
            <p style="color: #64748b; margin: 0;">Missing Values</p>
        </div>
        """.format(missing_color, summary['missing_values']), unsafe_allow_html=True)
    
    with col4:
        source_icon = "📊" if st.session_state.data_source == "CSV" else "📈" if st.session_state.data_source == "Excel" else "🔄"
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: #3b82f6; margin: 0;">{}</h3>
            <h2 style="margin: 10px 0; font-size: 1.3rem;">{}</h2>
            <p style="color: #64748b; margin: 0;">Data Source</p>
        </div>
        """.format(source_icon, st.session_state.data_source), unsafe_allow_html=True)
    
    with col5:
        if st.session_state.detection_run:
            anomaly_color = "#ef4444" if st.session_state.anomaly_count > 0 else "#10b981"
            st.markdown("""
            <div class="metric-container">
                <h3 style="color: {}; margin: 0;">🔍</h3>
                <h2 style="margin: 10px 0;">{}</h2>
                <p style="color: #64748b; margin: 0;">Anomalies Found</p>
            </div>
            """.format(anomaly_color, st.session_state.anomaly_count), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-container">
                <h3 style="color: #f59e0b; margin: 0;">🔍</h3>
                <h2 style="margin: 10px 0; font-size: 1.3rem;">Pending</h2>
                <p style="color: #64748b; margin: 0;">Detection Status</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Amount statistics
    if 'amount' in df.columns:
        st.markdown("#### 💰 Financial Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Amount", f"₹{summary['total_amount']:,.0f}", help="Sum of all transactions")
        with col2:
            st.metric("Average Amount", f"₹{summary['avg_amount']:,.0f}", help="Mean transaction value")
        with col3:
            st.metric("Maximum", f"₹{df['amount'].max():,.0f}", help="Largest transaction")
        with col4:
            st.metric("Minimum", f"₹{df['amount'].min():,.2f}", help="Smallest transaction")
    
    # Column information
    with st.expander("📋 Detailed Column Information", expanded=False):
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes.astype(str),
            'Non-Null Count': df.notna().sum().values,
            'Unique Values': df.nunique().values,
            'Memory Usage': [f"{df[col].memory_usage(deep=True) / 1024:.1f} KB" for col in df.columns]
        })
        st.dataframe(col_info, use_container_width=True, hide_index=True, height=300)
    
    # Data preview
    st.markdown("#### 📊 Data Preview")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        n_rows = st.selectbox("Rows to display:", [10, 25, 50, 100, 250], index=0)
    with col2:
        st.markdown(f"<p style='text-align: center; color: #64748b; padding-top: 8px;'>Showing {min(n_rows, len(df))} of {len(df):,} records</p>", unsafe_allow_html=True)
    with col3:
        # Download button
        csv_data = df.to_csv(index=False)
        st.download_button(
            "📥 Download Full Dataset",
            data=csv_data,
            file_name=f"fraud_detection_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Display data table
    display_df = df.head(n_rows)
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        hide_index=True
    )

# ==========================================
# NAVIGATION HINT
# ==========================================
st.markdown("---")

if st.session_state.data is not None:
    st.markdown("""
    <div class="nav-hint">
        <strong>✅ Data successfully loaded and ready for analysis!</strong><br><br>
        <strong>Next Steps:</strong> Use the sidebar navigation (←) to proceed:<br><br>
        🔹 <strong>📊 Dashboard</strong> → View comprehensive metrics and visualizations<br>
        🔹 <strong>🔍 Anomaly Detection</strong> → Run AI-powered fraud detection algorithms<br>
        🔹 <strong>📈 Analytics</strong> → Perform deep dive analysis and insights<br>
        🔹 <strong>⚠️ Alert Management</strong> → Configure and review alert rules<br>
        🔹 <strong>📋 Report Generation</strong> → Export professional reports<br>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="nav-hint">
        <strong>🚀 Getting Started</strong><br><br>
        No data loaded yet. Please:<br>
        🔹 Upload your CSV/Excel file containing transaction data, or<br>
        🔹 Generate sample data to explore the system's capabilities<br><br>
        <em>Once data is loaded, you'll have access to all analysis features.</em>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# QUICK START GUIDE
# ==========================================
with st.expander("📖 Quick Start Guide & Documentation", expanded=False):
    tab1, tab2, tab3 = st.tabs(["🚀 Getting Started", "📚 User Guide", "❓ FAQs"])
    
    with tab1:
        st.markdown("""
        ### Quick Start in 5 Steps
        
        **Step 1: Load Your Data** 📁
        - Upload a CSV or Excel file with transaction data
        - OR generate sample data for testing purposes
        
        **Step 2: Review Your Data** 👀
        - Examine the data preview table
        - Check column types and statistics
        - Verify data quality metrics
        
        **Step 3: Configure Detection** ⚙️
        - Navigate to **🔍 Anomaly Detection** in the sidebar
        - Select features for analysis
        - Choose detection algorithm (Isolation Forest, LOF, etc.)
        - Adjust sensitivity parameters
        
        **Step 4: Run Detection** 🔍
        - Click "Run Detection" button
        - Review detected anomalies
        - Analyze anomaly scores and patterns
        
        **Step 5: Export Results** 📊
        - View results in the **📊 Dashboard**
        - Check alerts in **⚠️ Alert Management**
        - Generate reports in **📋 Report Generation**
        - Download results as CSV or Excel
        """)
    
    with tab2:
        st.markdown("""
        ### Complete User Guide
        
        **Data Requirements**
        - Supported formats: CSV, Excel (XLSX, XLS)
        - Recommended columns: transaction_id, date, amount, category
        - Numeric columns for anomaly detection
        - Date columns for temporal analysis
        
        **Detection Algorithms**
        - **Isolation Forest**: Best for general anomaly detection
        - **Local Outlier Factor (LOF)**: Identifies local density anomalies
        - **One-Class SVM**: Effective for high-dimensional data
        - **Statistical Methods**: Z-score, IQR-based detection
        
        **Best Practices**
        - Ensure data quality before analysis
        - Start with sample data to understand the system
        - Adjust sensitivity based on your use case
        - Review and validate detected anomalies
        - Export and archive results regularly
        
        **Tips for Better Results**
        - Include multiple relevant features
        - Remove duplicate records
        - Handle missing values appropriately
        - Use domain knowledge to interpret results
        """)
    
    with tab3:
        st.markdown("""
        ### Frequently Asked Questions
        
        **Q: What file formats are supported?**  
        A: CSV, XLSX, and XLS files are supported. CSV files can use various delimiters.
        
        **Q: How many records can I analyze?**  
        A: The system can handle datasets up to 1 million records efficiently.
        
        **Q: What is the anomaly rate?**  
        A: The anomaly rate is the percentage of transactions flagged as suspicious.
        
        **Q: Can I customize detection parameters?**  
        A: Yes, you can adjust sensitivity, contamination rate, and feature selection.
        
        **Q: How do I interpret anomaly scores?**  
        A: Higher scores indicate greater deviation from normal patterns.
        
        **Q: Can I export the results?**  
        A: Yes, results can be exported as CSV or Excel files with detailed reports.
        
        **Q: Is my data secure?**  
        A: All data processing is done locally in your session and not stored permanently.
        """)

# ==========================================
# FOOTER
# ==========================================
st.markdown("""
<div class="footer">
    🛡️ <strong>AI Fraud & Anomaly Detection System</strong> v2.0<br>
    Powered by Advanced Machine Learning Algorithms<br>
    <small>Built with ❤️ using Streamlit • Designed for Government Transparency & Public Sector Integrity</small><br>
    <small style="color: #94a3b8;">© 2024 - All Rights Reserved</small>
</div>
""", unsafe_allow_html=True)
