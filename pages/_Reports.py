"""
Audit Report Generation
Export transaction details, AI analysis, and audit history to PDF/Excel
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import database
from io import BytesIO
import numpy as np

# Authentication check
if not st.session_state.get('authenticated'):
    st.error("🔒 Access Denied - Please login first")
    
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/_Login.py")
    
    st.stop()
# ========== END AUTHENTICATION CHECK ==========


st.set_page_config(page_title="Audit Reports", page_icon="📄", layout="wide")

st.title("📄 Audit Report Generation")

# Check if database has data
try:
    summary = database.get_audit_summary()
    total_trans = summary['total_transactions']
except:
    total_trans = 0

if total_trans == 0:
    st.warning("⚠️ No audit data available. Run anomaly detection and save audit actions first.")
    
    # Fallback to session-based reporting if database is empty but session data exists
    if st.session_state.get('data') is not None:
        st.info("📊 Session data available - showing session-based report options below")
        use_session_data = True
    else:
        st.stop()
else:
    use_session_data = False

# Display summary
st.subheader("📊 Audit Database Summary")

if not use_session_data:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Transactions", f"{summary['total_transactions']:,}")

    with col2:
        high_sev = summary['severity_counts'].get('high', 0)
        st.metric("High Severity", f"{high_sev:,}")

    with col3:
        reviewed = summary['status_counts'].get('Reviewed', 0)
        st.metric("Reviewed", f"{reviewed:,}")

    with col4:
        escalated = summary['status_counts'].get('Escalated', 0)
        st.metric("Escalated", f"{escalated:,}")

st.markdown("---")

# Report Type Selection
st.subheader("📋 Generate Report")

report_type = st.radio(
    "Select Report Type",
    ["Single Transaction Report", "Bulk Transaction Export", "Audit Summary Report", "Custom Analysis Report"],
    horizontal=True
)

st.markdown("---")

# ==========================================
# SINGLE TRANSACTION REPORT
# ==========================================
if report_type == "Single Transaction Report":
    st.markdown("### 📄 Single Transaction Audit Report")
    
    # Get all transactions for selection
    all_trans = database.get_all_transactions() if not use_session_data else pd.DataFrame()
    
    if len(all_trans) == 0 and not use_session_data:
        st.info("No transactions in database")
    else:
        if use_session_data:
            st.info("Using session data - save audit information to database for persistent reports")
            all_trans = st.session_state.data
            if 'is_anomaly' in all_trans.columns:
                all_trans = all_trans[all_trans['is_anomaly'] == -1].reset_index()
        
        if len(all_trans) == 0:
            st.info("No flagged transactions available")
        else:
            # Transaction selector
            trans_options = []
            for idx, row in all_trans.iterrows():
                trans_id = row.get('transaction_id', idx)
                dept = row.get('department', 'Unknown')
                amt = row.get('amount', 0)
                sev = row.get('severity', 'N/A')
                sev_display = (sev or "unknown").upper()
                trans_options.append(f"ID {trans_id} - {dept} - ${amt:,.2f} - {sev_display}")

            
            selected_idx = st.selectbox(
                "Select Transaction",
                range(len(trans_options)),
                format_func=lambda x: trans_options[x]
            )
            
            selected_trans_id = all_trans.iloc[selected_idx].get('transaction_id', all_trans.iloc[selected_idx].name)
            
            # Get full transaction details
            if not use_session_data:
                full_data = database.get_transaction_with_audit(selected_trans_id)
            else:
                full_data = {
                    'transaction': all_trans.iloc[selected_idx].to_dict(),
                    'audit_actions': []
                }
            
            if full_data:
                trans = full_data['transaction']
                audit_actions = full_data['audit_actions']
                
                # Display preview
                st.markdown("#### Report Preview")
                
                with st.expander("📊 Transaction Details", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Transaction ID:** {trans.get('transaction_id', 'N/A')}")
                        st.markdown(f"**Department:** {trans.get('department', 'Unknown')}")
                        st.markdown(f"**Amount:** ${trans.get('amount', 0):,.2f}")
                        st.markdown(f"**Vendor:** {trans.get('vendor', 'Unknown')}")
                    with col2:
                        st.markdown(f"**Date:** {trans.get('transaction_date', 'N/A')}")
                        st.markdown(f"**Risk Score:** {trans.get('risk_score', 0):.4f}")
                        st.markdown(f"**Severity:** {trans.get('severity', 'N/A').upper()}")
                        st.markdown(f"**Purpose:** {trans.get('purpose', 'N/A')}")
                
                with st.expander("🤖 AI Analysis"):
                    st.markdown(f"**Detection Time:** {trans.get('detection_timestamp', 'N/A')}")
                    st.markdown(f"**AI Reason:**")
                    st.info(trans.get('ai_reason', 'Anomaly detected'))
                
                with st.expander("👨‍💼 Audit History"):
                    if len(audit_actions) > 0:
                        for action in audit_actions:
                            st.markdown(f"**{action.get('action_type', 'ACTION').upper()}** - {action.get('created_at', 'N/A')}")
                            st.markdown(f"Status: {action.get('status', 'N/A')}")
                            if action.get('auditor_notes'):
                                st.text_area("Notes:", action['auditor_notes'], disabled=True, key=f"note_{action.get('id', 'N/A')}")
                            st.markdown("---")
                    else:
                        st.info("No audit actions recorded yet")
                
                # Export options
                st.markdown("---")
                st.markdown("#### 📥 Export Options")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Excel export
                    if st.button("📊 Export to Excel", use_container_width=True):
                        output = BytesIO()
                        
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            # Transaction sheet
                            trans_df = pd.DataFrame([trans])
                            trans_df.to_excel(writer, sheet_name='Transaction', index=False)
                            
                            # Audit actions sheet
                            if len(audit_actions) > 0:
                                audit_df = pd.DataFrame(audit_actions)
                                audit_df.to_excel(writer, sheet_name='Audit History', index=False)
                        
                        excel_data = output.getvalue()
                        
                        st.download_button(
                            label="⬇️ Download Excel Report",
                            data=excel_data,
                            file_name=f"audit_report_txn_{selected_trans_id}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                
                with col2:
                    # CSV export
                    if st.button("📄 Export to CSV", use_container_width=True):
                        # Combine transaction and latest audit info
                        combined_data = {**trans}
                        if len(audit_actions) > 0:
                            latest_audit = audit_actions[0]
                            combined_data['audit_status'] = latest_audit.get('status', 'N/A')
                            combined_data['auditor_notes'] = latest_audit.get('auditor_notes', '')
                            combined_data['review_timestamp'] = latest_audit.get('review_timestamp', 'N/A')
                        
                        combined_df = pd.DataFrame([combined_data])
                        csv_data = combined_df.to_csv(index=False)
                        
                        st.download_button(
                            label="⬇️ Download CSV Report",
                            data=csv_data,
                            file_name=f"audit_report_txn_{selected_trans_id}_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )

# ==========================================
# BULK TRANSACTION EXPORT
# ==========================================
elif report_type == "Bulk Transaction Export":
    st.markdown("### 📊 Bulk Transaction Export")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    if not use_session_data:
        all_depts = database.get_all_transactions()['department'].unique() if len(database.get_all_transactions()) > 0 else []
    else:
        all_depts = st.session_state.data['department'].unique() if 'department' in st.session_state.data.columns else []
    
    with col1:
        dept_filter = st.selectbox(
            "Department",
            ["All"] + list(all_depts)
        )
    
    with col2:
        severity_filter = st.selectbox(
            "Severity",
            ["All", "high", "medium", "low"]
        )
    
    with col3:
        include_audit = st.checkbox("Include Audit Info", value=True)
    
    # Build filters
    filters = {}
    if dept_filter != "All":
        filters['department'] = dept_filter
    if severity_filter != "All":
        filters['severity'] = severity_filter
    
    # Get filtered transactions
    if not use_session_data:
        trans_df = database.get_all_transactions(filters)
    else:
        trans_df = st.session_state.data
        if dept_filter != "All" and 'department' in trans_df.columns:
            trans_df = trans_df[trans_df['department'] == dept_filter]
        if severity_filter != "All" and 'severity' in trans_df.columns:
            trans_df = trans_df[trans_df['severity'] == severity_filter]
    
    st.info(f"📊 Found {len(trans_df)} transactions matching filters")
    
    # Preview
    st.dataframe(trans_df.head(10), use_container_width=True)
    
    # Export
    if len(trans_df) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel export
            output = BytesIO()
            trans_df.to_excel(output, index=False, engine='openpyxl')
            excel_data = output.getvalue()
            
            st.download_button(
                label="📊 Download Excel",
                data=excel_data,
                file_name=f"bulk_transactions_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            # CSV export
            csv_data = trans_df.to_csv(index=False)
            
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"bulk_transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# ==========================================
# AUDIT SUMMARY REPORT
# ==========================================
elif report_type == "Audit Summary Report":
    st.markdown("### 📈 Audit Summary Report")
    
    st.markdown("#### Overall Statistics")
    
    # Get all data
    if not use_session_data:
        all_trans = database.get_all_transactions()
    else:
        all_trans = st.session_state.data
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Transactions", len(all_trans))
        if 'amount' in all_trans.columns:
            st.metric("Total Amount", f"${all_trans['amount'].sum():,.2f}")
    
    with col2:
        if 'risk_score' in all_trans.columns:
            avg_risk = all_trans['risk_score'].mean()
            st.metric("Avg Risk Score", f"{avg_risk:.3f}")
            high_risk_count = len(all_trans[all_trans['risk_score'] > 0.8])
            st.metric("High Risk (>0.8)", high_risk_count)
        elif 'anomaly_score' in all_trans.columns:
            avg_risk = all_trans['anomaly_score'].mean()
            st.metric("Avg Anomaly Score", f"{avg_risk:.3f}")
    
    with col3:
        if 'department' in all_trans.columns:
            dept_count = all_trans['department'].nunique()
            st.metric("Departments", dept_count)
        if 'vendor' in all_trans.columns:
            vendor_count = all_trans['vendor'].nunique()
            st.metric("Unique Vendors", vendor_count)
    
    # Department breakdown
    if 'department' in all_trans.columns:
        st.markdown("#### Department Breakdown")
        dept_summary = all_trans.groupby('department').agg({
            all_trans.columns[0]: 'count',
            'amount': 'sum' if 'amount' in all_trans.columns else 'count'
        })
        
        if 'risk_score' in all_trans.columns:
            dept_summary['avg_risk_score'] = all_trans.groupby('department')['risk_score'].mean()
        
        st.dataframe(dept_summary, use_container_width=True)
    
    # Export summary
    st.markdown("---")
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        all_trans.to_excel(writer, sheet_name='All Transactions', index=False)
        if 'department' in all_trans.columns:
            dept_summary.to_excel(writer, sheet_name='Department Summary')
    
    excel_data = output.getvalue()
    
    st.download_button(
        label="📊 Download Complete Audit Summary",
        data=excel_data,
        file_name=f"audit_summary_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# ==========================================
# CUSTOM ANALYSIS REPORT (NEW)
# ==========================================
else:  # Custom Analysis Report
    st.markdown("### 📊 Custom Analysis Report")
    
    # Get data
    if not use_session_data:
        df = database.get_all_transactions()
    else:
        df = st.session_state.data
    
    if len(df) == 0:
        st.info("No data available")
    else:
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
        if 'risk_score' in df.columns:
            anomaly_count = len(df[df['risk_score'] > 0.5])
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
            if 'is_anomaly' in df.columns or 'risk_score' in df.columns:
                if 'is_anomaly' in df.columns:
                    anomaly_df = df[df['is_anomaly'] == -1]
                else:
                    anomaly_df = df[df['risk_score'] > 0.5]
                
                st.markdown(f"**Total Anomalies:** {len(anomaly_df):,}")
                st.markdown("**Top Anomalies:**")
                
                if 'anomaly_score' in anomaly_df.columns:
                    st.dataframe(anomaly_df.nlargest(10, 'anomaly_score'), use_container_width=True)
                elif 'risk_score' in anomaly_df.columns:
                    st.dataframe(anomaly_df.nlargest(10, 'risk_score'), use_container_width=True)
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
            2. **Short-term:** Implement additional validation rules for high-risk vendors
            3. **Medium-term:** Enhanced monitoring for departments with elevated risk scores
            4. **Long-term:** Develop predictive models for proactive detection
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
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='All Data', index=False)
                
                if 'is_anomaly' in df.columns:
                    df[df['is_anomaly'] == -1].to_excel(writer, sheet_name='Anomalies', index=False)
                elif 'risk_score' in df.columns:
                    df[df['risk_score'] > 0.5].to_excel(writer, sheet_name='High Risk', index=False)
                
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

# ==========================================
# DATABASE MANAGEMENT
# ==========================================
st.markdown("---")
st.subheader("⚙️ Database Management")

with st.expander("🗄️ Database Tools"):
    st.warning("⚠️ Use these tools with caution")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View Database Stats"):
            if not use_session_data:
                st.json(summary)
            else:
                st.info("Database empty - using session data")
    
    with col2:
        if st.button("💾 Export Complete Database"):
            if not use_session_data:
                all_data = database.get_all_transactions()
                csv = all_data.to_csv(index=False)
                st.download_button(
                    "Download Database CSV",
                    data=csv,
                    file_name=f"database_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    with col3:
        if st.button("🗑️ Clear Database (Danger)", type="secondary"):
            if st.checkbox("I understand this will delete all audit data"):
                database.clear_database()
                st.success("Database cleared")
                st.rerun()
