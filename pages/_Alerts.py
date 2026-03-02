"""
Alerts Page
Alert Management Center with Audit Intelligence Integration
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import database
import sys
from pathlib import Path

# ========== AUDIT ENGINE IMPORT ==========
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from utils.audit_engine import (
        generate_audit_flags,
        summarize_audit_findings,
        filter_by_audit_severity,
        get_flagged_transactions,
        get_audit_rules_documentation
    )
    AUDIT_ENGINE_AVAILABLE = True
except ImportError:
    AUDIT_ENGINE_AVAILABLE = False
    print("Warning: Audit engine not available")
# ========== END AUDIT ENGINE IMPORT ==========

# ========== AUDIT CASE MANAGER IMPORT ==========
try:
    from utils.AuditCaseManager import (
        update_case_status,
        assign_case,
        add_case_comment,
        get_case_summary
    )
    AUDIT_CASE_MANAGER_AVAILABLE = True
except ImportError:
    AUDIT_CASE_MANAGER_AVAILABLE = False
# ========== END AUDIT CASE MANAGER IMPORT ==========

def normalize_flags(flags):
    """
    Ensure audit_flags is always a list.
    Handles list, string, None safely.
    """
    if isinstance(flags, list):
        return flags

    if isinstance(flags, str):
        return [f.strip() for f in flags.split(";") if f.strip()]

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

# Viewers cannot access alerts
if user_role == 'viewer':
    st.error("🚫 Alert management requires Auditor or Admin role")
    st.info("Contact your administrator to upgrade your access level")
    st.stop()
# ========== END RBAC CHECK ==========

st.set_page_config(page_title="Alerts", page_icon="⚠️", layout="wide")

st.title("⚠️ Alert Management Center")

# Initialize alerts in session state
if 'alerts' not in st.session_state:
    st.session_state.alerts = []

# Initialize reviewed alerts tracker
if 'reviewed_alerts' not in st.session_state:
    st.session_state.reviewed_alerts = set()

if 'escalated_alerts' not in st.session_state:
    st.session_state.escalated_alerts = set()

if 'doc_requested_alerts' not in st.session_state:
    st.session_state.doc_requested_alerts = set()

# Initialize auditor workflow tracking
if 'audit_status' not in st.session_state:
    st.session_state.audit_status = {}

if 'audit_notes' not in st.session_state:
    st.session_state.audit_notes = {}

if 'review_timestamps' not in st.session_state:
    st.session_state.review_timestamps = {}

# ========== NEW: APPLY AUDIT ENGINE IF NOT ALREADY APPLIED ==========
if st.session_state.get('data') is not None:
    df = st.session_state.data.copy()
    
    if AUDIT_ENGINE_AVAILABLE and 'audit_flags' not in df.columns:
        with st.spinner("🔍 Applying audit intelligence to data..."):
            try:
                df = generate_audit_flags(df)
                st.session_state.data = df
                st.session_state.audit_processed = True
                st.success("✓ Audit rules applied to alert data")
            except Exception as e:
                st.warning(f"Audit engine could not be applied: {e}")
                AUDIT_ENGINE_AVAILABLE = False
# ========== END AUDIT ENGINE APPLICATION ==========

alerts = st.session_state.alerts

# Department Filter
selected_department = st.session_state.get('selected_department', 'All Departments')

# Filter alerts by department if data exists
if selected_department != "All Departments" and st.session_state.get('data') is not None:
    df = st.session_state.data
    dept_alerts = []
    for alert in alerts:
        record_id = alert.get('id')
        if record_id is not None and record_id < len(df):
            record = df.iloc[record_id]
            dept = record.get('department', record.get('dept', ''))
            if dept == selected_department:
                dept_alerts.append(alert)
    alerts = dept_alerts

# ========== NEW: AUDIT INTELLIGENCE SUMMARY ==========
if AUDIT_ENGINE_AVAILABLE and st.session_state.get('data') is not None:
    df = st.session_state.data
    
    if 'audit_severity' in df.columns:
        st.markdown("### 🔍 Audit Intelligence Summary")
        
        audit_summary = summarize_audit_findings(df)
        
        audit_col1, audit_col2, audit_col3, audit_col4 = st.columns(4)
        
        with audit_col1:
            st.metric("Total Audit Flags", f"{audit_summary['total_flagged']:,}")
        
        with audit_col2:
            st.metric("🔴 High Risk (Audit)", f"{audit_summary['high_risk_count']:,}")
        
        with audit_col3:
            st.metric("🟡 Medium Risk (Audit)", f"{audit_summary['medium_risk_count']:,}")
        
        with audit_col4:
            st.metric("🟢 Low Risk (Audit)", f"{audit_summary['low_risk_count']:,}")
        
        # Show audit rules documentation
        with st.expander("📋 View Active Audit Rules"):
            rules = get_audit_rules_documentation()
            for rule in rules:
                st.markdown(f"**{rule['rule_name']}** ({rule['risk_level']} - {rule['points']} points)")
                st.markdown(f"- {rule['description']}")
                st.markdown(f"- Flag: _{rule['flag_message']}_")
                st.markdown("---")
        
        st.markdown("---")
# ========== END AUDIT INTELLIGENCE SUMMARY ==========

# Alert statistics (ML-based)
col1, col2, col3, col4 = st.columns(4)

high_alerts = len([a for a in alerts if a.get('severity') == 'high'])
medium_alerts = len([a for a in alerts if a.get('severity') == 'medium'])
low_alerts = len([a for a in alerts if a.get('severity') == 'low'])

with col1:
    st.metric("🔴 High Priority (ML)", high_alerts)
with col2:
    st.metric("🟠 Medium Priority (ML)", medium_alerts)
with col3:
    st.metric("🟢 Low Priority (ML)", low_alerts)
with col4:
    st.metric("📊 Total ML Alerts", len(alerts))

st.markdown("---")

# Filter options (enhanced with audit filters)
col1, col2, col3 = st.columns(3)

with col1:
    # Enhanced severity filter with audit options
    filter_options = ["high", "medium", "low"]
    
    if AUDIT_ENGINE_AVAILABLE and st.session_state.get('data') is not None:
        df_check = st.session_state.data
        if 'audit_severity' in df_check.columns:
            filter_options.extend(["audit_high", "audit_medium", "audit_low"])
    
    severity_filter = st.multiselect(
        "Filter by Severity",
        filter_options,
        default=["high", "medium", "low"]
    )

with col2:
    sort_by = st.selectbox(
        "Sort by",
        ["Score (High to Low)", "Score (Low to High)", "Recent First", "Audit Risk Score"]
    )

with col3:
    search = st.text_input("Search by ID", "")

# Filter and sort alerts
filtered_alerts = [a for a in alerts if a.get('severity') in severity_filter]

# ========== NEW: ADD AUDIT-BASED ALERTS ==========
if AUDIT_ENGINE_AVAILABLE and st.session_state.get('data') is not None:
    df = st.session_state.data
    
    if 'audit_flags' in df.columns:
        # Check if we need to include audit-based alerts
        include_audit_high = "audit_high" in severity_filter
        include_audit_medium = "audit_medium" in severity_filter
        include_audit_low = "audit_low" in severity_filter
        
        if include_audit_high or include_audit_medium or include_audit_low:
            # Get flagged transactions
            flagged_df = get_flagged_transactions(df, min_flags=1)
            
            for idx, row in flagged_df.iterrows():
                audit_sev = row.get('audit_severity', 'Low').lower()
                
                # Check if this severity should be included
                should_include = False
                if audit_sev == 'high' and include_audit_high:
                    should_include = True
                elif audit_sev == 'medium' and include_audit_medium:
                    should_include = True
                elif audit_sev == 'low' and include_audit_low:
                    should_include = True
                
                if should_include:
                    # Create audit alert
                    audit_alert = {
                        'id': idx,
                        'severity': f"audit_{audit_sev}",
                        'score': row.get('audit_risk_score', 0) / 100,  # Normalize to 0-1
                        'timestamp': datetime.now().isoformat(),
                        'reason': '; '.join(row.get('audit_flags', [])),
                        'source': 'audit_engine'
                    }
                    
                    # Check if not already in filtered alerts
                    if not any(a.get('id') == idx and a.get('source') == 'audit_engine' for a in filtered_alerts):
                        filtered_alerts.append(audit_alert)
# ========== END AUDIT-BASED ALERTS ==========

if search:
    filtered_alerts = [a for a in filtered_alerts if search in str(a.get('id', ''))]

# Sort alerts
if sort_by == "Score (High to Low)":
    filtered_alerts = sorted(filtered_alerts, key=lambda x: x.get('score', 0), reverse=True)
elif sort_by == "Score (Low to High)":
    filtered_alerts = sorted(filtered_alerts, key=lambda x: x.get('score', 0))
elif sort_by == "Audit Risk Score" and AUDIT_ENGINE_AVAILABLE:
    # Sort by audit risk score if available
    def get_audit_score(alert):
        if alert.get('source') == 'audit_engine':
            return alert.get('score', 0)
        # For ML alerts, check if there's an audit score in the data
        record_id = alert.get('id')
        if st.session_state.get('data') is not None and record_id is not None:
            df = st.session_state.data
            if record_id < len(df) and 'audit_risk_score' in df.columns:
                return df.iloc[record_id].get('audit_risk_score', 0) / 100
        return alert.get('score', 0)
    
    filtered_alerts = sorted(filtered_alerts, key=get_audit_score, reverse=True)

# Display alerts
st.subheader(f"📋 Alerts ({len(filtered_alerts)})")

if not filtered_alerts:
    st.info("No alerts to display. Run AI Risk Scan to generate alerts or check filter settings.")
else:
    # ========== MODIFIED: FILTER TO SHOW ONLY HIGH/MEDIUM SEVERITY ==========
    # Only show alerts with audit cases (High/Medium severity)
    if st.session_state.get('data') is not None and 'audit_case_id' in st.session_state.data.columns:
        df_with_cases = st.session_state.data
        case_alerts = []
        
        for alert in filtered_alerts[:50]:
            alert_id = alert.get('id')
            if alert_id is not None and alert_id < len(df_with_cases):
                case_id = df_with_cases.iloc[alert_id].get('audit_case_id')
                if pd.notna(case_id):
                    alert['audit_case_id'] = case_id
                    alert['audit_status'] = df_with_cases.iloc[alert_id].get('audit_status', 'Open')
                    case_alerts.append(alert)
        
        display_alerts = case_alerts if case_alerts else filtered_alerts[:50]
        st.info(f"Showing {len(display_alerts)} alerts with audit cases (High/Medium severity only)")
    else:
        display_alerts = filtered_alerts[:50]
    # ========== END FILTER ==========
    
    for i, alert in enumerate(display_alerts):
        severity = alert.get('severity', 'medium')
        alert_id = alert.get('id', i)
        source = alert.get('source', 'ml')
        
        # Check alert status
        is_reviewed = alert_id in st.session_state.reviewed_alerts
        is_escalated = alert_id in st.session_state.escalated_alerts
        has_doc_request = alert_id in st.session_state.doc_requested_alerts
        
        # Get audit case info
        case_id = alert.get('audit_case_id', 'N/A')
        audit_status = alert.get('audit_status', 'N/A')
        
        # Determine alert color and badge
        if severity.startswith('audit_'):
            audit_sev = severity.replace('audit_', '')
            if audit_sev == 'high':
                alert_color = "🔴"
                severity_display = "HIGH (AUDIT)"
            elif audit_sev == 'medium':
                alert_color = "🟡"
                severity_display = "MEDIUM (AUDIT)"
            else:
                alert_color = "🟢"
                severity_display = "LOW (AUDIT)"
        else:
            if severity == 'high':
                alert_color = "🔴"
                severity_display = "HIGH (ML)"
            elif severity == 'medium':
                alert_color = "🟠"
                severity_display = "MEDIUM (ML)"
            else:
                alert_color = "🟢"
                severity_display = "LOW (ML)"
        
        # Add status badges
        status_badges = ""
        if is_reviewed:
            status_badges += "✅ Reviewed "
        if is_escalated:
            status_badges += "🚨 Escalated "
        if has_doc_request:
            status_badges += "📄 Docs Requested "
        
        # ========== NEW: SHOW CASE ID AND STATUS IN HEADER ==========
        header_text = f"{alert_color} Alert #{alert_id} - {severity_display} - Score: {alert.get('score', 0):.3f}"
        if case_id != 'N/A':
            header_text += f" | 📋 {case_id} - {audit_status}"
        header_text += f" {status_badges}"
        # ========== END HEADER ==========
        
        with st.expander(header_text):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**Record ID:** {alert_id}")
                # ========== NEW: SHOW CASE ID ==========
                if case_id != 'N/A':
                    st.markdown(f"**Case ID:** {case_id}")
                # ========== END CASE ID ==========
            with col2:
                st.markdown(f"**Risk Score:** {alert.get('score', 0):.4f}")
                # ========== NEW: SHOW AUDIT STATUS ==========
                if audit_status != 'N/A':
                    status_colors = {
                        'Open': '🟡',
                        'Under Review': '🔵',
                        'Escalated': '🔴',
                        'Closed': '🟢'
                    }
                    st.markdown(f"**Status:** {status_colors.get(audit_status, '⚪')} {audit_status}")
                # ========== END AUDIT STATUS ==========
            with col3:
                st.markdown(f"**Detected:** {alert.get('timestamp', 'N/A')[:19] if alert.get('timestamp') else 'N/A'}")
            
            # ========== NEW: AUDIT CASE MANAGEMENT DROPDOWN ==========
            if case_id != 'N/A' and AUDIT_CASE_MANAGER_AVAILABLE:
                st.markdown("---")
                st.markdown("**🔧 Case Management**")
                
                case_col1, case_col2 = st.columns(2)
                
                with case_col1:
                    new_status = st.selectbox(
                        "Update Case Status",
                        ["Open", "Under Review", "Escalated", "Closed"],
                        index=["Open", "Under Review", "Escalated", "Closed"].index(audit_status) if audit_status in ["Open", "Under Review", "Escalated", "Closed"] else 0,
                        key=f"status_select_{i}"
                    )
                    
                    if st.button("💾 Update Status", key=f"update_status_{i}"):
                        # Update in session state
                        if st.session_state.get('data') is not None:
                            df = st.session_state.data
                            df = update_case_status(df, case_id, new_status)
                            st.session_state.data = df
                            
                            # Update in database
                            try:
                                database.update_audit_case(case_id, 'status', new_status)
                                st.success(f"✓ Case {case_id} status updated to {new_status}")
                            except Exception as e:
                                st.warning(f"Status updated in session but not saved to database: {e}")
                            
                            st.rerun()
                
                with case_col2:
                    case_comment = st.text_input(
                        "Add Comment",
                        key=f"comment_{i}",
                        placeholder="Enter case notes..."
                    )
                    
                    if st.button("💬 Add Comment", key=f"add_comment_{i}"):
                        if case_comment:
                            # Update in session state
                            if st.session_state.get('data') is not None:
                                df = st.session_state.data
                                df = add_case_comment(df, case_id, case_comment)
                                st.session_state.data = df
                                
                                # Update in database
                                try:
                                    current_comment = database.get_audit_cases().query(f"case_id == '{case_id}'")['auditor_comment'].iloc[0]
                                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                                    if current_comment:
                                        new_comment = f"{current_comment}\n[{timestamp}] {case_comment}"
                                    else:
                                        new_comment = f"[{timestamp}] {case_comment}"
                                    database.update_audit_case(case_id, 'auditor_comment', new_comment)
                                    st.success(f"✓ Comment added to {case_id}")
                                except:
                                    st.warning("Comment added in session but not saved to database")
                                
                                st.rerun()
            # ========== END CASE MANAGEMENT ==========
            
            # Show audit flags if available
            if source == 'audit_engine' or (
                st.session_state.get('data') is not None and AUDIT_ENGINE_AVAILABLE
            ):
                df = st.session_state.data

                if alert_id < len(df) and 'audit_flags' in df.columns:

                    flags = normalize_flags(
                        df.iloc[alert_id].get('audit_flags', [])
                    )

                    if flags:
                        st.markdown("**🔍 Audit Flags:**")
                        for flag in flags:
                            st.write(f"• {flag}")            
            # Show record details if data is available
            if st.session_state.get('data') is not None:
                df = st.session_state.data
                record_id = alert.get('id')
                
                if record_id is not None and record_id < len(df):
                    st.markdown("**Record Details:**")
                    record = df.iloc[record_id]
                    
                    display_dict = {
                        'Amount': record.get('amount', 'N/A'),
                        'Department': record.get('department', 'N/A'),
                        'Vendor': record.get('vendor', 'N/A'),
                        'Date': record.get('date', record.get('transaction_date', 'N/A'))
                    }
                    
                    if 'audit_risk_score' in record:
                        display_dict['Audit Risk Score'] = f"{record['audit_risk_score']}/100"
                    if 'audit_severity' in record:
                        display_dict['Audit Severity'] = record['audit_severity']
                    
                    st.json(display_dict)
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("✅ Mark as Reviewed", key=f"review_{i}", disabled=is_reviewed):
                    st.session_state.reviewed_alerts.add(alert_id)
                    st.rerun()
            with col2:
                if st.button("🚫 False Positive", key=f"fp_{i}"):
                    st.info("Marked as false positive")
            with col3:
                if st.button("🔍 Investigate", key=f"inv_{i}"):
                    st.info("Opening investigation...")
            with col4:
                if st.button("📧 Escalate", key=f"esc_{i}", disabled=is_escalated):
                    st.session_state.escalated_alerts.add(alert_id)
                    st.rerun()

def get_ai_confidence(score):
    """Convert anomaly score to AI confidence percentage and level"""
    if score >= 0.8:
        return score * 100, "High Confidence"
    elif score >= 0.5:
        return score * 100, "Medium Confidence"
    else:
        return score * 100, "Low Confidence"

# Transaction Details Panel
if filtered_alerts:
    st.markdown("---")
    st.subheader("📄 Transaction Details")
    
    # Transaction selector
    alert_ids = []
    for i, alert in enumerate(filtered_alerts[:50]):
        severity = alert.get('severity', 'medium')
        source = alert.get('source', 'ml')
        
        if severity.startswith('audit_'):
            severity_label = severity.replace('audit_', '').upper() + " (AUDIT)"
        else:
            severity_label = severity.upper() + " (ML)"
        
        alert_ids.append(f"Alert #{alert.get('id', i)} - {severity_label}")
    
    selected_alert_idx = st.selectbox(
        "Select transaction to view details:",
        range(len(alert_ids)),
        format_func=lambda x: alert_ids[x],
        key="transaction_selector"
    )
    
    if selected_alert_idx is not None:
        selected_alert = filtered_alerts[selected_alert_idx]
        record_id = selected_alert.get('id')
        
        # Details container
        with st.container():
            # Header with severity indicator
            severity = selected_alert.get('severity', 'medium')
            
            if severity.startswith('audit_'):
                severity_colors = {'audit_high': '🔴', 'audit_medium': '🟡', 'audit_low': '🟢'}
            else:
                severity_colors = {'high': '🔴', 'medium': '🟠', 'low': '🟢'}
            
            st.markdown(f"### {severity_colors.get(severity, '⚪')} Transaction ID: {record_id}")
            
            # AI Confidence Display
            score = selected_alert.get('score', 0)
            confidence_pct, confidence_level = get_ai_confidence(score)
            
            col_conf1, col_conf2 = st.columns(2)
            with col_conf1:
                st.warning(f"**Risk Score:** {score:.4f} | **Severity:** {severity.upper()}")
            with col_conf2:
                st.info(f"**AI Confidence:** {confidence_pct:.1f}% ({confidence_level})")
            
            # Transaction details in columns
            if st.session_state.get('data') is not None and record_id is not None:
                df = st.session_state.data
                
                if record_id < len(df):
                    record = df.iloc[record_id]
                    
                    # Financial Information
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("**Date**")
                        st.text(record.get('date', record.get('transaction_date', 'N/A')))
                    with col2:
                        st.markdown("**Amount**")
                        amount = record.get('amount', record.get('transaction_amount', 0))
                        st.text(f"${amount:,.2f}" if isinstance(amount, (int, float)) else amount)
                    with col3:
                        st.markdown("**Department**")
                        st.text(record.get('department', record.get('dept', 'N/A')))
                    
                    st.markdown("---")
                    
                    # Additional Details
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Purpose**")
                        st.text(record.get('purpose', record.get('description', 'N/A')))
                        
                        st.markdown("**Vendor**")
                        st.text(record.get('vendor', record.get('vendor_name', 'N/A')))
                    
                    with col2:
                        st.markdown("**Risk Reason**")
                        reason = selected_alert.get('reason', 'Anomalous pattern detected based on statistical analysis')
                        st.text_area("", value=reason, height=100, disabled=True, label_visibility="collapsed")
                    
                    st.markdown("---")
                    
                    # ========== ENHANCED: WHY AI FLAGGED THIS (WITH AUDIT) ==========
                    st.markdown("### 🤖 Why AI Flagged This Transaction")
                    
                    with st.container():
                        # Generate AI explanation based on data
                        amount = record.get('amount', record.get('transaction_amount', 0))
                        dept = record.get('department', record.get('dept', 'Unknown'))
                        vendor = record.get('vendor', record.get('vendor_name', 'Unknown'))
                        score = selected_alert.get('score', 0)
                        
                        # Build explanation
                        explanations = []
                        
                        # ML explanations
                        if score > 0.8:
                            explanations.append("🔴 **High Anomaly Score**: Transaction significantly deviates from normal patterns")
                        
                        if isinstance(amount, (int, float)) and amount > 100000:
                            explanations.append(f"💰 **Amount Deviation**: ${amount:,.2f} exceeds typical {dept} department baseline")
                        
                        if "Unknown" in vendor or not vendor:
                            explanations.append("⚠️ **Vendor Risk**: Unknown or unregistered vendor")
                        
                        if record.get('approval_status', '').lower() == 'pending':
                            explanations.append("📋 **Approval Mismatch**: High-value transaction pending approval")
                        
                        payment_method = record.get('payment_method', '')
                        if 'Wire Transfer' in payment_method and amount > 50000:
                            explanations.append("🏦 **Payment Method Alert**: Large wire transfer requires additional scrutiny")
                        
                        # Time-based check
                        try:
                            trans_date = pd.to_datetime(record.get('date', record.get('transaction_date')))
                            if trans_date.weekday() >= 5:
                                explanations.append("📅 **Time-Based Anomaly**: Transaction occurred on weekend")
                        except:
                            pass
                        
                        # ========== NEW: ADD AUDIT ENGINE EXPLANATIONS ==========
                        if AUDIT_ENGINE_AVAILABLE and 'audit_flags' in record:
                            audit_flags = normalize_flags(record.get('audit_flags', []))

                            if audit_flags:
                                explanations.append("")
                                explanations.append("**🔍 Audit Rule Engine Findings:**")

                                for flag in audit_flags:
                                    explanations.append(f"• {flag}")

                                if 'audit_risk_score' in record:
                                    audit_score = record['audit_risk_score']
                                    explanations.append(f"• **Audit Risk Score**: {audit_score}/100")
                            if audit_flags:
                                explanations.append("")
                                explanations.append("**🔍 Audit Rule Engine Findings:**")
                                for flag in audit_flags:
                                    explanations.append(f"• {flag}")
                                
                                if 'audit_risk_score' in record:
                                    audit_score = record['audit_risk_score']
                                    explanations.append(f"• **Audit Risk Score**: {audit_score}/100")
                        # ========== END AUDIT EXPLANATIONS ==========
                        
                        if not explanations:
                            explanations.append("📊 **Pattern Deviation**: Statistical analysis detected unusual transaction characteristics")
                        
                        for exp in explanations:
                            st.markdown(exp)
                    
                    st.markdown("---")
                    
                    # TRANSACTION TIMELINE
                    st.markdown("### 📅 Transaction Timeline")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    try:
                        trans_date = pd.to_datetime(record.get('date', record.get('transaction_date', datetime.now())))
                    except:
                        trans_date = datetime.now()
                    
                    with col1:
                        st.markdown("**Created**")
                        st.info(trans_date.strftime("%Y-%m-%d"))
                    
                    with col2:
                        st.markdown("**Approved**")
                        approval_status = record.get('approval_status', 'Pending')
                        if approval_status.lower() == 'approved':
                            approved_date = trans_date + timedelta(days=1)
                            st.success(approved_date.strftime("%Y-%m-%d"))
                        else:
                            st.warning("Pending")
                    
                    with col3:
                        st.markdown("**Payment**")
                        if approval_status.lower() == 'approved':
                            payment_date = trans_date + timedelta(days=3)
                            st.success(payment_date.strftime("%Y-%m-%d"))
                        else:
                            st.warning("Not Paid")
                    
                    with col4:
                        st.markdown("**AI Flagged**")
                        flag_date = selected_alert.get('timestamp', datetime.now().isoformat())[:10]
                        st.error(flag_date)
                    
                    st.markdown("---")
                    
                    # ========== AUDIT CASE WORKFLOW WITH DATABASE ==========
                    st.markdown("### 📋 Audit Case Management")
                    
                    # Load from database if available
                    db_audit = database.get_audit_status(record_id)
                    
                    # Initialize from database or session state
                    if db_audit:
                        current_status = db_audit['status']
                        current_notes = db_audit['auditor_notes'] or ""
                        if db_audit['review_timestamp']:
                            try:
                                current_timestamp = datetime.fromisoformat(db_audit['review_timestamp'])
                            except:
                                current_timestamp = st.session_state.review_timestamps.get(record_id)
                        else:
                            current_timestamp = st.session_state.review_timestamps.get(record_id)
                    else:
                        current_status = st.session_state.audit_status.get(record_id, "Pending Review")
                        current_notes = st.session_state.audit_notes.get(record_id, "")
                        current_timestamp = st.session_state.review_timestamps.get(record_id)
                    
                    # Audit Status and Timestamp Display
                    col_audit1, col_audit2 = st.columns([1, 1])
                    
                    with col_audit1:
                        new_status = st.selectbox(
                            "Audit Case Status",
                            ["Pending Review", "Reviewed", "Escalated"],
                            index=["Pending Review", "Reviewed", "Escalated"].index(current_status),
                            key=f"audit_status_{record_id}"
                        )
                        
                        # Auto-update timestamp if status changed from Pending Review
                        if new_status != current_status and current_status == "Pending Review":
                            st.session_state.review_timestamps[record_id] = datetime.now()
                            current_timestamp = st.session_state.review_timestamps[record_id]
                    
                    with col_audit2:
                        if current_timestamp:
                            st.markdown("**Review Timestamp**")
                            st.info(current_timestamp.strftime("%Y-%m-%d %H:%M:%S"))
                        else:
                            st.markdown("**Review Timestamp**")
                            st.warning("Not yet reviewed")
                    
                    # Auditor Notes
                    st.markdown("**Auditor Notes**")
                    auditor_notes = st.text_area(
                        "Add your investigation notes, findings, or recommendations:",
                        value=current_notes,
                        height=120,
                        key=f"audit_notes_{record_id}",
                        placeholder="Enter notes about your review, findings, next steps, or recommendations..."
                    )
                    
                    # Save Audit Info Button
                    if st.button("💾 Save Audit Information", key=f"save_audit_{record_id}", type="primary", use_container_width=True):
                        # Save to session state
                        old_status = st.session_state.audit_status.get(record_id, "Pending Review")
                        st.session_state.audit_status[record_id] = new_status
                        st.session_state.audit_notes[record_id] = auditor_notes
                        
                        # Set timestamp if moving from Pending Review
                        if new_status != "Pending Review" and record_id not in st.session_state.review_timestamps:
                            st.session_state.review_timestamps[record_id] = datetime.now()
                        
                        current_timestamp = st.session_state.review_timestamps.get(record_id)
                        
                        # ========== SAVE TO DATABASE ==========
                        try:
                            # Get user and org info for RBAC
                            user_id = st.session_state['user']['id']
                            organization_id = st.session_state['user'].get('organization_id')
                            
                            # Save transaction to database
                            transaction_data = {
                                'transaction_id': record_id,
                                'department': record.get('department', record.get('dept', 'Unknown')),
                                'amount': float(record.get('amount', record.get('transaction_amount', 0))),
                                'vendor': record.get('vendor', record.get('vendor_name', 'Unknown')),
                                'purpose': record.get('purpose', record.get('description', 'N/A')),
                                'transaction_date': str(record.get('date', record.get('transaction_date', ''))),
                                'risk_score': float(selected_alert.get('score', 0)),
                                'severity': selected_alert.get('severity', 'medium'),
                                'ai_reason': selected_alert.get('reason', 'Anomaly detected'),
                                'detection_timestamp': selected_alert.get('timestamp', datetime.now().isoformat())
                            }
                            database.save_transaction(transaction_data, user_id=user_id, organization_id=organization_id)
                            
                            # Save audit action
                            database.save_audit_action(
                                transaction_id=record_id,
                                status=new_status,
                                auditor_notes=auditor_notes,
                                review_timestamp=current_timestamp.isoformat() if current_timestamp else None,
                                action_type="status_update" if old_status != new_status else "notes_update"
                            )
                            
                            # Log history if status changed
                            if old_status != new_status:
                                database.log_audit_history(record_id, "status", old_status, new_status)
                            
                            st.success(f"✓ Audit information saved to database - Status: {new_status}")
                            
                        except Exception as e:
                            st.error(f"Database save error: {e}")
                            st.warning("Data saved to session only (not persisted)")
                        # ========== END DATABASE SAVE ==========
                        
                        st.rerun()
                    
                    # Display current audit summary
                    if current_status != "Pending Review" or current_notes:
                        st.markdown("---")
                        st.markdown("**Audit Summary**")
                        summary_col1, summary_col2 = st.columns(2)
                        with summary_col1:
                            status_color = {"Pending Review": "🟡", "Reviewed": "✅", "Escalated": "🚨"}
                            st.markdown(f"{status_color.get(current_status, '⚪')} **Status:** {current_status}")
                        with summary_col2:
                            if current_timestamp:
                                st.markdown(f"📅 **Last Updated:** {current_timestamp.strftime('%Y-%m-%d %H:%M')}")
                        
                        if current_notes:
                            with st.expander("View Saved Notes"):
                                st.text(current_notes)
                    
                    st.markdown("---")
                    # ========== END AUDIT CASE WORKFLOW ==========
                    
                    # AUDITOR ACTIONS
                    st.markdown("### 👨‍💼 Auditor Actions")
                    
                    alert_id = selected_alert.get('id')
                    is_reviewed = alert_id in st.session_state.reviewed_alerts
                    is_escalated = alert_id in st.session_state.escalated_alerts
                    has_doc_request = alert_id in st.session_state.doc_requested_alerts
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✅ Mark as Reviewed", key="detail_review", use_container_width=True, disabled=is_reviewed):
                            st.session_state.reviewed_alerts.add(alert_id)
                            st.success("✓ Transaction marked as reviewed")
                            st.rerun()
                        if is_reviewed:
                            st.success("Already reviewed")
                    
                    with col2:
                        if st.button("🚨 Escalate to Supervisor", key="detail_escalate", use_container_width=True, disabled=is_escalated):
                            st.session_state.escalated_alerts.add(alert_id)
                            st.error("✓ Escalated to supervisor")
                            st.rerun()
                        if is_escalated:
                            st.error("Already escalated")
                    
                    with col3:
                        if st.button("📄 Request Documents", key="detail_docs", use_container_width=True, disabled=has_doc_request):
                            st.session_state.doc_requested_alerts.add(alert_id)
                            st.info("✓ Document request sent")
                            st.rerun()
                        if has_doc_request:
                            st.info("Documents requested")

# Alert Actions
st.markdown("---")
st.subheader("🛠️ Bulk Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Export All Alerts", use_container_width=True):
        if alerts:
            alert_df = pd.DataFrame(alerts)
            st.download_button(
                label="Download CSV",
                data=alert_df.to_csv(index=False),
                file_name="alerts_export.csv",
                mime="text/csv"
            )

with col2:
    if st.button("✅ Mark All as Reviewed", use_container_width=True):
        for alert in filtered_alerts:
            st.session_state.reviewed_alerts.add(alert.get('id'))
        st.success("✓ All alerts marked as reviewed")

with col3:
    if st.button("🗑️ Clear All Alerts", use_container_width=True):
        st.session_state.alerts = []
        st.session_state.reviewed_alerts = set()
        st.session_state.escalated_alerts = set()
        st.session_state.doc_requested_alerts = set()
        st.rerun()

# Alert Rules Configuration
st.markdown("---")
st.subheader("⚙️ Alert Configuration")

with st.expander("Configure Alert Rules"):
    st.markdown("#### Threshold Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        high_threshold = st.slider("High Severity Threshold", 0.0, 1.0, 0.8)
        medium_threshold = st.slider("Medium Severity Threshold", 0.0, 1.0, 0.5)
    
    with col2:
        email_notifications = st.checkbox("Enable Email Notifications", value=False)
        slack_notifications = st.checkbox("Enable Slack Notifications", value=False)
    
    if email_notifications:
        email = st.text_input("Notification Email")
    
    if st.button("Save Configuration"):
        st.success("✓ Configuration saved")
