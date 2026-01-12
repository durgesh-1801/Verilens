import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

st.set_page_config(page_title="Reports", page_icon="📋", layout="wide")

st.title("📋 Report Generation")

if st.session_state.get('data') is None:
    st.warning("⚠️ Please upload data first!")
    st.stop()

df = st.session_state.data

# Config
st.subheader("📝 Report Configuration")

col1, col2 = st.columns(2)

with col1:
    report_title = st.text_input("Report Title", "Fraud Detection Analysis Report")
    report_author = st.text_input("Author", "AI Fraud Detection System")

with col2:
    report_date = st.date_input("Date", datetime.now())
    sections = st.multiselect(
        "Include Sections",
        ["Executive Summary", "Data Overview", "Anomaly Analysis", "Risk Assessment", "Recommendations"],
        default=["Executive Summary", "Data Overview", "Anomaly Analysis", "Recommendations"]
    )

st.markdown("---")

# Preview
st.subheader("📄 Report Preview")

total_records = len(df)
anomaly_count = np.sum(df['is_anomaly'] == -1) if 'is_anomaly' in df.columns else 0
anomaly_rate = (anomaly_count / total_records * 100) if total_records > 0 else 0

if "Executive Summary" in sections:
    st.markdown("### Executive Summary")
    st.markdown(f"""
    **Analysis Date:** {report_date}
    
    **Key Findings:**
    - Total records analyzed: **{total_records:,}**
    - Anomalies detected: **{anomaly_count:,}** ({anomaly_rate:.2f}%)
    - High-risk alerts: **{len([a for a in st.session_state.get('alerts', []) if a.get('severity') == 'high'])}**
    
    Advanced ML algorithms were used to identify potential fraudulent activities.
    """)

if "Data Overview" in sections:
    st.markdown("### Data Overview")
    st.markdown(f"""
    - **Records:** {len(df):,}
    - **Features:** {len(df.columns)}
    - **Data Quality:** {(1 - df.isnull().sum().sum() / df.size) * 100:.1f}%
    """)
    st.dataframe(df.describe(), use_container_width=True)

if "Anomaly Analysis" in sections:
    st.markdown("### Anomaly Analysis")
    if 'is_anomaly' in df.columns:
        anomaly_df = df[df['is_anomaly'] == -1]
        st.markdown(f"**Total Anomalies:** {len(anomaly_df):,}")
        st.markdown("**Top Anomalies:**")
        if 'anomaly_score' in anomaly_df.columns:
            st.dataframe(anomaly_df.nlargest(10, 'anomaly_score'), use_container_width=True)
        else:
            st.dataframe(anomaly_df.head(10), use_container_width=True)
    else:
        st.info("Run detection first")

if "Risk Assessment" in sections:
    st.markdown("### Risk Assessment")
    alerts = st.session_state.get('alerts', [])
    st.markdown(f"""
    - 🔴 **High Risk:** {len([a for a in alerts if a.get('severity') == 'high'])}
    - 🟠 **Medium Risk:** {len([a for a in alerts if a.get('severity') == 'medium'])}
    - 🟢 **Low Risk:** {len([a for a in alerts if a.get('severity') == 'low'])}
    """)

if "Recommendations" in sections:
    st.markdown("### Recommendations")
    st.markdown("""
    1. **Immediate:** Review high-priority alerts within 24 hours
    2. **Short-term:** Implement additional validation rules
    3. **Long-term:** Develop predictive models for proactive detection
    """)

st.markdown("---")

# Export
st.subheader("📥 Export Report")

col1, col2, col3 = st.columns(3)

with col1:
    csv_data = df.to_csv(index=False)
    st.download_button(
        "📊 Download CSV",
        data=csv_data,
        file_name=f"report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='All Data', index=False)
        if 'is_anomaly' in df.columns:
            df[df['is_anomaly'] == -1].to_excel(writer, sheet_name='Anomalies', index=False)
        summary = pd.DataFrame({
            'Metric': ['Total', 'Anomalies', 'Rate'],
            'Value': [len(df), anomaly_count, f"{anomaly_rate:.2f}%"]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
    
    st.download_button(
        "📗 Download Excel",
        data=buffer.getvalue(),
        file_name=f"report_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with col3:
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>{report_title}</title>
    <style>
        body {{font-family: Arial; margin: 40px;}}
        h1 {{color: #667eea;}}
        .metric {{background: #f0f0f0; padding: 10px; margin: 5px; border-radius: 5px; display: inline-block;}}
    </style>
    </head>
    <body>
        <h1>{report_title}</h1>
        <p>Author: {report_author} | Date: {report_date}</p>
        <div class="metric">Total: {len(df):,}</div>
        <div class="metric">Anomalies: {anomaly_count:,}</div>
        <div class="metric">Rate: {anomaly_rate:.2f}%</div>
        <hr>
        {df.head(50).to_html()}
    </body>
    </html>
    """
    
    st.download_button(
        "🌐 Download HTML",
        data=html,
        file_name=f"report_{datetime.now().strftime('%Y%m%d')}.html",
        mime="text/html",
        use_container_width=True
    )
