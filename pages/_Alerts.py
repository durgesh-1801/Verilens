"""
⚠️ Alerts Page
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Alerts", page_icon="⚠️", layout="wide")

st.title("⚠️ Alert Management")

alerts = st.session_state.get('alerts', [])

# Stats
col1, col2, col3, col4 = st.columns(4)

high = len([a for a in alerts if a.get('severity') == 'high'])
medium = len([a for a in alerts if a.get('severity') == 'medium'])
low = len([a for a in alerts if a.get('severity') == 'low'])

with col1:
    st.metric("🔴 High", high)
with col2:
    st.metric("🟠 Medium", medium)
with col3:
    st.metric("🟢 Low", low)
with col4:
    st.metric("📊 Total", len(alerts))

st.markdown("---")

# Filters
col1, col2 = st.columns(2)

with col1:
    severity_filter = st.multiselect(
        "Filter by Severity",
        ["high", "medium", "low"],
        default=["high", "medium", "low"]
    )

with col2:
    sort_by = st.selectbox("Sort by", ["Score (High to Low)", "Score (Low to High)"])

# Filter and sort
filtered = [a for a in alerts if a.get('severity') in severity_filter]

if sort_by == "Score (High to Low)":
    filtered = sorted(filtered, key=lambda x: x.get('score', 0), reverse=True)
else:
    filtered = sorted(filtered, key=lambda x: x.get('score', 0))

# Display
st.subheader(f"📋 Alerts ({len(filtered)})")

if not filtered:
    st.info("No alerts. Run anomaly detection first.")
else:
    for i, alert in enumerate(filtered[:50]):
        severity = alert.get('severity', 'medium')
        icon = "🔴" if severity == 'high' else "🟠" if severity == 'medium' else "🟢"
        
        with st.expander(f"{icon} Alert #{alert.get('id')} | {severity.upper()} | Score: {alert.get('score', 0):.3f}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**ID:** {alert.get('id')}")
            with col2:
                st.write(f"**Score:** {alert.get('score', 0):.4f}")
            with col3:
                if 'amount' in alert:
                    st.write(f"**Amount:** ₹{alert['amount']:,.2f}")
            
            # Show record details
            if st.session_state.get('data') is not None:
                df = st.session_state.data
                idx = alert.get('id')
                if idx is not None and idx < len(df):
                    st.markdown("**Record Details:**")
                    st.json(df.iloc[idx].to_dict())
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.button("✅ Mark Reviewed", key=f"rev_{i}")
            with col2:
                st.button("🚫 False Positive", key=f"fp_{i}")
            with col3:
                st.button("📧 Escalate", key=f"esc_{i}")

st.markdown("---")

# Bulk actions
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Export Alerts", use_container_width=True):
        if alerts:
            st.download_button(
                "Download CSV",
                pd.DataFrame(alerts).to_csv(index=False),
                "alerts.csv",
                "text/csv"
            )

with col2:
    if st.button("✅ Mark All Reviewed", use_container_width=True):
        st.success("All marked!")

with col3:
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.alerts = []
        st.rerun()
