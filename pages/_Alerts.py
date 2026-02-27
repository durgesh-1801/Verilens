import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import database  # Database integration


# Authentication check
if not st.session_state.get('authenticated'):
    st.error("🔒 Access Denied - Please login first")
    
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/_Login.py")
    
    st.stop()
# ========== END AUTHENTICATION CHECK ==========


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

# Alert statistics
col1, col2, col3, col4 = st.columns(4)

high_alerts = len([a for a in alerts if a.get('severity') == 'high'])
medium_alerts = len([a for a in alerts if a.get('severity') == 'medium'])
low_alerts = len([a for a in alerts if a.get('severity') == 'low'])

with col1:
    st.metric("🔴 High Priority", high_alerts)
with col2:
    st.metric("🟠 Medium Priority", medium_alerts)
with col3:
    st.metric("🟢 Low Priority", low_alerts)
with col4:
    st.metric("📊 Total Alerts", len(alerts))

st.markdown("---")

# Filter options
col1, col2, col3 = st.columns(3)

with col1:
    severity_filter = st.multiselect(
        "Filter by Severity",
        ["high", "medium", "low"],
        default=["high", "medium", "low"]
    )

with col2:
    sort_by = st.selectbox(
        "Sort by",
        ["Score (High to Low)", "Score (Low to High)", "Recent First"]
    )

with col3:
    search = st.text_input("Search by ID", "")

# Filter and sort alerts
filtered_alerts = [a for a in alerts if a.get('severity') in severity_filter]

if search:
    filtered_alerts = [a for a in filtered_alerts if search in str(a.get('id', ''))]

if sort_by == "Score (High to Low)":
    filtered_alerts = sorted(filtered_alerts, key=lambda x: x.get('score', 0), reverse=True)
elif sort_by == "Score (Low to High)":
    filtered_alerts = sorted(filtered_alerts, key=lambda x: x.get('score', 0))

# Display alerts
st.subheader(f"📋 Alerts ({len(filtered_alerts)})")

if not filtered_alerts:
    st.info("No alerts to display. Run AI Risk Scan to generate alerts.")
else:
    for i, alert in enumerate(filtered_alerts[:50]):  # Show max 50 alerts
        severity = alert.get('severity', 'medium')
        alert_id = alert.get('id', i)
        
        # Check alert status
        is_reviewed = alert_id in st.session_state.reviewed_alerts
        is_escalated = alert_id in st.session_state.escalated_alerts
        has_doc_request = alert_id in st.session_state.doc_requested_alerts
        
        if severity == 'high':
            alert_color = "🔴"
            bg_color = "#ffebee"
        elif severity == 'medium':
            alert_color = "🟠"
            bg_color = "#fff3e0"
        else:
            alert_color = "🟢"
            bg_color = "#e8f5e9"
        
        # Add status badges
        status_badges = ""
        if is_reviewed:
            status_badges += "✅ Reviewed "
        if is_escalated:
            status_badges += "🚨 Escalated "
        if has_doc_request:
            status_badges += "📄 Docs Requested "
        
        with st.expander(f"{alert_color} Alert #{alert_id} - Severity: {severity.upper()} - Score: {alert.get('score', 0):.3f} {status_badges}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**Record ID:** {alert_id}")
            with col2:
                st.markdown(f"**Anomaly Score:** {alert.get('score', 0):.4f}")
            with col3:
                st.markdown(f"**Detected:** {alert.get('timestamp', 'N/A')[:19] if alert.get('timestamp') else 'N/A'}")
            
            # Show record details if data is available
            if st.session_state.get('data') is not None:
                df = st.session_state.data
                record_id = alert.get('id')
                
                if record_id is not None and record_id < len(df):
                    st.markdown("**Record Details:**")
                    record = df.iloc[record_id]
                    st.json(record.to_dict())
            
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
    alert_ids = [f"Alert #{alert.get('id', i)} - {alert.get('severity', 'medium').upper()}" 
                 for i, alert in enumerate(filtered_alerts[:50])]
    
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
                    
                    # WHY AI FLAGGED THIS
                    st.markdown("### 🤖 Why AI Flagged This Transaction")
                    
                    with st.container():
                        # Generate AI explanation based on data
                        amount = record.get('amount', record.get('transaction_amount', 0))
                        dept = record.get('department', record.get('dept', 'Unknown'))
                        vendor = record.get('vendor', record.get('vendor_name', 'Unknown'))
                        score = selected_alert.get('score', 0)
                        
                        # Build explanation
                        explanations = []
                        
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
                            database.save_transaction(transaction_data)
                            
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
