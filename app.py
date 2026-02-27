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

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AI Fraud Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== AUTHENTICATION CHECK ==========
# Check if user is logged in
if not st.session_state.get('authenticated'):
    st.markdown('<div class="main-title">AI Fraud & Anomaly Detection</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="subtitle">
    Designed for auditors to identify high-risk public transactions using explainable AI and real-time monitoring.
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("🔒 Please login to access the application")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info("You need to be logged in to use the AI Fraud Detection System")
        
        col_login, col_signup = st.columns(2)
        
        with col_login:
            if st.button("🔐 Login", use_container_width=True, type="primary"):
                st.switch_page("pages/_Login.py")
        
        with col_signup:
            if st.button("📝 Sign Up", use_container_width=True):
                st.switch_page("pages/_Signup.py")
    
    st.markdown("---")
    st.markdown("""
    <div class="footer">
    🛡️ AI Fraud Detection System · Secure Authentication Required<br>
    Built with Streamlit · Enterprise-Grade Security
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()
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

# ========== SIDEBAR USER INFO WITH RBAC AND ORGANIZATION ==========
with st.sidebar:
    st.markdown("---")
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
    
    # ========== NEW: DISPLAY ORGANIZATION ==========
    org_id = st.session_state['user'].get('organization_id')
    if org_id:
        try:
            org = database.get_organization_by_id(org_id)
            if org:
                st.info(f"🏢 **Organization:** {org['name']}")
        except:
            pass
    # ========== END ORGANIZATION DISPLAY ==========
    
    st.markdown('</div>', unsafe_allow_html=True)
    
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
# ========== END SIDEBAR USER INFO ==========

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
# ========== END NEW SESSION STATE ==========

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
    organization_id = st.session_state['user'].get('organization_id')  # NEW
    
    db_summary = database.get_audit_summary(
        user_id=user_id, 
        user_role=user_role, 
        organization_id=organization_id  # NEW
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
            
            st.success(f"✓ File uploaded: {len(raw_df)} rows, {len(raw_df.columns)} columns")
            
            # ========== NEW: PIPELINE MODE SELECTOR ==========
            st.markdown("---")
            pipeline_mode = st.radio(
                "Processing Mode:",
                ["🚀 Auto Pipeline (Recommended)", "🔧 Manual Mapping"],
                horizontal=True,
                help="Auto Pipeline: Automatic column detection, cleaning, and enrichment. Manual: Step-by-step configuration."
            )
            
            st.session_state.pipeline_mode = 'auto' if 'Auto' in pipeline_mode else 'manual'
            # ========== END PIPELINE MODE SELECTOR ==========
            
            # ========== NEW: AUTO PIPELINE ==========
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
                                normalized_health = normalize_health_output(df_processed, health)

                                st.session_state.update({
                                    "data": df_processed,
                                    "schema_validated": True,
                                    "data_health": normalized_health
                                })

                                # ========== MODIFIED: SAVE WITH ORGANIZATION_ID ==========
                                try:
                                    user_id = st.session_state['user']['id']
                                    organization_id = st.session_state['user'].get('organization_id')

                                    # Bridge pipeline date to DB schema
                                    if "date" in df_processed.columns and "transaction_date" not in df_processed.columns:
                                        df_processed["transaction_date"] = df_processed["date"]

                                    database.insert_dataframe(df_processed, user_id=user_id, organization_id=organization_id)

                                    st.success("✅ Dataset processed and saved to your organization")

                                except Exception as e:
                                    st.warning(f"Dataset processed but not saved to database: {e}")
                                # ========== END DATABASE SAVE ==========
                                
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
                                
                                # Show enriched features
                                st.info("✨ **Enriched Features Added:** monthly_spend_per_department, vendor_transaction_count, zscore_amount, amount_percentile, day_of_week, is_weekend")
                            
                            else:
                                st.warning("⚠️ Pipeline validation issues:")
                                for issue in issues:
                                    st.warning(f"  • {issue}")
                                st.info("Data processed but may have quality issues. Review and proceed with caution.")
                                
                                # Still save the data
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
            # ========== END AUTO PIPELINE ==========
            
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
        
        # For test data, auto-validate since it's already in standard format
        if DATA_PIPELINE_AVAILABLE:
            # Enrich test data with pipeline features
            df_enriched = enrich_features(raw_df)
            health = compute_health_score(df_enriched)
            
            st.session_state.data = df_enriched
            normalized_health = normalize_health_output(df_enriched, health)
            st.session_state.data_health = normalized_health
            
            # ========== MODIFIED: SAVE WITH ORGANIZATION_ID ==========
            try:
                user_id = st.session_state['user']['id']
                organization_id = st.session_state['user'].get('organization_id')
                database.insert_dataframe(df_enriched, user_id=user_id, organization_id=organization_id)
                st.success("✓ Test dataset loaded and saved to your organization")
            except Exception as e:
                st.warning(f"Dataset loaded but not saved to database: {e}")
            # ========== END DATABASE SAVE ==========

        else:
            st.session_state.data = raw_df
            st.session_state.data_health = get_data_health_summary(raw_df) if SCHEMA_MAPPER_AVAILABLE else None
        
        st.session_state.schema_validated = True

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# COLUMN MAPPING & VALIDATION (MANUAL MODE)
# ==========================================
if (st.session_state.raw_uploaded_data is not None and 
    SCHEMA_MAPPER_AVAILABLE and 
    option == "Upload CSV/Excel File" and 
    st.session_state.pipeline_mode == 'manual'):
    
    raw_df = st.session_state.raw_uploaded_data
    
    # Dataset Integrity Check
    is_valid, warnings = validate_dataset_integrity(raw_df)
    
    if warnings:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("⚠️ Data Quality Warnings")
        for warning in warnings:
            st.warning(warning)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if not is_valid:
        st.error("❌ Dataset failed integrity check. Please upload a valid dataset.")
        st.stop()
    
    # Column Mapping Interface
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.header("🔗 Manual Column Mapping")
    
    # Auto-detect columns
    if not st.session_state.column_mapping:
        detected_mapping = detect_columns(raw_df)
        st.session_state.column_mapping = detected_mapping
    
    st.markdown("**Map your dataset columns to the standard schema:**")
    
    # Create mapping UI
    mapping_changed = False
    new_mapping = {}
    
    col1, col2 = st.columns(2)
    
    available_cols = get_available_columns(raw_df)
    
    for i, (standard_field, config) in enumerate(STANDARD_SCHEMA.items()):
        with col1 if i % 2 == 0 else col2:
            current_value = st.session_state.column_mapping.get(standard_field)
            
            # Determine default index
            if current_value and current_value in available_cols:
                default_idx = available_cols.index(current_value)
            else:
                default_idx = 0
            
            # Label with required indicator
            label = f"**{standard_field}**" + (" (Required)" if config['required'] else " (Optional)")
            
            selected = st.selectbox(
                label,
                available_cols,
                index=default_idx,
                key=f"map_{standard_field}",
                help=f"Aliases: {', '.join(config['aliases'][:3])}"
            )
            
            new_mapping[standard_field] = None if selected == 'None' else selected
            
            if new_mapping[standard_field] != st.session_state.column_mapping.get(standard_field):
                mapping_changed = True
    
    # Update mapping if changed
    if mapping_changed:
        st.session_state.column_mapping = new_mapping
        st.session_state.schema_validated = False
    
    # Validate and Apply Mapping
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("✅ Validate & Apply Mapping", type="primary", use_container_width=True):
            # Map to standard schema
            try:
                standardized_df = map_to_standard_schema(raw_df, st.session_state.column_mapping)
                
                # Validate required fields
                is_valid, missing_fields = validate_required_fields(standardized_df)
                
                if is_valid:
                    # Apply data pipeline cleaning and enrichment if available
                    if DATA_PIPELINE_AVAILABLE:
                        try:
                            df_clean = clean_dataset(raw_df, st.session_state.column_mapping)
                            df_enriched = enrich_features(df_clean)
                            health = compute_health_score(df_enriched)
                            
                            st.session_state.data = df_enriched
                            normalized_health = normalize_health_output(df_enriched, health)
                            st.session_state.data_health = normalized_health
                            
                            # ========== MODIFIED: SAVE WITH ORGANIZATION_ID ==========
                            try:
                                user_id = st.session_state['user']['id']
                                organization_id = st.session_state['user'].get('organization_id')
                                database.insert_dataframe(df_enriched, user_id=user_id, organization_id=organization_id)
                                st.success("✓ Schema validated, cleaned, enriched, and saved to your organization!")
                            except Exception as e:
                                st.success("✓ Schema validated, cleaned, and enriched successfully!")
                                st.warning(f"Not saved to database: {e}")
                            # ========== END DATABASE SAVE ==========
                        except:
                            st.session_state.data = standardized_df
                            st.session_state.data_health = get_data_health_summary(standardized_df)
                            st.success("✓ Schema validated and applied successfully!")
                    else:
                        st.session_state.data = standardized_df
                        st.session_state.data_health = get_data_health_summary(standardized_df)
                        st.success("✓ Schema validated and applied successfully!")
                    
                    st.session_state.schema_validated = True
                    st.rerun()
                else:
                    st.error("❌ Validation failed. Missing required fields:")
                    for field in missing_fields:
                        st.error(f"  • {field}")
            
            except Exception as e:
                st.error(f"❌ Error during mapping: {e}")
    
    with col2:
        if st.button("🔄 Auto-Detect Again", use_container_width=True):
            st.session_state.column_mapping = detect_columns(raw_df)
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear Mapping", use_container_width=True):
            st.session_state.column_mapping = {}
            st.session_state.schema_validated = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# DATA HEALTH SUMMARY (ENHANCED)
# ==========================================
if st.session_state.schema_validated and st.session_state.data_health is not None:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.header("🏥 Data Health Summary")
    
    health = st.session_state.data_health
    
    # Overall Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rows", f"{health['total_rows']:,}")
    with col2:
        st.metric("Total Columns", health['total_columns'])
    with col3:
        dup_pct = (health['duplicate_rows'] / health['total_rows'] * 100) if health['total_rows'] > 0 else 0
        st.metric("Duplicate Rows", health['duplicate_rows'], delta=f"{dup_pct:.1f}%", delta_color="inverse")
    with col4:
        total_missing = sum(v['count'] for v in health['missing_values'].values())
        total_cells = health['total_rows'] * health['total_columns']
        missing_pct = (total_missing / total_cells * 100) if total_cells > 0 else 0
        st.metric("Missing Values", total_missing, delta=f"{missing_pct:.1f}%", delta_color="inverse")
    
    # Show advanced health metrics if available
    if 'overall_score' in health:
        st.markdown("#### 📊 Advanced Health Metrics")
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            comp_color = "🟢" if health['completeness'] >= 90 else "🟡" if health['completeness'] >= 70 else "🔴"
            st.metric("Completeness", f"{comp_color} {health['completeness']}%")
        
        with metric_col2:
            val_color = "🟢" if health['validity'] >= 90 else "🟡" if health['validity'] >= 70 else "🔴"
            st.metric("Validity", f"{val_color} {health['validity']}%")
        
        with metric_col3:
            cons_color = "🟢" if health.get('consistency', 100) >= 90 else "🟡" if health.get('consistency', 100) >= 70 else "🔴"
            st.metric("Consistency", f"{cons_color} {health.get('consistency', 100)}%")
        
        with metric_col4:
            score_color = "🟢" if health['overall_score'] >= 80 else "🟡" if health['overall_score'] >= 60 else "🔴"
            st.metric("Overall Score", f"{score_color} {health['overall_score']}")
    
    # Missing Values Breakdown
    st.markdown("#### Missing Values by Column")
    
    missing_data = []
    for col, stats in health['missing_values'].items():
        if stats['count'] > 0:
            missing_data.append({
                'Column': col,
                'Missing Count': stats['count'],
                'Missing %': stats['percentage']
            })
    
    if missing_data:
        missing_df = pd.DataFrame(missing_data)
        st.dataframe(missing_df, use_container_width=True, hide_index=True)
    else:
        st.success("✓ No missing values detected!")
    
    # Issues
    if health.get('issues'):
        st.markdown("#### ⚠️ Data Quality Issues")
        for issue in health['issues']:
            st.warning(issue)
    
    # Data Types
    with st.expander("📋 Column Data Types"):
        types_df = pd.DataFrame([
            {'Column': col, 'Data Type': dtype}
            for col, dtype in health['data_types'].items()
        ])
        st.dataframe(types_df, use_container_width=True, hide_index=True)
    
    # Value Ranges
    if health.get('value_ranges'):
        with st.expander("📊 Numeric Column Ranges"):
            ranges_df = pd.DataFrame([
                {
                    'Column': col,
                    'Min': f"{stats['min']:,.2f}" if stats['min'] is not None else 'N/A',
                    'Max': f"{stats['max']:,.2f}" if stats['max'] is not None else 'N/A',
                    'Mean': f"{stats['mean']:,.2f}" if stats['mean'] is not None else 'N/A'
                }
                for col, stats in health['value_ranges'].items()
            ])
            st.dataframe(ranges_df, use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# DATA PREVIEW (UPDATED)
# ==========================================
if st.session_state.data is not None and st.session_state.schema_validated:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.header("📋 Processed Data Preview")
    
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
    
    # Show enriched features if available
    enriched_cols = ['monthly_spend_per_department', 'vendor_transaction_count', 'zscore_amount', 
                     'amount_percentile', 'day_of_week', 'is_weekend']
    
    available_enriched = [col for col in enriched_cols if col in preview_data.columns]
    
    if available_enriched:
        with st.expander("✨ View Enriched Features"):
            st.info(f"**Available Features:** {', '.join(available_enriched)}")
            st.dataframe(preview_data[available_enriched].head(10), use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.raw_uploaded_data is not None and not st.session_state.schema_validated:
    st.info("👆 Please complete data processing above to continue")

# ==========================================
# QUICK ACTIONS (UPDATED)
# ==========================================
if st.session_state.data is not None and st.session_state.schema_validated:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.header("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 Run AI Risk Scan", use_container_width=True, type="primary"):
            st.info("Navigate to 'Anomaly Detection' page to run AI risk scan")
    
    with col2:
        if st.button("📊 View Dashboard", use_container_width=True):
            st.info("Navigate to 'Dashboard' page to view analytics")
    
    with col3:
        if st.button("⚠️ View Alerts", use_container_width=True):
            st.info("Navigate to 'Alerts' page to manage flagged transactions")
    
    with col4:
        if st.button("📄 Export Reports", use_container_width=True):
            st.info("Navigate to 'Reports' page to generate audit reports")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# FOOTER
# ==========================================
st.markdown("""
<div class="footer">
🛡️ AI Fraud Detection System · Hack4Delhi · Verilens Team<br>
Built with Streamlit · Explainable AI · Department-Based Risk Analysis · Persistent Audit Trail · Smart Data Validation · Automated Pipeline · Secure Authentication · Role-Based Access Control · Multi-Tenant Organizations
</div>
""", unsafe_allow_html=True)
