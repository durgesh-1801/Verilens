import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from scipy import stats
import time

st.set_page_config(page_title="Anomaly Detection", page_icon="🔍", layout="wide")

st.title("🔍 AI-Powered Anomaly Detection")

# ==========================================
# DEPARTMENT FILTER (NEW)
# ==========================================
selected_department = st.session_state.get('selected_department', 'All Departments')
if selected_department != "All Departments":
    st.info(f"🏛️ Analysis Mode: **{selected_department}** Department")

# Check if data exists
if st.session_state.get('data') is None:
    st.warning("⚠️ Please upload data on the home page first!")
    st.stop()

df = st.session_state.data.copy()

# ==========================================
# APPLY DEPARTMENT FILTER (NEW)
# ==========================================
original_count = len(df)
if selected_department != "All Departments":
    if 'department' in df.columns:
        df = df[df['department'] == selected_department].copy()
        if len(df) == 0:
            st.error(f"❌ No transactions found for {selected_department} department")
            st.stop()
        st.success(f"✓ Filtered to {len(df)} transactions from {selected_department} department (out of {original_count} total)")
    else:
        st.warning("⚠️ Department column not found in data. Showing all departments.")

# Sidebar configuration
st.sidebar.header("🎛️ Detection Settings")

# Algorithm selection
algorithm = st.sidebar.selectbox(
    "Detection Algorithm",
    [
        "Ensemble (Recommended)",
        "Isolation Forest",
        "Local Outlier Factor",
        "Statistical (Z-Score)",
        "IQR Method",
        "Custom Rules"
    ]
)

# Contamination rate
contamination = st.sidebar.slider(
    "Expected Anomaly Rate (%)",
    1, 30, 10,
    help="Percentage of data points expected to be anomalies"
) / 100

# Feature selection
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

if not numeric_cols:
    st.error("❌ No numeric columns found in the data!")
    st.stop()

selected_features = st.sidebar.multiselect(
    "Select Features for Detection",
    numeric_cols,
    default=numeric_cols[:min(5, len(numeric_cols))]
)

if not selected_features:
    st.warning("Please select at least one feature")
    st.stop()

# Advanced settings
with st.sidebar.expander("⚙️ Advanced Settings"):
    if algorithm == "Isolation Forest":
        n_estimators = st.slider("Number of Trees", 50, 200, 100)
        max_samples = st.slider("Max Samples", 100, 1000, 256)
    elif algorithm == "Local Outlier Factor":
        n_neighbors = st.slider("Number of Neighbors", 5, 50, 20)
    elif algorithm == "Statistical (Z-Score)":
        z_threshold = st.slider("Z-Score Threshold", 1.0, 5.0, 3.0)
    elif algorithm == "IQR Method":
        iqr_multiplier = st.slider("IQR Multiplier", 1.0, 3.0, 1.5)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Feature Analysis")
    
    # Prepare data
    feature_df = df[selected_features].copy()
    feature_df = feature_df.fillna(feature_df.median())
    
    # Display feature statistics
    stats_df = feature_df.describe().T
    stats_df['missing'] = df[selected_features].isnull().sum()
    st.dataframe(stats_df, use_container_width=True)

with col2:
    st.subheader("📈 Feature Distribution")
    selected_viz_feature = st.selectbox("Select Feature to Visualize", selected_features)
    
    fig = px.box(df, y=selected_viz_feature, title=f"Distribution of {selected_viz_feature}")
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================
# RUN DETECTION BUTTON (UPDATED WORDING)
# ==========================================
if st.button("🔍 Run AI Risk Scan", type="primary", use_container_width=True):
    
    with st.spinner("🔄 Running AI risk analysis..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Prepare data
        status_text.text("Preparing data for AI analysis...")
        progress_bar.progress(10)
        
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(feature_df)
        
        time.sleep(0.3)
        progress_bar.progress(30)
        
        # Run detection based on algorithm
        status_text.text(f"Running {algorithm}...")
        
        if algorithm == "Ensemble (Recommended)":
            # Run multiple algorithms
            predictions_list = []
            
            # Isolation Forest
            iso_model = IsolationForest(contamination=contamination, random_state=42)
            pred_iso = iso_model.fit_predict(scaled_data)
            predictions_list.append(pred_iso)
            progress_bar.progress(50)
            
            # LOF
            lof_model = LocalOutlierFactor(n_neighbors=20, contamination=contamination)
            pred_lof = lof_model.fit_predict(scaled_data)
            predictions_list.append(pred_lof)
            progress_bar.progress(70)
            
            # Z-Score
            z_scores = np.abs(stats.zscore(scaled_data))
            pred_zscore = np.where(np.any(z_scores > 3, axis=1), -1, 1)
            predictions_list.append(pred_zscore)
            progress_bar.progress(85)
            
            # Ensemble voting
            predictions_array = np.array(predictions_list)
            final_predictions = np.where(
                np.sum(predictions_array == -1, axis=0) >= 2, -1, 1
            )
            anomaly_scores = np.sum(predictions_array == -1, axis=0) / len(predictions_list)
            
        elif algorithm == "Isolation Forest":
            model = IsolationForest(
                contamination=contamination,
                n_estimators=n_estimators,
                max_samples=max_samples,
                random_state=42
            )
            final_predictions = model.fit_predict(scaled_data)
            anomaly_scores = -model.decision_function(scaled_data)
            
        elif algorithm == "Local Outlier Factor":
            model = LocalOutlierFactor(
                n_neighbors=n_neighbors,
                contamination=contamination
            )
            final_predictions = model.fit_predict(scaled_data)
            anomaly_scores = -model.negative_outlier_factor_
            
        elif algorithm == "Statistical (Z-Score)":
            z_scores = np.abs(stats.zscore(scaled_data))
            final_predictions = np.where(np.any(z_scores > z_threshold, axis=1), -1, 1)
            anomaly_scores = np.max(z_scores, axis=1)
            
        elif algorithm == "IQR Method":
            Q1 = np.percentile(scaled_data, 25, axis=0)
            Q3 = np.percentile(scaled_data, 75, axis=0)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - iqr_multiplier * IQR
            upper_bound = Q3 + iqr_multiplier * IQR
            
            outside_bounds = (scaled_data < lower_bound) | (scaled_data > upper_bound)
            final_predictions = np.where(np.any(outside_bounds, axis=1), -1, 1)
            anomaly_scores = np.sum(outside_bounds, axis=1) / scaled_data.shape[1]
        
        else:  # Custom Rules
            final_predictions = np.ones(len(df))
            anomaly_scores = np.zeros(len(df))
        
        progress_bar.progress(100)
        status_text.text("✅ AI risk scan complete!")
        time.sleep(0.5)
        status_text.empty()
        progress_bar.empty()
        
        # Add results to dataframe
        df['is_anomaly'] = final_predictions
        df['anomaly_score'] = anomaly_scores
        
        # ==========================================
        # GENERATE AI EXPLANATIONS (NEW)
        # ==========================================
        reasons = []
        for idx, row in df.iterrows():
            if row['is_anomaly'] == -1:
                reason_parts = []
                
                # Amount-based reasoning
                if 'amount' in df.columns:
                    amount = row['amount']
                    dept_mean = df[df['department'] == row.get('department', '')]['amount'].mean() if 'department' in df.columns else df['amount'].mean()
                    if amount > dept_mean * 2:
                        reason_parts.append(f"Amount ${amount:,.2f} significantly exceeds department baseline")
                
                # Vendor-based reasoning
                if 'vendor' in df.columns:
                    vendor = row.get('vendor', '')
                    if 'Unknown' in str(vendor) or pd.isna(vendor):
                        reason_parts.append("Unknown or unregistered vendor")
                
                # Payment method reasoning
                if 'payment_method' in df.columns and 'amount' in df.columns:
                    if 'Wire Transfer' in str(row.get('payment_method', '')) and row.get('amount', 0) > 50000:
                        reason_parts.append("Large wire transfer requires scrutiny")
                
                # Approval status reasoning
                if 'approval_status' in df.columns:
                    if str(row.get('approval_status', '')).lower() == 'pending':
                        reason_parts.append("High-value transaction pending approval")
                
                # Statistical reasoning
                if row['anomaly_score'] > 0.8:
                    reason_parts.append("Extreme statistical deviation from normal patterns")
                elif row['anomaly_score'] > 0.5:
                    reason_parts.append("Significant deviation from expected behavior")
                
                if not reason_parts:
                    reason_parts.append("Anomalous pattern detected by AI algorithms")
                
                reasons.append("; ".join(reason_parts))
            else:
                reasons.append("")
        
        df['ai_reason'] = reasons
        
        # Update session state with filtered data
        if selected_department != "All Departments":
            # Merge results back to original data
            original_df = st.session_state.data.copy()
            original_df.loc[df.index, 'is_anomaly'] = df['is_anomaly']
            original_df.loc[df.index, 'anomaly_score'] = df['anomaly_score']
            original_df.loc[df.index, 'ai_reason'] = df['ai_reason']
            st.session_state.data = original_df
        else:
            st.session_state.data = df
        
        st.session_state.anomaly_count = np.sum(final_predictions == -1)
        
        # Create alerts with AI explanations
        anomaly_indices = np.where(final_predictions == -1)[0]
        alerts = []
        for idx in anomaly_indices:
            severity = 'high' if anomaly_scores[idx] > 0.8 else 'medium' if anomaly_scores[idx] > 0.5 else 'low'
            actual_idx = df.index[idx]
            alerts.append({
                'id': int(actual_idx),
                'severity': severity,
                'score': float(anomaly_scores[idx]),
                'timestamp': pd.Timestamp.now().isoformat(),
                'reason': df.loc[actual_idx, 'ai_reason'] if 'ai_reason' in df.columns else 'Anomaly detected',
                'department': df.loc[actual_idx, 'department'] if 'department' in df.columns else 'Unknown'
            })
        st.session_state.alerts = alerts
        
        # SUCCESS MESSAGE (NO BALLOONS)
        st.success(f"✓ AI Risk Scan complete! Found {np.sum(final_predictions == -1)} high-risk transactions")

# Display results
if 'is_anomaly' in df.columns:
    st.markdown("---")
    st.subheader("🎯 Detection Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total = len(df)
    anomalies = np.sum(df['is_anomaly'] == -1)
    normal = total - anomalies
    
    with col1:
        st.metric("Total Records", f"{total:,}")
    with col2:
        st.metric("Normal Transactions", f"{normal:,}", delta=f"{normal/total*100:.1f}%")
    with col3:
        st.metric("High-Risk Flagged", f"{anomalies:,}", delta=f"{anomalies/total*100:.1f}%", delta_color="inverse")
    with col4:
        if 'anomaly_score' in df.columns:
            avg_score = df[df['is_anomaly'] == -1]['anomaly_score'].mean()
            st.metric("Avg Risk Score", f"{avg_score:.3f}")
    
    # Visualization tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Scatter Plot", "📈 Distribution", "🎯 High-Risk Details", "📋 Data Table"])
    
    with tab1:
        st.subheader("Risk Scatter Plot")
        
        if len(selected_features) >= 2:
            x_axis = st.selectbox("X-Axis", selected_features, index=0, key="scatter_x")
            y_axis = st.selectbox("Y-Axis", selected_features, index=min(1, len(selected_features)-1), key="scatter_y")
            
            fig = px.scatter(
                df,
                x=x_axis,
                y=y_axis,
                color=df['is_anomaly'].map({1: 'Normal', -1: 'High-Risk'}),
                color_discrete_map={'Normal': '#00cc96', 'High-Risk': '#ef553b'},
                title=f"Risk Detection: {x_axis} vs {y_axis}",
                hover_data=df.columns.tolist()[:5]
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Select at least 2 features for scatter plot")
    
    with tab2:
        st.subheader("Risk Score Distribution")
        
        if 'anomaly_score' in df.columns:
            fig = px.histogram(
                df,
                x='anomaly_score',
                color=df['is_anomaly'].map({1: 'Normal', -1: 'High-Risk'}),
                nbins=50,
                title="Risk Score Distribution",
                color_discrete_map={'Normal': '#00cc96', 'High-Risk': '#ef553b'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Top High-Risk Transactions")
        
        anomaly_df = df[df['is_anomaly'] == -1].copy()
        if 'anomaly_score' in anomaly_df.columns:
            anomaly_df = anomaly_df.sort_values('anomaly_score', ascending=False)
        
        # Display with AI reasons if available
        display_cols = anomaly_df.columns.tolist()
        if 'ai_reason' in display_cols:
            # Move ai_reason to front for visibility
            display_cols.remove('ai_reason')
            display_cols.insert(0, 'ai_reason')
            anomaly_df = anomaly_df[display_cols]
        
        st.dataframe(
            anomaly_df.head(20).style.background_gradient(subset=['anomaly_score'] if 'anomaly_score' in anomaly_df.columns else [], cmap='Reds'),
            use_container_width=True
        )
        
        # Download anomalies
        st.download_button(
            label="📥 Download High-Risk Transactions",
            data=anomaly_df.to_csv(index=False),
            file_name=f"high_risk_transactions_{selected_department.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )
    
    with tab4:
        st.subheader("Complete Results")
        
        show_only_anomalies = st.checkbox("Show only high-risk transactions", key="table_filter")
        
        display_df = df[df['is_anomaly'] == -1] if show_only_anomalies else df
        st.dataframe(display_df, use_container_width=True, height=400)

# ==========================================
# HELP SECTION (NEW)
# ==========================================
st.markdown("---")
with st.expander("ℹ️ How AI Risk Scanning Works"):
    st.markdown("""
    ### AI-Powered Risk Detection
    
    This system uses multiple machine learning algorithms to identify suspicious transactions:
    
    **Algorithms Available:**
    - **Ensemble (Recommended)**: Combines Isolation Forest, LOF, and Z-Score for robust detection
    - **Isolation Forest**: Identifies outliers by isolating anomalies in decision trees
    - **Local Outlier Factor**: Detects anomalies based on local density deviation
    - **Statistical Methods**: Z-Score and IQR for mathematical outlier detection
    
    **Risk Scoring:**
    - **High Risk** (>0.8): Immediate attention required
    - **Medium Risk** (0.5-0.8): Review recommended
    - **Low Risk** (<0.5): Monitor for patterns
    
    **Why AI Flags Transactions:**
    - Amount deviates significantly from department baseline
    - Unknown or suspicious vendors
    - Unusual payment methods for transaction size
    - Approval mismatches
    - Statistical anomalies in transaction patterns
    """)
