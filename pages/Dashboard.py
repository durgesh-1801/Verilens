"""
Dashboard Page
Real-time analytics and visualizations with Audit Intelligence
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from scipy import stats
import sys
from pathlib import Path

# ========== AUDIT ENGINE IMPORT ==========
sys.path.insert(0, str(Path(__file__).parent.parent))
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
    print("Warning: Audit engine not available")
# ========== END AUDIT ENGINE IMPORT ==========

def normalize_flags(flags):
    if isinstance(flags, list):
        return flags
    elif isinstance(flags, str):
        return [f.strip() for f in flags.split(";") if f.strip()]
    else:
        return []

# Authentication check
if not st.session_state.get('authenticated'):
    st.error("🔒 Access Denied - Please login first")
    
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/_Login.py")
    
    st.stop()
# ========== END AUTHENTICATION CHECK ==========

# ========== RBAC CHECK ==========
user_id = st.session_state['user']['id']
user_role = st.session_state['user'].get('role', 'viewer')

# All roles can view dashboard (data is already filtered by RBAC in database)
# ========== END RBAC CHECK ==========

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Fraud Detection Dashboard")

# ==========================================
# DEPARTMENT FILTER
# ==========================================
selected_department = st.session_state.get('selected_department', 'All Departments')

# Check if data exists
if st.session_state.get('data') is None:
    st.warning("⚠️ Please upload data on the home page first!")
    st.stop()

df = st.session_state.data.copy()

# ========== NEW: APPLY AUDIT ENGINE IF NOT ALREADY APPLIED ==========
if AUDIT_ENGINE_AVAILABLE and 'audit_flags' not in df.columns:
    with st.spinner("🔍 Applying audit intelligence..."):
        try:
            df = generate_audit_flags(df)
            st.session_state.data = df  # Update session state
            st.session_state.audit_processed = True
            st.success("✓ Audit rules applied to data")
        except Exception as e:
            st.warning(f"Audit engine could not be applied: {e}")
            AUDIT_ENGINE_AVAILABLE = False
# ========== END AUDIT ENGINE APPLICATION ==========

# ==========================================
# APPLY DEPARTMENT FILTER
# ==========================================
original_total = len(df)
if selected_department != "All Departments":
    if 'department' in df.columns:
        df = df[df['department'] == selected_department].copy()
        st.info(f"🏛️ Dashboard: **{selected_department}** Department - Showing {len(df)} of {original_total} total transactions")
    else:
        st.warning("⚠️ Department column not found. Showing all departments.")
else:
    st.info(f"🏛️ Dashboard: **All Departments** - Global Overview")

# ========== ADDITION 1: QUICK FILTERS (ENHANCED WITH AUDIT SEVERITY) ==========
st.markdown("---")
st.subheader("🔍 Analytics Filters")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    # Risk level filter - now includes audit severity if available
    if AUDIT_ENGINE_AVAILABLE and 'audit_severity' in df.columns:
        risk_filter_options = ["All", "Audit: High Risk", "Audit: Medium Risk", "Audit: Low Risk", "ML: High-Risk", "ML: Medium-Risk", "ML: Normal"]
    else:
        risk_filter_options = ["All", "High-Risk", "Medium-Risk", "Normal"]
    
    selected_risk_filter = st.selectbox(
        "Filter by Risk Level",
        risk_filter_options,
        key="analytics_risk_filter"
    )

with filter_col2:
    # Date range filter (if date column exists)
    date_cols = df.select_dtypes(include=['datetime64', 'object']).columns
    date_col = None
    
    for col in date_cols:
        try:
            pd.to_datetime(df[col])
            date_col = col
            break
        except:
            continue
    
    if date_col:
        df_temp = df.copy()
        df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
        df_temp = df_temp.dropna(subset=[date_col])
        
        if len(df_temp) > 0:
            min_date = df_temp[date_col].min().date()
            max_date = df_temp[date_col].max().date()
            
            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="analytics_date_filter"
            )
        else:
            date_range = None
    else:
        date_range = None
        st.info("No date column available")

with filter_col3:
    st.markdown("**Active Filters:**")
    if selected_risk_filter != "All":
        st.markdown(f"🔴 Risk: {selected_risk_filter}")
    if date_range and len(date_range) == 2:
        st.markdown(f"📅 {date_range[0]} to {date_range[1]}")

# Apply filters to dataframe
filtered_analytics_df = df.copy()

# Apply risk filter
if selected_risk_filter != "All":
    if selected_risk_filter.startswith("Audit:") and AUDIT_ENGINE_AVAILABLE and 'audit_severity' in filtered_analytics_df.columns:
        # Audit engine filter
        if "High Risk" in selected_risk_filter:
            filtered_analytics_df = filter_by_audit_severity(filtered_analytics_df, "High")
        elif "Medium Risk" in selected_risk_filter:
            filtered_analytics_df = filter_by_audit_severity(filtered_analytics_df, "Medium")
        elif "Low Risk" in selected_risk_filter:
            filtered_analytics_df = filter_by_audit_severity(filtered_analytics_df, "Low")
    elif 'is_anomaly' in filtered_analytics_df.columns:
        # ML-based filter
        if selected_risk_filter == "High-Risk" or selected_risk_filter == "ML: High-Risk":
            if 'anomaly_score' in filtered_analytics_df.columns:
                filtered_analytics_df = filtered_analytics_df[
                    (filtered_analytics_df['is_anomaly'] == -1) & 
                    (filtered_analytics_df['anomaly_score'] > 0.8)
                ]
            else:
                filtered_analytics_df = filtered_analytics_df[filtered_analytics_df['is_anomaly'] == -1]
        elif selected_risk_filter == "Medium-Risk" or selected_risk_filter == "ML: Medium-Risk":
            if 'anomaly_score' in filtered_analytics_df.columns:
                filtered_analytics_df = filtered_analytics_df[
                    (filtered_analytics_df['is_anomaly'] == -1) & 
                    (filtered_analytics_df['anomaly_score'] > 0.5) & 
                    (filtered_analytics_df['anomaly_score'] <= 0.8)
                ]
            else:
                filtered_analytics_df = filtered_analytics_df[filtered_analytics_df['is_anomaly'] == -1]
        elif selected_risk_filter == "Normal" or selected_risk_filter == "ML: Normal":
            filtered_analytics_df = filtered_analytics_df[filtered_analytics_df['is_anomaly'] == 1]

# Apply date filter
if date_range and len(date_range) == 2 and date_col:
    filtered_analytics_df[date_col] = pd.to_datetime(filtered_analytics_df[date_col], errors='coerce')
    filtered_analytics_df = filtered_analytics_df[
        (filtered_analytics_df[date_col].dt.date >= date_range[0]) &
        (filtered_analytics_df[date_col].dt.date <= date_range[1])
    ]

st.info(f"📊 Analytics showing {len(filtered_analytics_df)} transactions after filters")
# ========== END ADDITION 1 ==========

st.markdown("---")

# ========== ADDITION 2: AUDIT INTELLIGENCE SUMMARY (NEW) ==========
if AUDIT_ENGINE_AVAILABLE and 'audit_severity' in filtered_analytics_df.columns:
    st.subheader("🔍 Audit Intelligence Summary")
    
    audit_summary = summarize_audit_findings(filtered_analytics_df)
    
    audit_col1, audit_col2, audit_col3, audit_col4 = st.columns(4)
    
    with audit_col1:
        st.metric(
            "Total Flagged",
            f"{audit_summary['total_flagged']:,}",
            delta=f"{audit_summary['total_flagged']/len(filtered_analytics_df)*100:.1f}%" if len(filtered_analytics_df) > 0 else "0%"
        )
    
    with audit_col2:
        st.metric(
            "🔴 High Risk (Audit)",
            f"{audit_summary['high_risk_count']:,}",
            delta="Requires immediate review",
            delta_color="inverse"
        )
    
    with audit_col3:
        st.metric(
            "🟡 Medium Risk (Audit)",
            f"{audit_summary['medium_risk_count']:,}",
            delta="Further investigation"
        )
    
    with audit_col4:
        st.metric(
            "🟢 Low Risk (Audit)",
            f"{audit_summary['low_risk_count']:,}",
            delta="Monitor"
        )
    
    # Show audit rules breakdown
    if audit_summary['total_flagged'] > 0:
        with st.expander("📋 View Audit Flags Breakdown"):
            flagged_df = get_flagged_transactions(filtered_analytics_df, min_flags=1)
            
            if len(flagged_df) > 0:
                # Count each flag type
                all_flags = []

                for flags_list in flagged_df['audit_flags']:
                    normalized = normalize_flags(flags_list)
                    all_flags.extend(normalized)
                flag_counts = pd.Series(all_flags).value_counts()
                
                # Display flag counts
                st.markdown("**Most Common Audit Flags:**")
                for flag, count in flag_counts.items():
                    st.markdown(f"- **{flag}**: {count} occurrences")
                
                # Show sample flagged transactions
                st.markdown("**Sample Flagged Transactions:**")
                display_cols = ['transaction_id', 'amount', 'vendor', 'audit_risk_score', 'audit_severity', 'audit_flags']
                available_display_cols = [col for col in display_cols if col in flagged_df.columns]
                st.dataframe(flagged_df[available_display_cols].head(10), use_container_width=True)
    
    st.markdown("---")
# ========== END AUDIT INTELLIGENCE SUMMARY ==========

# ========== NEW: AUDIT CASE METRICS ==========
if AUDIT_ENGINE_AVAILABLE and st.session_state.get('data') is not None:
    df = st.session_state.data
    
    if 'audit_case_id' in df.columns:
        from utils.AuditCaseManager import get_case_summary
        
        st.markdown("---")
        st.subheader("📋 Audit Case Management")
        
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
            st.caption(f"**Case Completion Rate:** {completion_rate:.1f}% ({case_summary['closed_cases']} / {case_summary['total_cases']} cases resolved)")
        
        st.markdown("---")
# ========== END AUDIT CASE METRICS ==========

# ========== ADDITION 2 (ORIGINAL): DEPARTMENT RISK SUMMARY PANEL ==========
st.subheader("🎯 Department Risk Summary")

risk_summary_col1, risk_summary_col2, risk_summary_col3, risk_summary_col4 = st.columns(4)

# Calculate risk counts
total_txns = len(filtered_analytics_df)

if 'is_anomaly' in filtered_analytics_df.columns and 'anomaly_score' in filtered_analytics_df.columns:
    high_risk = len(filtered_analytics_df[
        (filtered_analytics_df['is_anomaly'] == -1) & 
        (filtered_analytics_df['anomaly_score'] > 0.8)
    ])
    medium_risk = len(filtered_analytics_df[
        (filtered_analytics_df['is_anomaly'] == -1) & 
        (filtered_analytics_df['anomaly_score'] > 0.5) & 
        (filtered_analytics_df['anomaly_score'] <= 0.8)
    ])
    normal = len(filtered_analytics_df[filtered_analytics_df['is_anomaly'] == 1])
elif 'is_anomaly' in filtered_analytics_df.columns:
    # Fallback if no anomaly_score
    all_anomalies = len(filtered_analytics_df[filtered_analytics_df['is_anomaly'] == -1])
    high_risk = int(all_anomalies * 0.4)  # Estimate
    medium_risk = all_anomalies - high_risk
    normal = len(filtered_analytics_df[filtered_analytics_df['is_anomaly'] == 1])
else:
    high_risk = 0
    medium_risk = 0
    normal = total_txns

with risk_summary_col1:
    st.metric(
        "Total Transactions",
        f"{total_txns:,}",
        delta=f"{selected_department}"
    )

with risk_summary_col2:
    high_pct = (high_risk / total_txns * 100) if total_txns > 0 else 0
    st.metric(
        "🔴 High Risk (ML)",
        f"{high_risk:,}",
        delta=f"{high_pct:.1f}% flagged",
        delta_color="inverse"
    )

with risk_summary_col3:
    medium_pct = (medium_risk / total_txns * 100) if total_txns > 0 else 0
    st.metric(
        "🟠 Medium Risk (ML)",
        f"{medium_risk:,}",
        delta=f"{medium_pct:.1f}% flagged",
        delta_color="inverse"
    )

with risk_summary_col4:
    normal_pct = (normal / total_txns * 100) if total_txns > 0 else 0
    st.metric(
        "🟢 Normal (ML)",
        f"{normal:,}",
        delta=f"{normal_pct:.1f}% clean"
    )

# Overall flagged percentage
total_flagged = high_risk + medium_risk
total_flagged_pct = (total_flagged / total_txns * 100) if total_txns > 0 else 0

st.progress(total_flagged_pct / 100)
st.caption(f"**Overall ML Risk Rate:** {total_flagged_pct:.2f}% of transactions flagged ({total_flagged:,} / {total_txns:,})")
# ========== END ADDITION 2 ==========

st.markdown("---")

# ========== ADDITION 3: RISK TREND OVER TIME ==========
st.subheader("📈 Risk Trend Over Time")

if date_col and 'is_anomaly' in filtered_analytics_df.columns and len(filtered_analytics_df) > 0:
    trend_df = filtered_analytics_df.copy()
    trend_df[date_col] = pd.to_datetime(trend_df[date_col], errors='coerce')
    trend_df = trend_df.dropna(subset=[date_col])
    
    if len(trend_df) > 0:
        # Determine grouping (daily vs monthly based on date range)
        date_range_days = (trend_df[date_col].max() - trend_df[date_col].min()).days
        
        if date_range_days > 90:
            # Monthly grouping
            trend_df['period'] = trend_df[date_col].dt.to_period('M').astype(str)
            period_label = "Month"
        else:
            # Daily grouping
            trend_df['period'] = trend_df[date_col].dt.date.astype(str)
            period_label = "Date"
        
        # Count high and medium risk by period
        if 'anomaly_score' in trend_df.columns:
            risk_only = trend_df[trend_df['is_anomaly'] == -1]

            risk_trend = (
                risk_only.groupby('period')
                .agg(
                    High_Risk=('anomaly_score', lambda x: (x > 0.8).sum()),
                    Medium_Risk=('anomaly_score', lambda x: ((x > 0.5) & (x <= 0.8)).sum()),
                    Total_Risk=('anomaly_score', 'count')
                )
                .reset_index()
            )

            risk_trend = risk_trend.rename(columns={
                'High_Risk': 'High Risk',
                'Medium_Risk': 'Medium Risk',
                'Total_Risk': 'Total Risk'
            })

        else:
            risk_trend = trend_df[trend_df['is_anomaly'] == -1].groupby('period').size().reset_index(name='Total Risk')
            risk_trend['High Risk'] = risk_trend['Total Risk'] * 0.4
            risk_trend['Medium Risk'] = risk_trend['Total Risk'] * 0.6
        
        # Create stacked bar chart
        fig = go.Figure()
        
        if 'High Risk' in risk_trend.columns:
            fig.add_trace(go.Bar(
                x=risk_trend['period'],
                y=risk_trend['High Risk'],
                name='High Risk',
                marker_color='#ef553b'
            ))
        
        if 'Medium Risk' in risk_trend.columns:
            fig.add_trace(go.Bar(
                x=risk_trend['period'],
                y=risk_trend['Medium Risk'],
                name='Medium Risk',
                marker_color='#ffa15a'
            ))
        
        fig.update_layout(
            title=f"Risk Transactions Trend - {selected_department}",
            xaxis_title=period_label,
            yaxis_title="Number of Risky Transactions",
            barmode='stack',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show trend summary
        if len(risk_trend) >= 2:
            recent_period = risk_trend.iloc[-1]['Total Risk']
            previous_period = risk_trend.iloc[-2]['Total Risk']
            trend_change = ((recent_period - previous_period) / previous_period * 100) if previous_period > 0 else 0
            
            trend_col1, trend_col2, trend_col3 = st.columns(3)
            with trend_col1:
                st.metric("Latest Period Risk Count", f"{int(recent_period):,}")
            with trend_col2:
                st.metric("Previous Period", f"{int(previous_period):,}", delta=f"{trend_change:+.1f}%", delta_color="inverse")
            with trend_col3:
                avg_risk = risk_trend['Total Risk'].mean()
                st.metric("Average per Period", f"{avg_risk:.1f}")
    else:
        st.info("No date data available after filtering")
else:
    st.info("Risk trend requires date column and anomaly detection to be run")
# ========== END ADDITION 3 ==========

st.markdown("---")

# ========== ADDITION 4: TOP RISK VENDORS TABLE (ENHANCED WITH AUDIT) ==========
st.subheader("🏢 Top Risk Vendors")

if 'vendor' in filtered_analytics_df.columns and len(filtered_analytics_df) > 0:
    # Get risky transactions from both ML and Audit
    risky_df = filtered_analytics_df.copy()
    
    # Filter for risky transactions
    if 'is_anomaly' in risky_df.columns:
        ml_risky = risky_df[risky_df['is_anomaly'] == -1]
    else:
        ml_risky = pd.DataFrame()
    
    if AUDIT_ENGINE_AVAILABLE and 'audit_severity' in risky_df.columns:
        audit_risky = risky_df[risky_df['audit_severity'].isin(['High', 'Medium'])]
    else:
        audit_risky = pd.DataFrame()
    
    # Combine ML and Audit risk (union)
    if len(ml_risky) > 0 and len(audit_risky) > 0:
        risky_df = pd.concat([ml_risky, audit_risky]).drop_duplicates(subset=['transaction_id'] if 'transaction_id' in risky_df.columns else None)
    elif len(ml_risky) > 0:
        risky_df = ml_risky
    elif len(audit_risky) > 0:
        risky_df = audit_risky
    else:
        risky_df = pd.DataFrame()
    
    if len(risky_df) > 0 and 'amount' in risky_df.columns:
        # Group by vendor
        vendor_risk = risky_df.groupby('vendor').agg({
            'vendor': 'count',
            'amount': 'sum'
        }).rename(columns={'vendor': 'risk_count', 'amount': 'total_risky_amount'})
        
        # Add high risk count if score available
        if 'anomaly_score' in risky_df.columns:
            high_risk_counts = risky_df[risky_df['anomaly_score'] > 0.8].groupby('vendor').size()
            vendor_risk['high_risk_count'] = high_risk_counts
            vendor_risk['high_risk_count'] = vendor_risk['high_risk_count'].fillna(0).astype(int)
        
        # Add audit high risk count
        if AUDIT_ENGINE_AVAILABLE and 'audit_severity' in risky_df.columns:
            audit_high_counts = risky_df[risky_df['audit_severity'] == 'High'].groupby('vendor').size()
            vendor_risk['audit_high_count'] = audit_high_counts
            vendor_risk['audit_high_count'] = vendor_risk['audit_high_count'].fillna(0).astype(int)
        
        # Sort by risk count
        vendor_risk = vendor_risk.sort_values('risk_count', ascending=False).head(10)
        vendor_risk = vendor_risk.reset_index()
        
        # Format the table
        vendor_risk['total_risky_amount'] = vendor_risk['total_risky_amount'].apply(lambda x: f"${x:,.2f}")
        
        # Display columns
        display_cols = ['vendor', 'risk_count', 'total_risky_amount']
        col_names = ['Vendor Name', 'Risk Transaction Count', 'Total Risky Amount']
        
        if 'high_risk_count' in vendor_risk.columns:
            display_cols.insert(2, 'high_risk_count')
            col_names.insert(2, 'ML High Severity')
        
        if 'audit_high_count' in vendor_risk.columns:
            display_cols.insert(3, 'audit_high_count')
            col_names.insert(3, 'Audit High Severity')
        
        vendor_risk_display = vendor_risk[display_cols].copy()
        vendor_risk_display.columns = col_names
        
        # Display with styling
        st.dataframe(
            vendor_risk_display,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv_data = vendor_risk_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Top Risk Vendors",
            data=csv_data,
            file_name=f"top_risk_vendors_{selected_department.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )
        
        # Visual representation
        st.markdown("#### Risk Distribution by Vendor")
        
        fig = go.Figure(data=[
            go.Bar(
                y=vendor_risk['vendor'].head(10),
                x=vendor_risk['risk_count'].head(10),
                orientation='h',
                marker_color='#ef553b',
                text=vendor_risk['risk_count'].head(10),
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Top 10 Vendors by Risk Transaction Count",
            xaxis_title="Number of Risky Transactions",
            yaxis_title="Vendor",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    elif len(risky_df) > 0:
        # No amount column, just show count
        vendor_risk = risky_df['vendor'].value_counts().head(10).reset_index()
        vendor_risk.columns = ['Vendor Name', 'Risk Transaction Count']
        
        st.dataframe(vendor_risk, use_container_width=True, hide_index=True)
    else:
        st.info("No risky transactions found for vendor analysis")
else:
    st.info("Vendor risk analysis requires vendor column")
# ========== END ADDITION 4 ==========

st.markdown("---")

# ==========================================
# DEPARTMENT-SPECIFIC METRICS
# ==========================================
if selected_department != "All Departments" and 'department' in st.session_state.data.columns:
    st.markdown("### 🏛️ Department Overview")
    
    dept_col1, dept_col2, dept_col3, dept_col4 = st.columns(4)
    
    all_data = st.session_state.data
    dept_data = df
    
    with dept_col1:
        st.metric(
            "Department Transactions",
            f"{len(dept_data):,}",
            delta=f"{len(dept_data)/len(all_data)*100:.1f}% of total"
        )
    
    with dept_col2:
        if 'amount' in dept_data.columns:
            dept_total = dept_data['amount'].sum()
            overall_total = all_data['amount'].sum()
            st.metric(
                "Department Spend",
                f"${dept_total:,.2f}",
                delta=f"{dept_total/overall_total*100:.1f}% of total"
            )
    
    with dept_col3:
        dept_anomalies = len(dept_data[dept_data.get('is_anomaly', pd.Series([-1]*len(dept_data))) == -1]) if 'is_anomaly' in dept_data.columns else 0
        st.metric(
            "Dept High-Risk",
            f"{dept_anomalies:,}",
            delta=f"{dept_anomalies/len(dept_data)*100:.1f}% flagged" if len(dept_data) > 0 else "0%",
            delta_color="inverse"
        )
    
    with dept_col4:
        if 'amount' in dept_data.columns:
            st.metric(
                "Avg Transaction",
                f"${dept_data['amount'].mean():,.2f}"
            )
    
    st.markdown("---")

# Top metrics row
st.subheader("📈 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

# Calculate metrics
total_records = len(df)
numeric_cols = df.select_dtypes(include=[np.number]).columns

if 'amount' in df.columns:
    total_amount = df['amount'].sum()
    avg_amount = df['amount'].mean()
else:
    total_amount = 0
    avg_amount = 0

# Display metrics
with col1:
    st.metric(
        label="Total Transactions",
        value=f"{total_records:,}",
        delta="Live Data"
    )

with col2:
    st.metric(
        label="Total Amount",
        value=f"${total_amount:,.2f}" if total_amount else "N/A",
        delta=None
    )

with col3:
    # Count anomalies in filtered data
    if 'is_anomaly' in df.columns:
        anomaly_count = len(df[df['is_anomaly'] == -1])
    else:
        anomaly_count = 0
    
    st.metric(
        label="High-Risk Flagged",
        value=f"{anomaly_count:,}",
        delta=f"{(anomaly_count/total_records*100):.1f}%" if total_records > 0 else "0%",
        delta_color="inverse"
    )

with col4:
    # Count high severity alerts in filtered department
    alerts = st.session_state.get('alerts', [])
    if selected_department != "All Departments":
        dept_alerts = [a for a in alerts if a.get('department') == selected_department and a.get('severity') == 'high']
    else:
        dept_alerts = [a for a in alerts if a.get('severity') == 'high']
    
    st.metric(
        label="High Priority Alerts",
        value=len(dept_alerts),
        delta="Needs Review",
        delta_color="inverse"
    )

with col5:
    st.metric(
        label="Data Quality Score",
        value=f"{(1 - df.isnull().sum().sum() / df.size) * 100:.1f}%" if df.size > 0 else "N/A",
        delta="Good" if df.size > 0 and (1 - df.isnull().sum().sum() / df.size) > 0.9 else "Check Data"
    )

st.markdown("---")

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Transaction Amount Distribution")
    if 'amount' in df.columns and len(df) > 0:
        fig = px.histogram(
            df, 
            x='amount', 
            nbins=50,
            title=f"Amount Distribution - {selected_department}",
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(
            xaxis_title="Amount ($)",
            yaxis_title="Frequency",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Use first numeric column
        if len(numeric_cols) > 0 and len(df) > 0:
            fig = px.histogram(
                df, 
                x=numeric_cols[0], 
                nbins=50,
                color_discrete_sequence=['#667eea']
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for visualization")

with col2:
    st.subheader("🔵 Transaction Risk Status")
    if 'is_anomaly' in df.columns and len(df) > 0:
        anomaly_counts = df['is_anomaly'].value_counts()
        labels = ['Normal', 'High-Risk']
        values = [
            anomaly_counts.get(1, 0) + anomaly_counts.get(False, 0),
            anomaly_counts.get(-1, 0) + anomaly_counts.get(True, 0)
        ]
    else:
        labels = ['Pending AI Scan']
        values = [total_records] if total_records > 0 else [0]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker_colors=['#00cc96', '#ef553b']
    )])
    fig.update_layout(
        title=f"Risk Status - {selected_department}",
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Transaction Trend Analysis")
    
    # Check for date column
    date_cols = df.select_dtypes(include=['datetime64', 'object']).columns
    date_col_temp = None
    
    for col in date_cols:
        try:
            pd.to_datetime(df[col])
            date_col_temp = col
            break
        except:
            continue
    
    if date_col_temp and 'amount' in df.columns and len(df) > 0:
        temp_df = df.copy()
        temp_df[date_col_temp] = pd.to_datetime(temp_df[date_col_temp], errors='coerce')
        temp_df = temp_df.dropna(subset=[date_col_temp])
        
        if len(temp_df) > 0:
            trend_data = temp_df.groupby(temp_df[date_col_temp].dt.date)['amount'].agg(['sum', 'count']).reset_index()
            trend_data.columns = ['date', 'amount', 'count']
            
            fig = px.line(
                trend_data,
                x='date',
                y='amount',
                title=f"Daily Transaction Trend - {selected_department}",
                color_discrete_sequence=['#667eea']
            )
            fig.update_traces(mode='lines+markers')
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Total Amount ($)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No valid date data for trend analysis")
    else:
        st.info("Add date column for trend analysis")

with col2:
    st.subheader("🎯 Feature Correlation Matrix")
    if len(numeric_cols) >= 2 and len(df) > 0:
        corr_matrix = df[numeric_cols].corr()
        fig = px.imshow(
            corr_matrix,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu",
            title="Feature Correlation Heatmap"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need at least 2 numeric columns for correlation analysis")

# ==========================================
# DEPARTMENT COMPARISON
# ==========================================
if selected_department == "All Departments" and 'department' in st.session_state.data.columns:
    st.markdown("---")
    st.subheader("🏛️ Department Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Department spending comparison
        if 'amount' in st.session_state.data.columns:
            dept_spending = st.session_state.data.groupby('department')['amount'].sum().sort_values(ascending=False)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=dept_spending.index,
                    y=dept_spending.values,
                    marker_color='#667eea'
                )
            ])
            fig.update_layout(
                title="Total Spending by Department",
                xaxis_title="Department",
                yaxis_title="Total Amount ($)",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Department risk comparison
        if 'is_anomaly' in st.session_state.data.columns:
            dept_risk = st.session_state.data.groupby('department').apply(
                lambda x: len(x[x['is_anomaly'] == -1])
            ).sort_values(ascending=False)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=dept_risk.index,
                    y=dept_risk.values,
                    marker_color='#ef553b'
                )
            ])
            fig.update_layout(
                title="High-Risk Transactions by Department",
                xaxis_title="Department",
                yaxis_title="Number of High-Risk Flags",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

# Risk Distribution
st.markdown("---")
st.subheader("⚠️ Risk Level Distribution")

if len(numeric_cols) > 0 and len(df) > 0:
    # Create risk scores based on z-scores
    risk_col = numeric_cols[0] if 'amount' not in df.columns else 'amount'
    
    # Handle missing values
    risk_data = df[risk_col].fillna(df[risk_col].median())
    
    if len(risk_data) > 0 and risk_data.std() > 0:
        z_scores = np.abs(stats.zscore(risk_data))
        
        risk_levels = pd.cut(
            z_scores,
            bins=[-np.inf, 1, 2, 3, np.inf],
            labels=['Low', 'Medium', 'High', 'Critical']
        )
        
        risk_counts = risk_levels.value_counts()
        
        fig = go.Figure(data=[
            go.Bar(
                x=risk_counts.index.tolist(),
                y=risk_counts.values,
                marker_color=['#00cc96', '#ffa15a', '#ef553b', '#ab63fa'],
                text=risk_counts.values,
                textposition='auto'
            )
        ])
        fig.update_layout(
            title=f"Risk Level Distribution - {selected_department}",
            xaxis_title="Risk Level",
            yaxis_title="Count",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient data variance for risk distribution analysis")
else:
    st.info("No data available for risk distribution")

# ==========================================
# VENDOR ANALYSIS
# ==========================================
if 'vendor' in df.columns and len(df) > 0:
    st.markdown("---")
    st.subheader("🏢 Vendor Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top vendors by transaction count
        vendor_counts = df['vendor'].value_counts().head(10)
        
        fig = go.Figure(data=[
            go.Bar(
                y=vendor_counts.index,
                x=vendor_counts.values,
                orientation='h',
                marker_color='#667eea'
            )
        ])
        fig.update_layout(
            title="Top 10 Vendors by Transaction Count",
            xaxis_title="Number of Transactions",
            yaxis_title="Vendor",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # High-risk vendors
        if 'is_anomaly' in df.columns:
            vendor_risk = df[df['is_anomaly'] == -1]['vendor'].value_counts().head(10)
            
            fig = go.Figure(data=[
                go.Bar(
                    y=vendor_risk.index,
                    x=vendor_risk.values,
                    orientation='h',
                    marker_color='#ef553b'
                )
            ])
            fig.update_layout(
                title="Top 10 Vendors with High-Risk Flags",
                xaxis_title="Number of High-Risk Transactions",
                yaxis_title="Vendor",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

# Data Table with Filtering
st.markdown("---")
st.subheader("📋 Transaction Data Explorer")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    if 'amount' in df.columns and len(df) > 0:
        amount_min = float(df['amount'].min())
        amount_max = float(df['amount'].max())
        amount_filter = st.slider(
            "Amount Range",
            amount_min,
            amount_max,
            (amount_min, amount_max)
        )
    else:
        amount_filter = None

with col2:
    if 'vendor' in df.columns and len(df) > 0:
        vendors = (
    df['vendor']
    .dropna()
    .astype(str)
    .str.strip()
    )

        vendors = ['All'] + sorted(vendors[vendors != ""].unique())
        selected_vendor = st.selectbox("Vendor", vendors)
    else:
        selected_vendor = 'All'

with col3:
    show_anomalies_only = st.checkbox("Show High-Risk Only")

# Apply filters
filtered_df = df.copy()

if amount_filter and 'amount' in df.columns:
    filtered_df = filtered_df[
        (filtered_df['amount'] >= amount_filter[0]) & 
        (filtered_df['amount'] <= amount_filter[1])
    ]

if selected_vendor != 'All' and 'vendor' in df.columns:
    filtered_df = filtered_df[filtered_df['vendor'] == selected_vendor]

if show_anomalies_only and 'is_anomaly' in df.columns:
    filtered_df = filtered_df[filtered_df['is_anomaly'] == -1]

# Show filtered count
st.info(f"Showing {len(filtered_df)} of {len(df)} transactions")

st.dataframe(filtered_df, use_container_width=True, height=400)

# Download button
col1, col2 = st.columns(2)

with col1:
    st.download_button(
        label="📥 Download Filtered Data",
        data=filtered_df.to_csv(index=False),
        file_name=f"filtered_transactions_{selected_department.lower().replace(' ', '_')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    if 'is_anomaly' in filtered_df.columns:
        high_risk_df = filtered_df[filtered_df['is_anomaly'] == -1]
        st.download_button(
            label="⚠️ Download High-Risk Only",
            data=high_risk_df.to_csv(index=False),
            file_name=f"high_risk_{selected_department.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ==========================================
# SUMMARY INSIGHTS
# ==========================================
st.markdown("---")
st.subheader("💡 Key Insights")

insight_col1, insight_col2, insight_col3 = st.columns(3)

with insight_col1:
    if 'amount' in df.columns and len(df) > 0:
        high_value = df[df['amount'] > df['amount'].quantile(0.9)]
        st.metric(
            "High-Value Transactions",
            len(high_value),
            delta=f">${df['amount'].quantile(0.9):,.2f} threshold"
        )

with insight_col2:
    if 'is_anomaly' in df.columns and len(df) > 0:
        detection_rate = len(df[df['is_anomaly'] == -1]) / len(df) * 100
        st.metric(
            "Detection Rate",
            f"{detection_rate:.2f}%",
            delta="of transactions flagged"
        )

with insight_col3:
    if 'vendor' in df.columns and len(df) > 0:
        unique_vendors = df['vendor'].nunique()
        st.metric(
            "Active Vendors",
            unique_vendors,
            delta=f"{len(df)/unique_vendors:.1f} avg txn/vendor"
        )
