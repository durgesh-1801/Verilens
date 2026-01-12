import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Alerts", page_icon="⚠️", layout="wide")

st.title("⚠️ Alert Management Center")

# Initialize alerts in session state
if 'alerts' not in st.session_state:
    st.session_state.alerts = []

alerts = st.session_state.alerts

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
    st.info("No alerts to display. Run anomaly detection to generate alerts.")
else:
    for i, alert in enumerate(filtered_alerts[:50]):  # Show max 50 alerts
        severity = alert.get('severity', 'medium')
        
        if severity == 'high':
            alert_color = "🔴"
            bg_color = "#ffebee"
        elif severity == 'medium':
            alert_color = "🟠"
            bg_color = "#fff3e0"
        else:
            alert_color = "🟢"
            bg_color = "#e8f5e9"
        
        with st.expander(f"{alert_color} Alert #{alert.get('id', i)} - Severity: {severity.upper()} - Score: {alert.get('score', 0):.3f}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**Record ID:** {alert.get('id', 'N/A')}")
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
                if st.button("✅ Mark as Reviewed", key=f"review_{i}"):
                    st.success("Marked as reviewed!")
            with col2:
                if st.button("🚫 False Positive", key=f"fp_{i}"):
                    st.info("Marked as false positive")
            with col3:
                if st.button("🔍 Investigate", key=f"inv_{i}"):
                    st.info("Opening investigation...")
            with col4:
                if st.button("📧 Escalate", key=f"esc_{i}"):
                    st.warning("Escalated to supervisor")

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
        st.success("All alerts marked as reviewed!")

with col3:
    if st.button("🗑️ Clear All Alerts", use_container_width=True):
        st.session_state.alerts = []
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
        st.success("Configuration saved!")
