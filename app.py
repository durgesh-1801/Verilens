"""
AI Fraud & Anomaly Detection System
Professional UI Version with Advanced Animations
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import time

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
# PROFESSIONAL CUSTOM CSS
# ==========================================
st.markdown("""
<style>
    /* Import Professional Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main Container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Professional Color Scheme */
    :root {
        --primary: #2563eb;
        --primary-dark: #1e40af;
        --secondary: #7c3aed;
        --success: #059669;
        --warning: #d97706;
        --danger: #dc2626;
        --dark: #1e293b;
        --light: #f1f5f9;
        --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --gradient-3: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --gradient-4: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.12);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.16);
    }
    
    /* Animated Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        background-attachment: fixed;
    }
    
    /* Success Animation */
    @keyframes successPulse {
        0% {
            transform: scale(1);
            opacity: 1;
        }
        50% {
            transform: scale(1.05);
            opacity: 0.8;
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }
    
    @keyframes checkmark {
        0% {
            stroke-dashoffset: 100;
        }
        100% {
            stroke-dashoffset: 0;
        }
    }
    
    /* Professional Header */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1e40af 0%, #7c3aed 50%, #db2777 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInScale 0.8s ease-out;
        letter-spacing: -2px;
        text-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #475569;
        font-size: 1.15rem;
        margin-bottom: 3rem;
        animation: slideInUp 1s ease-out;
        line-height: 1.8;
        font-weight: 400;
    }
    
    /* Professional Feature Cards */
    .feature-card {
        background: white;
        padding: 2.5rem 2rem;
        border-radius: 20px;
        color: #1e293b;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: var(--shadow-md);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
        border: 2px solid transparent;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-12px) scale(1.03);
        box-shadow: var(--shadow-lg);
        border-color: #667eea;
    }
    
    .feature-card h3 {
        font-size: 3.5rem;
        margin: 0 0 1rem 0;
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    
    .feature-card p {
        margin: 0;
        color: #64748b;
        font-weight: 600;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .feature-card strong {
        color: #1e293b;
        display: block;
        font-size: 1.1rem;
    }
    
    /* Professional Upload Section */
    .upload-section {
        background: white;
        border: 3px dashed #cbd5e1;
        border-radius: 24px;
        padding: 40px;
        text-align: center;
        margin: 25px 0;
        transition: all 0.4s ease;
        position: relative;
        box-shadow: var(--shadow-sm);
    }
    
    .upload-section:hover {
        border-color: #667eea;
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
        transform: translateY(-4px);
        box-shadow: var(--shadow-md);
    }
    
    .upload-section h4 {
        color: #1e40af;
        margin-bottom: 15px;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .upload-section p {
        color: #64748b;
        font-size: 1.05rem;
        margin: 0;
        font-weight: 400;
    }
    
    /* Professional Success Box */
    .success-box {
        background: white;
        border-left: 6px solid #059669;
        color: #1e293b;
        padding: 25px 30px;
        border-radius: 16px;
        margin: 20px 0;
        box-shadow: var(--shadow-md);
        animation: slideInUp 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .success-box::before {
        content: '✓';
        position: absolute;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 4rem;
        color: #059669;
        opacity: 0.1;
        font-weight: bold;
    }
    
    .success-box strong {
        color: #059669;
        font-size: 1.2rem;
    }
    
    /* Professional Info Box */
    .info-box {
        background: white;
        border-left: 6px solid #2563eb;
        color: #1e293b;
        padding: 25px 30px;
        border-radius: 16px;
        margin: 20px 0;
        box-shadow: var(--shadow-md);
        animation: slideInUp 0.6s ease-out;
    }
    
    .info-box strong {
        color: #2563eb;
        font-size: 1.1rem;
    }
    
    /* Professional Warning Box */
    .warning-box {
        background: white;
        border-left: 6px solid #dc2626;
        color: #1e293b;
        padding: 25px 30px;
        border-radius: 16px;
        margin: 20px 0;
        box-shadow: var(--shadow-md);
        animation: slideInUp 0.6s ease-out;
    }
    
    .warning-box strong {
        color: #dc2626;
        font-size: 1.1rem;
    }
    
    /* Professional Navigation Hint */
    .nav-hint {
        background: white;
        border-radius: 20px;
        padding: 30px 35px;
        margin-top: 40px;
        border-left: 6px solid #7c3aed;
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
    }
    
    .nav-hint:hover {
        transform: translateX(8px);
        box-shadow: var(--shadow-lg);
    }
    
    .nav-hint strong {
        color: #7c3aed;
        font-size: 1.2rem;
    }
    
    /* Professional Metric Cards */
    .metric-container {
        background: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
        border: 2px solid #f1f5f9;
        text-align: center;
    }
    
    .metric-container:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-8px);
        border-color: #667eea;
    }
    
    .metric-container h3 {
        font-size: 3rem;
        margin: 0;
    }
    
    .metric-container h2 {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin: 15px 0 5px 0;
    }
    
    .metric-container p {
        color: #64748b;
        font-weight: 500;
        margin: 0;
        font-size: 0.95rem;
    }
    
    /* Professional Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.7rem 1.8rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(5, 150, 105, 0.3);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(5, 150, 105, 0.4);
        background: linear-gradient(135deg, #047857 0%, #059669 100%);
    }
    
    /* Professional Expander */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 12px;
        font-weight: 600;
        padding: 18px 20px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
        color: #1e293b;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
        border-color: #667eea;
        box-shadow: var(--shadow-sm);
    }
    
    /* Select Box */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #cbd5e1;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #667eea;
    }
    
    /* Slider */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Radio Buttons */
    .stRadio > div {
        background: white;
        padding: 20px;
        border-radius: 16px;
        border: 2px solid #e2e8f0;
        box-shadow: var(--shadow-sm);
    }
    
    .stRadio > div:hover {
        border-color: #667eea;
    }
    
    /* Data Frame */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: white;
        padding: 10px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Professional Footer */
    .footer {
        text-align: center;
        color: #64748b;
        padding: 40px 20px;
        font-size: 0.95rem;
        border-top: 3px solid #e2e8f0;
        margin-top: 60px;
        background: white;
        border-radius: 24px 24px 0 0;
        box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .footer strong {
        color: #1e40af;
        font-size: 1.2rem;
        font-weight: 700;
    }
    
    /* Badge System */
    .badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 24px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin: 0 6px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }
    
    .badge-success {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
    }
    
    .badge-info {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        color: white;
    }
    
    .badge-warning {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        color: white;
    }
    
    /* Loading Spinner Override */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* File Uploader */
    .uploadedFile {
        border-radius: 12px;
        background: white;
        border: 2px solid #cbd5e1;
        box-shadow: var(--shadow-sm);
    }
    
    /* Number Input */
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #cbd5e1;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Metric Override */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    /* Divider */
    hr {
        margin: 3rem 0;
        border: none;
        height: 3px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        opacity: 0.3;
    }
    
    /* Section Headers */
    h1, h2, h3, h4 {
        color: #1e293b;
        font-weight: 700;
    }
    
    h2 {
        border-left: 5px solid #667eea;
        padding-left: 15px;
        margin-top: 2rem;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        
        .feature-card {
            padding: 2rem 1.5rem;
        }
        
        .upload-section {
            padding: 30px;
        }
        
        .badge {
            display: block;
            margin: 8px 0;
        }
    }
    
    /* Success Animation - Confetti Alternative */
    @keyframes checkmarkGrow {
        0% {
            transform: scale(0);
            opacity: 0;
        }
        50% {
            transform: scale(1.2);
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    .success-checkmark {
        width: 80px;
        height: 80px;
        margin: 0 auto;
        animation: checkmarkGrow 0.6s ease-out;
    }
    
    .success-checkmark circle {
        stroke-dasharray: 166;
        stroke-dashoffset: 166;
        stroke-width: 2;
        stroke: #059669;
        fill: none;
        animation: checkmarkCircle 0.6s ease-out forwards;
    }
    
    .success-checkmark path {
        stroke-dasharray: 48;
        stroke-dashoffset: 48;
        stroke: #059669;
        fill: none;
        stroke-width: 3;
        animation: checkmarkPath 0.3s 0.6s ease-out forwards;
    }
    
    @keyframes checkmarkCircle {
        to {
            stroke-dashoffset: 0;
        }
    }
    
    @keyframes checkmarkPath {
        to {
            stroke-dashoffset: 0;
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

def show_success_animation():
    """Display a professional success animation"""
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <svg class="success-checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
            <circle cx="26" cy="26" r="25"/>
            <path fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
        </svg>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(0.8)

# ==========================================
# HEADER SECTION
# ==========================================
st.markdown('<h1 class="main-header">🛡️ AI Fraud & Anomaly Detection System</h1>', unsafe_allow_html=True)
st.markdown("""
<p class="subtitle">
    <strong>Enterprise-Grade Intelligence for Detecting Fraudulent Activities in Public Sector Operations</strong><br>
    <span class="badge badge-info">AI Powered</span>
    <span class="badge badge-success">Real-time Analysis</span>
    <span class="badge badge-warning">Government Certified</span>
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
        <p><strong>Smart Alert</strong><br>Management System</p>
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
    "Select your preferred data source:",
    ["📊 Upload CSV/Excel File", "🔄 Generate Sample Dataset"],
    horizontal=True,
    help="Choose to upload your own data or generate sample data for testing purposes"
)

# ==========================================
# CSV/EXCEL UPLOAD
# ==========================================
if upload_option == "📊 Upload CSV/Excel File":
    st.markdown("""
    <div class="upload-section">
        <h4>📊 Import Transaction Data</h4>
        <p>Upload your transaction data in CSV or Excel format for comprehensive fraud analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls'],
        help="Supported formats: CSV, XLSX, XLS (Maximum file size: 200MB)",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        # File information display
        file_size_kb = uploaded_file.size / 1024
        file_size_display = f"{file_size_kb:.1f} KB" if file_size_kb < 1024 else f"{file_size_kb/1024:.1f} MB"
        
        st.markdown(f"""
        <div class="info-box">
            <strong>📄 File Information</strong><br>
            <strong>Name:</strong> {uploaded_file.name}<br>
            <strong>Size:</strong> {file_size_display}<br>
            <strong>Type:</strong> {uploaded_file.type}
        </div>
        """, unsafe_allow_html=True)
        
        # Advanced import options
        with st.expander("⚙️ Advanced Import Configuration", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                delimiter = st.selectbox(
                    "CSV Delimiter",
                    [",", ";", "\t", "|"],
                    help="Select the delimiter character used in your CSV file"
                )
            with col2:
                encoding = st.selectbox(
                    "Character Encoding",
                    ["utf-8", "latin-1", "cp1252"],
                    help="Select the character encoding of your file"
                )
        
        # Load data button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📥 Load and Process Data", type="primary", use_container_width=True):
                with st.spinner("🔄 Processing your data... Please wait"):
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
                        
                        # Show success animation
                        show_success_animation()
                        
                        # Success message
                        st.markdown(f"""
                        <div class="success-box">
                            <strong>✅ Data Successfully Loaded!</strong><br>
                            Successfully imported <strong>{len(df):,}</strong> records with <strong>{len(df.columns)}</strong> columns<br>
                            System is ready for fraud detection analysis
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show snow effect as alternative to balloons
                        st.snow()
                        
                    except Exception as e:
                        st.markdown(f"""
                        <div class="warning-box">
                            <strong>❌ Error Loading File</strong><br>
                            Unable to process the file: {str(e)}<br>
                            Please check your file format and try again
                        </div>
                        """, unsafe_allow_html=True)

# ==========================================
# SAMPLE DATA GENERATION
# ==========================================
elif upload_option == "🔄 Generate Sample Dataset":
    st.markdown("""
    <div class="upload-section">
        <h4>🔄 Generate Synthetic Dataset</h4>
        <p>Create realistic sample transaction data with embedded anomaly patterns for testing and demonstration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration parameters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        n_samples = st.slider(
            "📊 Transaction Volume",
            min_value=100,
            max_value=5000,
            value=1000,
            step=100,
            help="Total number of transactions to generate in the dataset"
        )
    
    with col2:
        anomaly_rate = st.slider(
            "⚠️ Anomaly Percentage",
            min_value=5,
            max_value=30,
            value=10,
            help="Percentage of transactions that will contain anomaly patterns"
        )
    
    with col3:
        random_seed = st.number_input(
            "🎲 Random Seed",
            min_value=1,
            max_value=9999,
            value=42,
            help="Seed value for reproducible dataset generation"
        )
    
    # Data schema preview
    with st.expander("📋 Dataset Schema & Anomaly Patterns", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Data Structure**")
            schema_data = {
                'Column Name': ['transaction_id', 'date', 'amount', 'category', 'department', 'vendor_id', 
                          'num_items', 'processing_days', 'is_weekend', 'approval_level', 'payment_method', 'region'],
                'Data Type': ['String', 'Date', 'Numeric', 'String', 'String', 'String', 
                        'Integer', 'Numeric', 'Binary', 'Integer', 'String', 'String'],
                'Description': ['Unique identifier', 'Transaction date', 'Transaction amount', 'Transaction category', 
                              'Department name', 'Vendor identifier', 'Number of items', 'Processing duration', 
                              'Weekend indicator', 'Approval level', 'Payment method', 'Geographic region']
            }
            st.dataframe(pd.DataFrame(schema_data), use_container_width=True, hide_index=True, height=400)
        
        with col2:
            st.markdown("**⚠️ Embedded Anomaly Patterns**")
            st.markdown("""
            - 💰 **Suspicious Amounts**
              - Extremely high transaction values
              - Unusually low micro-transactions
            
            - 📅 **Temporal Anomalies**
              - Weekend processing activities
              - After-hours transactions
            
            - 🏢 **Vendor Irregularities**
              - Unknown vendor IDs (900-999 range)
              - New or unverified vendors
            
            - ⚡ **Process Anomalies**
              - Rush approval patterns
              - Bypassed approval levels
            
            - 🔢 **Volume Anomalies**
              - Bulk item quantities
              - Unusual purchase volumes
            
            - 💳 **Payment Irregularities**
              - Wire transfers and cash payments
              - Non-standard payment methods
            """)
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Generate Synthetic Dataset", type="primary", use_container_width=True):
            with st.spinner("🔄 Generating synthetic transaction data... Please wait"):
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
                
                # Show success animation
                show_success_animation()
                
                # Success message
                expected_anomalies = int(n_samples * anomaly_rate / 100)
                st.markdown(f"""
                <div class="success-box">
                    <strong>✅ Dataset Generated Successfully!</strong><br>
                    Created <strong>{len(df):,}</strong> synthetic transactions<br>
                    Embedded approximately <strong>{expected_anomalies}</strong> anomaly patterns (~{anomaly_rate}%)<br>
                    Dataset generated with seed value: <strong>{random_seed}</strong>
                </div>
                """, unsafe_allow_html=True)
                
                # Show snow effect as alternative to balloons
                st.snow()

# ==========================================
# DATA PREVIEW SECTION
# ==========================================
if st.session_state.data is not None:
    st.markdown("---")
    st.header("📋 Data Overview & Statistical Summary")
    
    df = st.session_state.data
    summary = get_data_summary(df)
    
    # Top-level performance metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: #2563eb;">📊</h3>
            <h2>{:,}</h2>
            <p>Total Records</p>
        </div>
        """.format(summary['total_records']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: #059669;">📋</h3>
            <h2>{}</h2>
            <p>Data Columns</p>
        </div>
        """.format(summary['total_columns']), unsafe_allow_html=True)
    
    with col3:
        missing_color = "#dc2626" if summary['missing_values'] > 0 else "#059669"
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: {};">❓</h3>
            <h2>{}</h2>
            <p>Missing Values</p>
        </div>
        """.format(missing_color, summary['missing_values']), unsafe_allow_html=True)
    
    with col4:
        source_icon = "📊" if st.session_state.data_source == "CSV" else "📈" if st.session_state.data_source == "Excel" else "🔄"
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: #7c3aed;">{}</h3>
            <h2 style="font-size: 1.4rem;">{}</h2>
            <p>Data Source</p>
        </div>
        """.format(source_icon, st.session_state.data_source), unsafe_allow_html=True)
    
    with col5:
        if st.session_state.detection_run:
            anomaly_color = "#dc2626" if st.session_state.anomaly_count > 0 else "#059669"
            st.markdown("""
            <div class="metric-container">
                <h3 style="color: {};">🔍</h3>
                <h2>{}</h2>
                <p>Detected Anomalies</p>
            </div>
            """.format(anomaly_color, st.session_state.anomaly_count), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-container">
                <h3 style="color: #d97706;">🔍</h3>
                <h2 style="font-size: 1.3rem;">Pending</h2>
                <p>Analysis Status</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Financial statistics
    if 'amount' in df.columns:
        st.markdown("#### 💰 Financial Transaction Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Transaction Value", f"₹{summary['total_amount']:,.0f}", help="Aggregate sum of all transactions")
        with col2:
            st.metric("Average Transaction", f"₹{summary['avg_amount']:,.0f}", help="Mean transaction value")
        with col3:
            st.metric("Maximum Value", f"₹{df['amount'].max():,.0f}", help="Largest single transaction")
        with col4:
            st.metric("Minimum Value", f"₹{df['amount'].min():,.2f}", help="Smallest transaction amount")
    
    # Detailed column information
    with st.expander("📋 Comprehensive Column Information", expanded=False):
        col_info = pd.DataFrame({
            'Column Name': df.columns,
            'Data Type': df.dtypes.astype(str),
            'Non-Null Count': df.notna().sum().values,
            'Null Count': df.isnull().sum().values,
            'Unique Values': df.nunique().values,
            'Memory Usage': [f"{df[col].memory_usage(deep=True) / 1024:.1f} KB" for col in df.columns]
        })
        st.dataframe(col_info, use_container_width=True, hide_index=True, height=350)
    
    # Data table preview
    st.markdown("#### 📊 Transaction Data Preview")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        n_rows = st.selectbox("Display rows:", [10, 25, 50, 100, 250], index=0)
    with col2:
        st.markdown(f"<p style='text-align: center; color: #64748b; padding-top: 8px; font-weight: 500;'>Displaying {min(n_rows, len(df))} of {len(df):,} total records</p>", unsafe_allow_html=True)
    with col3:
        # Export functionality
        csv_data = df.to_csv(index=False)
        st.download_button(
            "📥 Export Dataset",
            data=csv_data,
            file_name=f"fraud_detection_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Download the complete dataset as CSV"
        )
    
    # Display interactive data table
    display_df = df.head(n_rows)
    st.dataframe(
        display_df,
        use_container_width=True,
        height=450,
        hide_index=True
    )

# ==========================================
# NAVIGATION GUIDANCE
# ==========================================
st.markdown("---")

if st.session_state.data is not None:
    st.markdown("""
    <div class="nav-hint">
        <strong>✅ System Ready - Data Successfully Loaded!</strong><br><br>
        <strong>Recommended Next Steps:</strong><br><br>
        Use the sidebar navigation panel (←) to access advanced features:<br><br>
        🔹 <strong>📊 Analytics Dashboard</strong> → Comprehensive metrics and data visualizations<br>
        🔹 <strong>🔍 Anomaly Detection</strong> → Execute AI-powered fraud detection algorithms<br>
        🔹 <strong>📈 Advanced Analytics</strong> → In-depth statistical analysis and insights<br>
        🔹 <strong>⚠️ Alert Management</strong> → Configure and monitor alert triggers<br>
        🔹 <strong>📋 Report Generation</strong> → Create and export professional reports<br>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="nav-hint">
        <strong>🚀 Welcome to the AI Fraud Detection System</strong><br><br>
        <strong>To begin your analysis:</strong><br><br>
        🔹 <strong>Option 1:</strong> Upload your CSV or Excel file containing transaction data<br>
        🔹 <strong>Option 2:</strong> Generate synthetic sample data to explore system capabilities<br><br>
        <em>Once your data is loaded, you'll gain full access to all analytical features and tools.</em>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# COMPREHENSIVE DOCUMENTATION
# ==========================================
with st.expander("📖 Complete System Documentation & User Guide", expanded=False):
    tab1, tab2, tab3 = st.tabs(["🚀 Quick Start", "📚 User Manual", "❓ FAQ & Support"])
    
    with tab1:
        st.markdown("""
        ### Quick Start Guide - 5 Simple Steps
        
        **Step 1: Data Acquisition** 📁
        - Upload a CSV or Excel file containing your transaction data
        - Alternatively, generate synthetic sample data for system exploration
        - Ensure your data includes key fields: transaction_id, date, amount, category
        
        **Step 2: Data Verification** 👀
        - Review the data preview table to confirm successful import
        - Examine column types and validate data structure
        - Check data quality metrics and identify any missing values
        - Verify financial statistics align with expectations
        
        **Step 3: Detection Configuration** ⚙️
        - Navigate to **🔍 Anomaly Detection** via the sidebar
        - Select relevant features for analysis
        - Choose your preferred detection algorithm:
          - Isolation Forest (recommended for general use)
          - Local Outlier Factor (for density-based anomalies)
          - One-Class SVM (for high-dimensional data)
        - Adjust sensitivity and contamination parameters
        
        **Step 4: Execute Detection** 🔍
        - Click the "Run Detection" button to initiate analysis
        - Monitor the detection progress
        - Review identified anomalies and their confidence scores
        - Analyze patterns and distributions of detected anomalies
        
        **Step 5: Results & Reporting** 📊
        - Examine comprehensive results in the **📊 Dashboard**
        - Configure and review alerts in **⚠️ Alert Management**
        - Generate professional reports via **📋 Report Generation**
        - Export results in your preferred format (CSV/Excel)
        """)
    
    with tab2:
        st.markdown("""
        ### Complete User Manual
        
        **System Requirements & Data Specifications**
        - **Supported Formats:** CSV, Excel (XLSX, XLS)
        - **Maximum File Size:** 200MB per upload
        - **Required Columns:** transaction_id, date, amount (minimum)
        - **Recommended Columns:** category, department, vendor_id, payment_method
        - **Data Types:** Numeric columns for quantitative analysis, categorical for segmentation
        
        **Available Detection Algorithms**
        
        1. **Isolation Forest**
           - Best suited for general-purpose anomaly detection
           - Effective with high-dimensional datasets
           - Works by isolating observations through random partitioning
           - Recommended contamination: 5-15%
        
        2. **Local Outlier Factor (LOF)**
           - Identifies anomalies based on local density deviation
           - Excellent for detecting clustered anomalies
           - Compares local density of point with neighbors
           - Best for structured transaction patterns
        
        3. **One-Class SVM**
           - Effective for high-dimensional feature spaces
           - Creates decision boundary around normal data
           - Robust to outliers in training data
           - Requires careful parameter tuning
        
        4. **Statistical Methods**
           - Z-score based detection (3-sigma rule)
           - Interquartile Range (IQR) method
           - Suitable for normally distributed data
           - Fast computation for large datasets
        
        **Best Practices for Optimal Results**
        
        - **Data Quality:** Ensure data cleanliness before analysis
        - **Feature Selection:** Choose relevant features based on domain knowledge
        - **Parameter Tuning:** Start conservative, adjust based on results
        - **Validation:** Always review and validate detected anomalies
        - **Documentation:** Maintain records of detection parameters and results
        - **Regular Updates:** Refresh your analysis as new data becomes available
        
        **Interpreting Results**
        
        - **Anomaly Score:** Higher scores indicate greater deviation from normal patterns
        - **Confidence Level:** Represents the model's certainty in the classification
        - **Pattern Analysis:** Look for common characteristics among flagged transactions
        - **False Positives:** Review and filter out legitimate unusual transactions
        """)
    
    with tab3:
        st.markdown("""
        ### Frequently Asked Questions
        
        **General Questions**
        
        **Q: What file formats are supported for data upload?**  
        A: The system supports CSV, XLSX, and XLS formats. CSV files can use various delimiters (comma, semicolon, tab, pipe).
        
        **Q: What is the maximum dataset size the system can handle?**  
        A: The system efficiently processes datasets up to 1 million records. For larger datasets, consider batch processing.
        
        **Q: How long does the detection process take?**  
        A: Processing time varies based on dataset size and algorithm. Typically:
        - Small datasets (<10K records): 5-15 seconds
        - Medium datasets (10K-100K): 30-60 seconds
        - Large datasets (>100K): 1-5 minutes
        
        **Technical Questions**
        
        **Q: What is the anomaly rate and how should I set it?**  
        A: The anomaly rate represents the expected percentage of fraudulent transactions. Start with 5-10% and adjust based on your industry and historical data.
        
        **Q: Can I customize the detection parameters?**  
        A: Yes, you can adjust sensitivity levels, contamination rates, feature selection, and algorithm-specific parameters through the configuration panel.
        
        **Q: How should I interpret anomaly scores?**  
        A: Anomaly scores typically range from 0-1 (or -1 to 1 depending on algorithm). Higher absolute values indicate greater deviation from normal patterns. Scores above 0.7 warrant immediate investigation.
        
        **Q: What makes a transaction flagged as anomalous?**  
        A: Transactions are flagged based on deviations in multiple dimensions: unusual amounts, irregular timing, suspicious vendors, abnormal approval patterns, or atypical payment methods.
        
        **Data Security & Privacy**
        
        **Q: Is my data secure and private?**  
        A: Yes. All data processing occurs locally within your browser session. Data is not stored permanently on external servers and is cleared when you close your session.
        
        **Q: Can I export and save my analysis results?**  
        A: Absolutely. Results can be exported as CSV or Excel files with comprehensive details including anomaly scores, flagged transactions, and statistical summaries.
        
        **Q: Does the system comply with data protection regulations?**  
        A: The system is designed with privacy-first principles and does not transmit or store your sensitive data externally.
        
        **Support & Troubleshooting**
        
        **Q: What if my file upload fails?**  
        A: Common solutions:
        - Verify file format is supported (CSV, XLSX, XLS)
        - Check file size is under 200MB
        - Ensure file is not corrupted or password-protected
        - Try different encoding options (UTF-8, Latin-1)
        
        **Q: The detection is taking too long. What should I do?**  
        A: For large datasets:
        - Consider using a sample of your data first
        - Try the Isolation Forest algorithm (fastest)
        - Reduce the number of features selected
        - Ensure no other resource-intensive processes are running
        """)

# ==========================================
# PROFESSIONAL FOOTER
# ==========================================
st.markdown("""
<div class="footer">
    🛡️ <strong>AI Fraud & Anomaly Detection System</strong><br>
    <strong>Professional Edition v2.0</strong><br>
    Powered by Advanced Machine Learning & Statistical Analysis<br><br>
    <small>Built with precision using Streamlit Framework</small><br>
    <small>Engineered for Government Transparency, Public Sector Integrity & Financial Compliance</small><br><br>
    <small style="color: #94a3b8;">© 2024 - All Rights Reserved | Enterprise-Grade Security & Privacy</small>
</div>
""", unsafe_allow_html=True)
