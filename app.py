"""
AI Fraud & Anomaly Detection System
Main Application - UI Refined (Logic Preserved)
Day 2 Updates: Department Filter, Button Wording, UX Cleanup
Day 3 Updates: Database Persistence Layer
Day 4 Updates: Schema Mapper & Dataset Validation
Day 5 Updates: built the REAL data engineering layer
Day 6 Updates: integrated pipeline into real UI & persistence
Day 7 Updates: stabilized it like a real product
Day 8 Updates: Secure Authentication System
Day 9 Updates: Role-Based Access Control (RBAC)
Day 10 Updates: Multi-Tenant Organization System
Day 11 Updates: Audit Rule Engine Integration
Day 12 Updates: Audit Case Management System
Landing Page: Home.py integration
Sidebar Navigation: Clean professional sidebar
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import sys
from pathlib import Path

def normalize_health_output(df, health_basic):
    """
    Converts pipeline health format into full UI-compatible format
    without modifying pipeline logic.
    """
    full_health = {}

    full_health["total_rows"] = len(df)
    full_health["total_columns"] = len(df.columns)

    # Duplicate rows
    dup_count = df.duplicated().sum()
    full_health["duplicate_rows"] = int(dup_count)

    # Missing values
    missing = {}
    for col in df.columns:
        count = df[col].isna().sum()
        missing[col] = {
            "count": int(count),
            "percentage": round((count / len(df) * 100), 2) if len(df) > 0 else 0
        }

    full_health["missing_values"] = missing

    # Data types
    full_health["data_types"] = {col: str(dtype) for col, dtype in df.dtypes.items()}

    # Value ranges for numeric columns
    value_ranges = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        value_ranges[col] = {
            "min": float(df[col].min()) if df[col].notna().any() else None,
            "max": float(df[col].max()) if df[col].notna().any() else None,
            "mean": float(df[col].mean()) if df[col].notna().any() else None
        }

    full_health["value_ranges"] = value_ranges

    # Copy advanced metrics if available
    if health_basic:
        full_health.update(health_basic)

    full_health["issues"] = []

    return full_health


# ========== DATABASE INITIALIZATION ==========
import database

# Initialize database on app startup
try:
    database.init_database()
except Exception as e:
    st.error(f"⚠️ Database initialization error: {e}")
# ========== END DATABASE INITIALIZATION ==========

# ========== AUTHENTICATION IMPORT ==========
import auth

# Initialize session state for authentication
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
# ========== END AUTHENTICATION IMPORT ==========

# ========== SCHEMA MAPPER IMPORT ==========
# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from utils.schema_mapper import (
        detect_columns,
        map_to_standard_schema,
        validate_required_fields,
        get_data_health_summary,
        get_available_columns,
        validate_dataset_integrity,
        STANDARD_SCHEMA
    )
    SCHEMA_MAPPER_AVAILABLE = True
except ImportError:
    SCHEMA_MAPPER_AVAILABLE = False
    print("Warning: utils/schema_mapper.py not found - column mapping disabled")
# ========== END SCHEMA MAPPER IMPORT ==========

# ========== DATA PIPELINE IMPORT ==========
try:
    from utils.data_pipeline import (
        auto_detect_columns as pipeline_auto_detect,
        clean_dataset,
        compute_health_score,
        enrich_features,
        run_complete_pipeline,
        validate_pipeline_output
    )
    DATA_PIPELINE_AVAILABLE = True
except ImportError:
    DATA_PIPELINE_AVAILABLE = False
    print("Warning: utils/data_pipeline.py not found - advanced pipeline disabled")
# ========== END DATA PIPELINE IMPORT ==========

# ========== AUDIT ENGINE IMPORT ==========
try:
    from utils.audit_engine import (
        generate_audit_flags,
        summarize_audit_findings,
        get_audit_rules_documentation
    )
    AUDIT_ENGINE_AVAILABLE = True
except ImportError:
    AUDIT_ENGINE_AVAILABLE = False
    print("Warning: utils/audit_engine.py not found - audit rules disabled")
# ========== END AUDIT ENGINE IMPORT ==========

# ========== AUDIT CASE MANAGER IMPORT ==========
try:
    from utils.AuditCaseManager import (
        create_audit_cases,
        update_case_status,
        assign_case,
        add_case_comment,
        get_case_summary
    )
    AUDIT_CASE_MANAGER_AVAILABLE = True
except ImportError:
    AUDIT_CASE_MANAGER_AVAILABLE = False
    print("Warning: Audit Case Manager not available")
# ========== END AUDIT CASE MANAGER IMPORT ==========

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Verilens - AI Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit's default page navigation
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# ========== AUTHENTICATION CHECK - REDIRECT TO LANDING PAGE ==========
# Check if user is logged in
if not st.session_state.get('authenticated'):
    # Redirect to landing page (Home.py)
    st.switch_page("Home.py")
# ========== END AUTHENTICATION CHECK ==========

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

.user-info-box {
    background: linear-gradient(145deg, #1a1f3a, #0f1424);
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #7c7cff;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ========== CUSTOM SIDEBAR NAVIGATION ==========
with st.sidebar:
    # Sidebar title
    st.markdown("## 🛡️ Verilens")
    st.caption("AI Audit Intelligence Platform")
    
    st.markdown("---")
    
    # User info section
    st.markdown('<div class="user-info-box">', unsafe_allow_html=True)
    st.markdown("### 👤 Logged in as:")
    st.success(f"**{st.session_state['user']['username']}**")
    st.caption(f"📧 {st.session_state['user']['email']}")
    
    # Display role
    role = st.session_state['user'].get('role', 'viewer')
    role_colors = {
        'admin': '🔴',
        'auditor': '🟡',
        'viewer': '🟢'
    }
    role_badge = role_colors.get(role, '⚪')
    st.info(f"{role_badge} **Role:** {role.upper()}")
    
    # Display organization
    org_id = st.session_state['user'].get('organization_id')
    if org_id:
        try:
            org = database.get_organization_by_id(org_id)
            if org:
                st.info(f"🏢 **Organization:** {org['name']}")
        except:
            pass
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation section
    st.markdown("### 📍 Navigation")
    
    # Main pages
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("pages/Home.py")
    
    if st.button("📂 Data Upload", use_container_width=True, type="primary"):
        st.switch_page("app.py")
    
    st.markdown("---")
    st.markdown("**Analysis & Detection**")
    
    if st.button("🤖 Anomaly Detection", use_container_width=True):
        st.switch_page("pages/_Anomaly_Detection.py")
    
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/Dashboard.py")
    
    if st.button("🚨 Alerts", use_container_width=True):
        st.switch_page("pages/_Alerts.py")
    
    st.markdown("---")
    st.markdown("**Reports & Analytics**")
    
    if st.button("📑 Reports", use_container_width=True):
        st.switch_page("pages/_Reports.py")
    
    st.markdown("---")
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True, type="secondary"):
        # Clear session state
        st.session_state['user'] = None
        st.session_state['authenticated'] = False
        
        # Clear other session data
        for key in list(st.session_state.keys()):
            if key not in ['user', 'authenticated']:
                del st.session_state[key]
        
        st.success("✓ Logged out successfully")
        st.rerun()
    
    st.markdown("---")
    
    # Footer
    st.caption("Verilens AI Audit Platform")
    st.caption("© 2024 Verilens Team")
# ========== END SIDEBAR NAVIGATION ==========

# ==========================================
# SESSION STATE
# ==========================================
if 'data' not in st.session_state:
    st.session_state.data = None
if 'detection_run' not in st.session_state:
    st.session_state.detection_run = False
if 'selected_department' not in st.session_state:
    st.session_state.selected_department = 'All Departments'

# ========== NEW SESSION STATE FOR SCHEMA MAPPER ==========
if 'raw_uploaded_data' not in st.session_state:
    st.session_state.raw_uploaded_data = None

if 'column_mapping' not in st.session_state:
    st.session_state.column_mapping = {}

if 'schema_validated' not in st.session_state:
    st.session_state.schema_validated = False

if 'data_health' not in st.session_state:
    st.session_state.data_health = None

if 'pipeline_mode' not in st.session_state:
    st.session_state.pipeline_mode = 'auto'  # 'auto' or 'manual'

# ========== NEW: AUDIT ENGINE SESSION STATE ==========
if 'audit_processed' not in st.session_state:
    st.session_state.audit_processed = False
# ========== END AUDIT SESSION STATE ==========

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
# DATABASE STATUS INDICATOR WITH RBAC AND ORGANIZATION
# ==========================================
try:
    user_id = st.session_state['user']['id']
    user_role = st.session_state['user'].get('role', 'viewer')
    organization_id = st.session_state['user'].get('organization_id')
    
    db_summary = database.get_audit_summary(
        user_id=user_id, 
        user_role=user_role, 
        organization_id=organization_id
    )
    
    if db_summary['total_transactions'] > 0:
        scope = "All organization" if user_role == 'admin' else "Your"
        st.info(
            f"💾 Database Active: {db_summary['total_transactions']:,} {scope.lower()} transactions stored | "
            "Visit Reports page to export audit data"
        )
except:
    pass

# ==========================================
# GLOBAL DEPARTMENT SELECTOR
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
# DATA UPLOAD SECTION (ENHANCED WITH DATA PIPELINE)
# ==========================================
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.header("📁 Data Upload & Validation")

option = st.radio(
    "Choose data source:",
    ["Upload CSV/Excel File", "Load Test Dataset"],
    horizontal=True
)

if option == "Upload CSV/Excel File":
    file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    if file:
        try:
            # Load raw data
            if file.name.endswith(".csv"):
                raw_df = pd.read_csv(file)
            else:
                raw_df = pd.read_excel(file)
            
            st.session_state.raw_uploaded_data = raw_df
            st.session_state.schema_validated = False  # Reset validation
            st.session_state.audit_processed = False  # Reset audit
            
            st.success(f"✓ File uploaded: {len(raw_df)} rows, {len(raw_df.columns)} columns")
            
            # Pipeline mode selector
            st.markdown("---")
            pipeline_mode = st.radio(
                "Processing Mode:",
                ["🚀 Auto Pipeline (Recommended)", "🔧 Manual Mapping"],
                horizontal=True,
                help="Auto Pipeline: Automatic column detection, cleaning, and enrichment. Manual: Step-by-step configuration."
            )
            
            st.session_state.pipeline_mode = 'auto' if 'Auto' in pipeline_mode else 'manual'
            
            # Auto Pipeline
            if st.session_state.pipeline_mode == 'auto' and DATA_PIPELINE_AVAILABLE:
                st.markdown("#### 🚀 Automatic Data Pipeline")
                
                run_pipeline = st.button("▶️ Run Auto Pipeline", type="primary", use_container_width=True)

                if run_pipeline and not st.session_state.schema_validated:
                    with st.spinner("🔄 Running automated data pipeline..."):
                        try:
                            # Run complete pipeline
                            df_processed, health = run_complete_pipeline(raw_df)
                            
                            # Validate output
                            is_valid, issues = validate_pipeline_output(df_processed)
                            
                            if is_valid:
                                # Apply audit engine
                                if AUDIT_ENGINE_AVAILABLE:
                                    with st.spinner("🔍 Running audit rule engine..."):
                                        df_processed = generate_audit_flags(df_processed)
                                        st.session_state.audit_processed = True
                                        
                                        audit_summary = summarize_audit_findings(df_processed)
                                        st.success(f"✓ Audit engine processed: {audit_summary['total_flagged']} transactions flagged")
                                        
                                        # Create audit cases
                                        if AUDIT_CASE_MANAGER_AVAILABLE:
                                            df_processed = create_audit_cases(df_processed)
                                            
                                            # Count created cases
                                            cases_created = df_processed['audit_case_id'].notna().sum()
                                            if cases_created > 0:
                                                st.success(f"✓ Created {cases_created} audit cases for high/medium severity transactions")
                                                
                                                # Save cases to database
                                                try:
                                                    database.insert_audit_cases(df_processed)
                                                except Exception as e:
                                                    st.warning(f"Cases created but not saved to database: {e}")
                                
                                normalized_health = normalize_health_output(df_processed, health)

                                st.session_state.update({
                                    "data": df_processed,
                                    "schema_validated": True,
                                    "data_health": normalized_health
                                })

                                # Save to database
                                try:
                                    user_id = st.session_state['user']['id']
                                    organization_id = st.session_state['user'].get('organization_id')

                                    if "date" in df_processed.columns and "transaction_date" not in df_processed.columns:
                                        df_processed["transaction_date"] = df_processed["date"]

                                    database.insert_dataframe(df_processed, user_id=user_id, organization_id=organization_id)

                                    st.success("✅ Dataset processed and saved to your organization")

                                except Exception as e:
                                    st.warning(f"Dataset processed but not saved to database: {e}")
                                
                                # Show health metrics
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    st.metric("Completeness", f"{health['completeness']}%")
                                
                                with col2:
                                    st.metric("Validity", f"{health['validity']}%")
                                
                                with col3:
                                    st.metric("Duplicates", health['duplicates'])
                                
                                with col4:
                                    score_color = "🟢" if health['overall_score'] >= 80 else "🟡" if health['overall_score'] >= 60 else "🔴"
                                    st.metric("Overall Health", f"{score_color} {health['overall_score']}")
                                
                                st.info("✨ **Enriched Features Added:** monthly_spend_per_department, vendor_transaction_count, zscore_amount, amount_percentile, day_of_week, is_weekend")
                            
                            else:
                                st.warning("⚠️ Pipeline validation issues:")
                                for issue in issues:
                                    st.warning(f"  • {issue}")
                                st.info("Data processed but may have quality issues. Review and proceed with caution.")
                                
                                normalized_health = normalize_health_output(df_processed, health)

                                st.session_state.update({
                                    "data": df_processed,
                                    "schema_validated": True,
                                    "data_health": normalized_health
                                })

                                st.success("✅ Dataset processed successfully")

                        except Exception as e:
                            st.error(f"❌ Pipeline error: {e}")
                            st.info("Falling back to manual mapping mode...")
                            st.session_state.pipeline_mode = 'manual'
            
            elif st.session_state.pipeline_mode == 'auto' and not DATA_PIPELINE_AVAILABLE:
                st.warning("⚠️ Auto pipeline not available. Install data_pipeline.py or use manual mapping.")
                st.session_state.pipeline_mode = 'manual'
            
            # Show raw preview
            with st.expander("🔍 View Raw Data"):
                st.dataframe(raw_df.head(10), use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
            st.session_state.raw_uploaded_data = None

else:
    rows = st.slider("Number of records", 100, 5000, 1000)
    if st.button("📊 Load Test Dataset", use_container_width=True):
        raw_df = generate_sample_data(rows)
        st.session_state.raw_uploaded_data = raw_df
        st.session_state.schema_validated = False
        st.session_state.audit_processed = False
        
        # For test data, auto-validate since it's already in standard format
        if DATA_PIPELINE_AVAILABLE:
            # Enrich test data with pipeline features
            df_enriched = enrich_features(raw_df)
            health = compute_health_score(df_enriched)
            
            # Apply audit engine
            if AUDIT_ENGINE_AVAILABLE:
                df_enriched = generate_audit_flags(df_enriched)
                st.session_state.audit_processed = True
                audit_summary = summarize_audit_findings(df_enriched)
                st.info(f"🔍 Audit: {audit_summary['total_flagged']} transactions flagged")
                
                # Create audit cases
                if AUDIT_CASE_MANAGER_AVAILABLE:
                    df_enriched = create_audit_cases(df_enriched)
                    cases_created = df_enriched['audit_case_id'].notna().sum()
                    if cases_created > 0:
                        st.info(f"📋 Created {cases_created} audit cases")
                        
                        # Save cases to database
                        try:
                            database.insert_audit_cases(df_enriched)
                        except:
                            pass
            
            st.session_state.data = df_enriched
            normalized_health = normalize_health_output(df_enriched, health)
            st.session_state.data_health = normalized_health
            
            # Save to database
            try:
                user_id = st.session_state['user']['id']
                organization_id = st.session_state['user'].get('organization_id')
                database.insert_dataframe(df_enriched, user_id=user_id, organization_id=organization_id)
                st.success("✓ Test dataset loaded and saved to your organization")
            except Exception as e:
                st.warning(f"Dataset loaded but not saved to database: {e}")

        else:
            st.session_state.data = raw_df
            st.session_state.data_health = get_data_health_summary(raw_df) if SCHEMA_MAPPER_AVAILABLE else None
        
        st.session_state.schema_validated = True

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# FOOTER
# ==========================================
st.markdown("""
<div class="footer">
🛡️ Verilens AI Audit Platform · Hack4Delhi · Verilens Team<br>
Built with Streamlit · Explainable AI · Department-Based Risk Analysis · Persistent Audit Trail · Smart Data Validation · Automated Pipeline · Secure Authentication · Role-Based Access Control · Multi-Tenant Organizations · Intelligent Audit Rules · Audit Case Management
</div>
""", unsafe_allow_html=True)
