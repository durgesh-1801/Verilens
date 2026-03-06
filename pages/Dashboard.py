"""
Dashboard Page - Executive Analytics
Streamlined view showing key fraud detection metrics and insights
Enhanced with Data Quality monitoring
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# ========== AUDIT ENGINE IMPORT ==========
try:
    from utils.audit_engine import (
        generate_audit_flags,
        summarize_audit_findings,
        filter_by_audit_severity,
        get_flagged_transactions
    )
    AUDIT_ENGINE_AVAILABLE = True
except ImportError:
    AUDIT_ENGINE_AVAILABLE = False
# ========== END AUDIT ENGINE IMPORT ==========

# ========== AUDIT CASE MANAGER IMPORT ==========
try:
    from utils.AuditCaseManager import get_case_summary
    AUDIT_CASE_MANAGER_AVAILABLE = True
except ImportError:
    AUDIT_CASE_MANAGER_AVAILABLE = False
# ========== END AUDIT CASE MANAGER IMPORT ==========

def normalize_flags(flags):
    """Normalize flags to list format"""
    if isinstance(flags, list):
        return flags
    elif isinstance(flags, str):
        return [f.strip() for f in flags.split(";") if f.strip()]
    else:
        return []

# ========== AUTHENTICATION CHECK ==========
if not st.session_state.get('authenticated'):
    st.error("🔒 Access Denied - Please login first")
    
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/1_🔐_Login.py")
    
    st.stop()
# ========== END AUTHENTICATION CHECK ==========

# ========== RBAC CHECK ==========
user_id = st.session_state['user']['id']
user_role = st.session_state['user'].get('role', 'viewer')

# All roles can view dashboard
# ========== END RBAC CHECK ==========

# Page config
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Executive Dashboard")
st.markdown("**Comprehensive fraud detection analytics and insights**")

# ==========================================
# DATA VALIDATION
# ==========================================
if st.session_state.get('data') is None:
    st.warning("⚠️ No data loaded. Please upload data on the Home page.")
    
    if st.button("📁 Go to Data Upload"):
        st.switch_page("app.py")
    
    st.stop()

# Get data and apply department filter
df = st.session_state.data.copy()
selected_department = st.session_state.get('selected_department', 'All Departments')

# Apply department filter
if selected_department != "All Departments":
    if 'department' in df.columns:
        df = df[df['department'] == selected_department]
        st.info(f"🏛️ Viewing data for: **{selected_department}** department")
    else:
        st.warning("Department column not found - showing all data")

if len(df) == 0:
    st.error("No data available for the selected department")
    st.stop()

# ========== AUTO-APPLY AUDIT ENGINE IF NOT APPLIED ==========
if AUDIT_ENGINE_AVAILABLE and 'audit_flags' not in df.columns:
    with st.spinner("🔍 Applying audit intelligence..."):
        df = generate_audit_flags(df)
        st.session_state.data = df
        st.session_state.audit_processed = True
# ========== END AUTO-APPLY AUDIT ENGINE ==========

# ==========================================
# TOP SECTION - KEY PERFORMANCE INDICATORS
# ==========================================
st.markdown("---")
st.subheader("📈 Key Performance Indicators")

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

# KPI 1: Total Transactions
with kpi_col1:
    total_transactions = len(df)
    st.metric(
        label="Total Transactions",
        value=f"{total_transactions:,}",
        delta=f"{selected_department if selected_department != 'All Departments' else 'All Depts'}"
    )

# KPI 2: Total Anomalies (ML)
with kpi_col2:
    total_anomalies = 0
    if 'is_anomaly' in df.columns:
        total_anomalies = (df['is_anomaly'] == -1).sum()
    
    anomaly_rate = (total_anomalies / total_transactions * 100) if total_transactions > 0 else 0
    
    st.metric(
        label="ML Anomalies Detected",
        value=f"{total_anomalies:,}",
        delta=f"{anomaly_rate:.1f}% detection rate",
        delta_color="inverse"
    )

# KPI 3: High Risk Alerts (Audit)
with kpi_col3:
    high_risk_count = 0
    if 'audit_severity' in df.columns:
        high_risk_count = (df['audit_severity'] == 'High').sum()
    
    st.metric(
        label="High Risk Alerts",
        value=f"{high_risk_count:,}",
        delta="Audit Engine",
        delta_color="off"
    )

# KPI 4: Data Quality Score
with kpi_col4:
    avg_quality_score = 0
    quality_status = "Good"
    
    if 'data_quality_score' in df.columns:
        avg_quality_score = df['data_quality_score'].mean()
        
        if avg_quality_score > 50:
            quality_status = "Poor"
        elif avg_quality_score > 20:
            quality_status = "Fair"
        else:
            quality_status = "Good"
    
    # Invert for display (lower score = better quality)
    display_score = 100 - avg_quality_score
    
    st.metric(
        label="Data Quality Score",
        value=f"{display_score:.0f}/100",
        delta=quality_status,
        delta_color="normal" if quality_status == "Good" else "inverse"
    )

# ==========================================
# DATA QUALITY WIDGET (NEW)
# ==========================================
if 'data_quality_score' in df.columns:
    st.markdown("---")
    st.subheader("🔍 Data Quality Assessment")
    
    quality_col1, quality_col2, quality_col3, quality_col4 = st.columns(4)
    
    records_with_issues = (df['data_quality_score'] > 0).sum()
    records_clean = total_transactions - records_with_issues
    issue_rate = (records_with_issues / total_transactions * 100) if total_transactions > 0 else 0
    
    with quality_col1:
        st.metric(
            label="Average Quality Risk",
            value=f"{avg_quality_score:.1f}",
            delta="Lower is better",
            delta_color="inverse"
        )
    
    with quality_col2:
        st.metric(
            label="Records with Issues",
            value=f"{records_with_issues:,}",
            delta=f"{issue_rate:.1f}% of total"
        )
    
    with quality_col3:
        st.metric(
            label="Clean Records",
            value=f"{records_clean:,}",
            delta=f"{100-issue_rate:.1f}% of total"
        )
    
    with quality_col4:
        max_quality_score = df['data_quality_score'].max()
        st.metric(
            label="Highest Risk Score",
            value=f"{max_quality_score:.0f}",
            delta="Needs review" if max_quality_score > 50 else "Acceptable"
        )
    
    # Show common quality issues if available
    if 'data_quality_flags' in df.columns and records_with_issues > 0:
        with st.expander("📋 View Common Data Quality Issues"):
            # Count flag occurrences
            all_flags = []
            for flags in df['data_quality_flags']:
                if isinstance(flags, list):
                    all_flags.extend(flags)
                elif isinstance(flags, str) and flags != 'No issues':
                    all_flags.extend(flags.split('; '))
            
            if all_flags:
                from collections import Counter
                flag_counts = Counter(all_flags)
                
                issue_df = pd.DataFrame([
                    {'Issue': issue, 'Count': count, 'Percentage': f"{count/records_with_issues*100:.1f}%"}
                    for issue, count in flag_counts.most_common(10)
                ])
                
                st.dataframe(issue_df, use_container_width=True, hide_index=True)

# ==========================================
# MIDDLE SECTION - RISK CHARTS
# ==========================================
st.markdown("---")
st.subheader("⚠️ Risk Distribution Analysis")

risk_col1, risk_col2 = st.columns(2)

# Chart 1: Fraud Risk Distribution (ML + Audit Combined)
with risk_col1:
    st.markdown("#### Fraud Risk Distribution")
    
    risk_data = []
    
    # ML Anomaly Detection
    if 'is_anomaly' in df.columns:
        ml_anomalies = (df['is_anomaly'] == -1).sum()
        ml_normal = (df['is_anomaly'] == 1).sum()
        
        risk_data.append({'Category': 'ML: High Risk', 'Count': ml_anomalies, 'Type': 'ML Detection'})
        risk_data.append({'Category': 'ML: Normal', 'Count': ml_normal, 'Type': 'ML Detection'})
    
    # Audit Severity
    if 'audit_severity' in df.columns:
        audit_high = (df['audit_severity'] == 'High').sum()
        audit_medium = (df['audit_severity'] == 'Medium').sum()
        audit_low = (df['audit_severity'] == 'Low').sum()
        
        risk_data.append({'Category': 'Audit: High', 'Count': audit_high, 'Type': 'Audit Rules'})
        risk_data.append({'Category': 'Audit: Medium', 'Count': audit_medium, 'Type': 'Audit Rules'})
        risk_data.append({'Category': 'Audit: Low', 'Count': audit_low, 'Type': 'Audit Rules'})
    
    if risk_data:
        risk_df = pd.DataFrame(risk_data)
        
        fig_risk = px.bar(
            risk_df,
            x='Category',
            y='Count',
            color='Type',
            title='',
            color_discrete_map={
                'ML Detection': '#FF6B6B',
                'Audit Rules': '#4ECDC4'
            },
            text='Count'
        )
        
        fig_risk.update_traces(textposition='outside')
        fig_risk.update_layout(
            showlegend=True,
            height=400,
            xaxis_title="Risk Category",
            yaxis_title="Number of Transactions"
        )
        
        st.plotly_chart(fig_risk, use_container_width=True)
    else:
        st.info("No risk data available")

# Chart 2: Department-wise Anomaly Count
with risk_col2:
    st.markdown("#### Department Risk Analysis")
    
    if 'department' in df.columns:
        # Combine ML and Audit risks
        df_dept = df.copy()
        df_dept['is_risky'] = False
        
        if 'is_anomaly' in df_dept.columns:
            df_dept['is_risky'] = df_dept['is_risky'] | (df_dept['is_anomaly'] == -1)
        
        if 'audit_severity' in df_dept.columns:
            df_dept['is_risky'] = df_dept['is_risky'] | (df_dept['audit_severity'].isin(['High', 'Medium']))
        
        dept_risk = df_dept.groupby('department').agg({
            'is_risky': 'sum',
            'transaction_id': 'count' if 'transaction_id' in df_dept.columns else 'size'
        }).reset_index()
        
        dept_risk.columns = ['Department', 'Risk Count', 'Total']
        dept_risk['Risk %'] = (dept_risk['Risk Count'] / dept_risk['Total'] * 100).round(1)
        dept_risk = dept_risk.sort_values('Risk Count', ascending=False).head(10)
        
        fig_dept = px.bar(
            dept_risk,
            x='Department',
            y='Risk Count',
            title='',
            color='Risk %',
            color_continuous_scale='Reds',
            text='Risk Count'
        )
        
        fig_dept.update_traces(textposition='outside')
        fig_dept.update_layout(
            showlegend=True,
            height=400,
            xaxis_title="Department",
            yaxis_title="Risky Transactions"
        )
        
        st.plotly_chart(fig_dept, use_container_width=True)
    else:
        st.info("Department data not available")

# ==========================================
# BOTTOM SECTION - VENDOR & DEPARTMENT INSIGHTS
# ==========================================
st.markdown("---")
st.subheader("🔎 Vendor & Department Insights")

insight_col1, insight_col2 = st.columns(2)

# Insight 1: Top Risk Vendors
with insight_col1:
    st.markdown("#### Top 10 Risk Vendors")
    
    if 'vendor' in df.columns:
        # Identify risky transactions
        risky_transactions = pd.DataFrame()
        
        # ML-based risk
        if 'is_anomaly' in df.columns:
            ml_risky = df[df['is_anomaly'] == -1]
            risky_transactions = pd.concat([risky_transactions, ml_risky])
        
        # Audit-based risk
        if 'audit_severity' in df.columns:
            audit_risky = df[df['audit_severity'].isin(['High', 'Medium'])]
            risky_transactions = pd.concat([risky_transactions, audit_risky])
        
        # Remove duplicates
        risky_transactions = risky_transactions.drop_duplicates()
        
        if len(risky_transactions) > 0:
            # Group by vendor
            vendor_risk = risky_transactions.groupby('vendor').agg({
                'vendor': 'size',
                'amount': 'sum' if 'amount' in risky_transactions.columns else 'size'
            }).reset_index(drop=True)
            
            if 'amount' in risky_transactions.columns:
                vendor_risk = risky_transactions.groupby('vendor').agg({
                    'vendor': 'size',
                    'amount': 'sum'
                })
                vendor_risk.columns = ['Risk Transactions', 'Total Amount']
            else:
                vendor_risk = risky_transactions.groupby('vendor').size().to_frame()
                vendor_risk.columns = ['Risk Transactions']
            
            vendor_risk = vendor_risk.reset_index()
            vendor_risk = vendor_risk.sort_values('Risk Transactions', ascending=False).head(10)
            
            # Create visualization
            fig_vendor = go.Figure()
            
            fig_vendor.add_trace(go.Bar(
                x=vendor_risk['vendor'],
                y=vendor_risk['Risk Transactions'],
                name='Risk Transactions',
                marker_color='#FF6B6B',
                text=vendor_risk['Risk Transactions'],
                textposition='outside'
            ))
            
            fig_vendor.update_layout(
                height=400,
                xaxis_title="Vendor",
                yaxis_title="Number of Risky Transactions",
                showlegend=False
            )
            
            st.plotly_chart(fig_vendor, use_container_width=True)
            
            # Show table
            if 'Total Amount' in vendor_risk.columns:
                vendor_risk['Total Amount'] = vendor_risk['Total Amount'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(vendor_risk, use_container_width=True, hide_index=True)
        else:
            st.info("No risky vendors detected")
    else:
        st.info("Vendor data not available")

# Insight 2: Department Summary Table
with insight_col2:
    st.markdown("#### Department Summary")
    
    if 'department' in df.columns:
        dept_summary = df.groupby('department').agg({
            'department': 'size',
            'amount': ['sum', 'mean'] if 'amount' in df.columns else 'size'
        }).reset_index()
        
        if 'amount' in df.columns:
            dept_summary.columns = ['Department', 'Total Transactions', 'Total Amount', 'Avg Amount']
        else:
            dept_summary.columns = ['Department', 'Total Transactions']
        
        # Add risk counts
        dept_summary['High Risk'] = 0
        dept_summary['Medium Risk'] = 0
        
        if 'audit_severity' in df.columns:
            for idx, row in dept_summary.iterrows():
                dept = row['Department']
                dept_df = df[df['department'] == dept]
                
                high = (dept_df['audit_severity'] == 'High').sum()
                medium = (dept_df['audit_severity'] == 'Medium').sum()
                
                dept_summary.at[idx, 'High Risk'] = high
                dept_summary.at[idx, 'Medium Risk'] = medium
        
        if 'Total Amount' in dept_summary.columns:
            dept_summary = dept_summary.sort_values('Total Amount', ascending=False)
            # Format amounts
            dept_summary['Total Amount'] = dept_summary['Total Amount'].apply(lambda x: f"${x:,.2f}")
            dept_summary['Avg Amount'] = dept_summary['Avg Amount'].apply(lambda x: f"${x:,.2f}")
        else:
            dept_summary = dept_summary.sort_values('Total Transactions', ascending=False)
        
        st.dataframe(
            dept_summary,
            use_container_width=True,
            hide_index=True,
            height=400
        )
    else:
        st.info("Department data not available")

# ==========================================
# AUDIT CASE SUMMARY (IF AVAILABLE)
# ==========================================
if AUDIT_CASE_MANAGER_AVAILABLE and 'audit_case_id' in df.columns:
    st.markdown("---")
    st.subheader("📋 Audit Case Management Summary")
    
    case_summary = get_case_summary(df)
    
    case_col1, case_col2, case_col3, case_col4, case_col5 = st.columns(5)
    
    with case_col1:
        st.metric("Total Cases", f"{case_summary['total_cases']:,}")
    
    with case_col2:
        st.metric(
            "🟡 Open Cases",
            f"{case_summary['open_cases']:,}",
            delta="Needs Assignment"
        )
    
    with case_col3:
        st.metric(
            "🔵 Under Review",
            f"{case_summary['under_review']:,}",
            delta="In Progress"
        )
    
    with case_col4:
        st.metric(
            "🔴 Escalated",
            f"{case_summary['escalated']:,}",
            delta="High Priority",
            delta_color="inverse"
        )
    
    with case_col5:
        st.metric(
            "🟢 Closed Cases",
            f"{case_summary['closed_cases']:,}",
            delta="Resolved"
        )
    
    # Case completion rate
    if case_summary['total_cases'] > 0:
        completion_rate = (case_summary['closed_cases'] / case_summary['total_cases']) * 100
        st.progress(completion_rate / 100)
        st.caption(f"**Case Resolution Rate:** {completion_rate:.1f}% ({case_summary['closed_cases']} / {case_summary['total_cases']} cases resolved)")

# ==========================================
# QUICK ACTIONS
# ==========================================
st.markdown("---")
st.subheader("⚡ Quick Actions")

action_col1, action_col2, action_col3, action_col4 = st.columns(4)

with action_col1:
    if st.button("🔍 Run AI Detection", use_container_width=True, type="primary"):
        st.switch_page("pages/3_🤖_Anomaly_Detection.py")

with action_col2:
    if st.button("⚠️ View Alerts", use_container_width=True):
        st.switch_page("pages/4_⚠️_Alerts.py")

with action_col3:
    if st.button("📄 Generate Report", use_container_width=True):
        st.switch_page("pages/5_📄_Reports.py")

with action_col4:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.caption(f"**Dashboard last updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **User:** {st.session_state['user']['username']} ({user_role.upper()})")
