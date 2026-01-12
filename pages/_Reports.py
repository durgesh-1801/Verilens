"""
📋 Reports Page (CSV/Excel/HTML Only)
"""

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

# ==========================================
# CONFIGURATION
# ==========================================

st.subheader("📝 Report Configuration")

col1, col2 = st.columns(2)

with col1:
    report_title = st.text_input("Report Title", "Fraud Detection Analysis Report")
    report_author = st.text_input("Author", "AI Fraud Detection System")

with col2:
    report_date = st.date_input("Date", datetime.now())
    organization = st.text_input("Organization", "Government of India")

st.markdown("---")

# ==========================================
# PREVIEW
# ==========================================

st.subheader("📄 Report Preview")

# Calculate metrics
total_records = len(df)
anomaly_count = int(np.sum(df['is_anomaly'] == -1)) if 'is_anomaly' in df.columns else 0
anomaly_rate = (anomaly_count / total_records * 100) if total_records > 0 else 0
alerts = st.session_state.get('alerts', [])

# Summary
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Records", f"{total_records:,}")
with col2:
    st.metric("Anomalies", f"{anomaly_count:,}")
with col3:
    st.metric("Detection Rate", f"{anomaly_rate:.2f}%")
with col4:
    high_alerts = len([a for a in alerts if a.get('severity') == 'high'])
    st.metric("High Risk", high_alerts)

# Preview tabs
tab1, tab2, tab3 = st.tabs(["📊 Summary", "🔍 Anomalies", "⚠️ Alerts"])

with tab1:
    st.markdown(f"""
    ### Executive Summary
    
    **Report:** {report_title}  
    **Date:** {report_date}  
    **Author:** {report_author}  
    **Organization:** {organization}
    
    ---
    
    **Key Findings:**
    - Total transactions analyzed: **{total_records:,}**
    - Anomalies detected: **{anomaly_count:,}** ({anomaly_rate:.2f}%)
    - High-risk alerts: **{high_alerts}**
    
    **Detection Method:** Ensemble ML (Isolation Forest + LOF + Z-Score)
    """)

with tab2:
    if 'is_anomaly' in df.columns:
        anomaly_df = df[df['is_anomaly'] == -1]
        if len(anomaly_df) > 0:
            st.dataframe(anomaly_df.head(20), use_container_width=True)
        else:
            st.info("No anomalies detected")
    else:
        st.info("Run detection first")

with tab3:
    if alerts:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"🔴 **High:** {len([a for a in alerts if a['severity']=='high'])}")
        with col2:
            st.markdown(f"🟠 **Medium:** {len([a for a in alerts if a['severity']=='medium'])}")
        with col3:
            st.markdown(f"🟢 **Low:** {len([a for a in alerts if a['severity']=='low'])}")
        
        st.dataframe(pd.DataFrame(alerts).head(20), use_container_width=True)
    else:
        st.info("No alerts")

st.markdown("---")

# ==========================================
# EXPORT OPTIONS
# ==========================================

st.subheader("📥 Export Report")

col1, col2, col3 = st.columns(3)

# CSV Export
with col1:
    st.markdown("### 📊 CSV")
    
    csv_data = df.to_csv(index=False)
    st.download_button(
        "📥 Download Full Data",
        data=csv_data,
        file_name=f"report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    if 'is_anomaly' in df.columns:
        anomaly_csv = df[df['is_anomaly'] == -1].to_csv(index=False)
        st.download_button(
            "📥 Download Anomalies",
            data=anomaly_csv,
            file_name=f"anomalies_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Excel Export
with col2:
    st.markdown("### 📗 Excel")
    
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Summary
        summary = pd.DataFrame({
            'Metric': ['Report Title', 'Author', 'Date', 'Total Records', 'Anomalies', 'Rate (%)', 'High Alerts'],
            'Value': [report_title, report_author, str(report_date), total_records, anomaly_count, f"{anomaly_rate:.2f}", high_alerts]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # All data
        df.to_excel(writer, sheet_name='All Data', index=False)
        
        # Anomalies
        if 'is_anomaly' in df.columns:
            df[df['is_anomaly'] == -1].to_excel(writer, sheet_name='Anomalies', index=False)
        
        # Alerts
        if alerts:
            pd.DataFrame(alerts).to_excel(writer, sheet_name='Alerts', index=False)
    
    st.download_button(
        "📥 Download Excel",
        data=buffer.getvalue(),
        file_name=f"report_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# HTML Export
with col3:
    st.markdown("### 🌐 HTML")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{report_title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }}
            h1 {{ color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
            .metric {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px; text-align: center; display: inline-block; margin: 10px; min-width: 150px; }}
            .metric h2 {{ margin: 0; font-size: 2em; }}
            .metric p {{ margin: 5px 0 0 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th {{ background: #667eea; color: white; padding: 12px; }}
            td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ {report_title}</h1>
            <p><strong>Author:</strong> {report_author} | <strong>Date:</strong> {report_date} | <strong>Organization:</strong> {organization}</p>
            
            <h2>📊 Summary</h2>
            <div>
                <div class="metric"><h2>{total_records:,}</h2><p>Total Records</p></div>
                <div class="metric"><h2>{anomaly_count:,}</h2><p>Anomalies</p></div>
                <div class="metric"><h2>{anomaly_rate:.2f}%</h2><p>Detection Rate</p></div>
                <div class="metric"><h2>{high_alerts}</h2><p>High Risk</p></div>
            </div>
            
            <h2>📋 Data Preview</h2>
            {df.head(50).to_html(index=False)}
            
            <h2>🎯 Recommendations</h2>
            <ol>
                <li>Review high-priority alerts within 24 hours</li>
                <li>Investigate transactions with score > 0.8</li>
                <li>Implement additional validation rules</li>
            </ol>
            
            <hr>
            <p><em>Generated by AI Fraud Detection System | {datetime.now().strftime('%Y-%m-%d %H:%M')}</em></p>
        </div>
    </body>
    </html>
    """
    
    st.download_button(
        "📥 Download HTML",
        data=html_content,
        file_name=f"report_{datetime.now().strftime('%Y%m%d')}.html",
        mime="text/html",
        use_container_width=True
    )

st.markdown("---")

st.info("""
**Available Export Formats:**
- **CSV** - Raw data for further analysis
- **Excel** - Multi-sheet workbook with summary, data, and alerts
- **HTML** - Printable web page report
""")
