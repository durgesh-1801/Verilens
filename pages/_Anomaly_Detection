"""
🔍 Anomaly Detection Page
"""

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
from datetime import datetime

st.set_page_config(page_title="Anomaly Detection", page_icon="🔍", layout="wide")

st.title("🔍 AI-Powered Anomaly Detection")

# Check data
if st.session_state.get('data') is None:
    st.warning("⚠️ Please upload data on the Home page first!")
    st.stop()

df = st.session_state.data.copy()

# ==========================================
# SIDEBAR SETTINGS
# ==========================================

st.sidebar.header("🎛️ Detection Settings")

# Algorithm selection
algorithm = st.sidebar.selectbox(
    "Detection Algorithm",
    [
        "Ensemble (Recommended)",
        "Isolation Forest",
        "Local Outlier Factor",
        "Statistical (Z-Score)",
        "IQR Method"
    ]
)

# Contamination
contamination = st.sidebar.slider(
    "Expected Anomaly Rate (%)",
    1, 30, 10
) / 100

# Get numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
exclude_cols = ['is_anomaly', 'anomaly_score']
numeric_cols = [c for c in numeric_cols if c not in exclude_cols]

if not numeric_cols:
    st.error("❌ No numeric columns found!")
    st.stop()

# Feature selection
selected_features = st.sidebar.multiselect(
    "Select Features",
    numeric_cols,
    default=numeric_cols[:min(5, len(numeric_cols))]
)

if not selected_features:
    st.warning("Please select at least one feature")
    st.stop()

# Advanced settings
with st.sidebar.expander("⚙️ Advanced Settings"):
    if algorithm == "Isolation Forest":
        n_estimators = st.slider("Trees", 50, 200, 100)
    elif algorithm == "Local Outlier Factor":
        n_neighbors = st.slider("Neighbors", 5, 50, 20)
    elif algorithm == "Statistical (Z-Score)":
        z_threshold = st.slider("Z-Score Threshold", 1.5, 4.0, 3.0)
    elif algorithm == "IQR Method":
        iqr_multiplier = st.slider("IQR Multiplier", 1.0, 3.0, 1.5)

# ==========================================
# FEATURE PREVIEW
# ==========================================

st.subheader("📊 Feature Statistics")

col1, col2 = st.columns([2, 1])

with col1:
    feature_df = df[selected_features].fillna(df[selected_features].median())
    st.dataframe(feature_df.describe().round(2), use_container_width=True)

with col2:
    st.metric("Features Selected", len(selected_features))
    st.metric("Total Records", f"{len(df):,}")
    
    missing = df[selected_features].isnull().sum().sum()
    if missing > 0:
        st.warning(f"⚠️ {missing} missing values")
    else:
        st.success("✅ No missing values")

st.markdown("---")

# ==========================================
# RUN DETECTION
# ==========================================

if st.button("🚀 Run Anomaly Detection", type="primary", use_container_width=True):
    
    with st.spinner("🔄 Detecting anomalies..."):
        
        progress = st.progress(0)
        status = st.empty()
        
        # Prepare data
        status.text("Preparing data...")
        progress.progress(10)
        
        feature_df = df[selected_features].fillna(df[selected_features].median())
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(feature_df)
        
        progress.progress(30)
        time.sleep(0.3)
        
        # Run algorithm
        status.text(f"Running {algorithm}...")
        
        if algorithm == "Ensemble (Recommended)":
            predictions_list = []
            scores_list = []
            
            # Isolation Forest
            iso = IsolationForest(contamination=contamination, random_state=42, n_estimators=100)
            pred_iso = iso.fit_predict(scaled_data)
            score_iso = -iso.decision_function(scaled_data)
            predictions_list.append(pred_iso)
            scores_list.append(score_iso)
            progress.progress(50)
            
            # LOF
            lof = LocalOutlierFactor(n_neighbors=20, contamination=contamination)
            pred_lof = lof.fit_predict(scaled_data)
            score_lof = -lof.negative_outlier_factor_
            predictions_list.append(pred_lof)
            scores_list.append(score_lof)
            progress.progress(70)
            
            # Z-Score
            z_scores = np.abs(stats.zscore(scaled_data, nan_policy='omit'))
            z_scores = np.nan_to_num(z_scores, nan=0)
            max_z = np.max(z_scores, axis=1)
            pred_z = np.where(max_z > 3, -1, 1)
            predictions_list.append(pred_z)
            scores_list.append(max_z)
            progress.progress(85)
            
            # Ensemble voting
            predictions_array = np.array(predictions_list)
            anomaly_votes = np.sum(predictions_array == -1, axis=0)
            final_predictions = np.where(anomaly_votes >= 2, -1, 1)
            
            # Normalize and average scores
            for i in range(len(scores_list)):
                scores_list[i] = (scores_list[i] - scores_list[i].min()) / (scores_list[i].max() - scores_list[i].min() + 1e-10)
            final_scores = np.mean(scores_list, axis=0)
            
        elif algorithm == "Isolation Forest":
            model = IsolationForest(contamination=contamination, n_estimators=n_estimators, random_state=42)
            final_predictions = model.fit_predict(scaled_data)
            final_scores = -model.decision_function(scaled_data)
            final_scores = (final_scores - final_scores.min()) / (final_scores.max() - final_scores.min() + 1e-10)
            progress.progress(85)
            
        elif algorithm == "Local Outlier Factor":
            model = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination)
            final_predictions = model.fit_predict(scaled_data)
            final_scores = -model.negative_outlier_factor_
            final_scores = (final_scores - final_scores.min()) / (final_scores.max() - final_scores.min() + 1e-10)
            progress.progress(85)
            
        elif algorithm == "Statistical (Z-Score)":
            z_scores = np.abs(stats.zscore(scaled_data, nan_policy='omit'))
            z_scores = np.nan_to_num(z_scores, nan=0)
            max_z = np.max(z_scores, axis=1)
            final_predictions = np.where(max_z > z_threshold, -1, 1)
            final_scores = max_z / (max_z.max() + 1e-10)
            progress.progress(85)
            
        elif algorithm == "IQR Method":
            Q1 = np.percentile(scaled_data, 25, axis=0)
            Q3 = np.percentile(scaled_data, 75, axis=0)
            IQR = Q3 - Q1
            lower = Q1 - iqr_multiplier * IQR
            upper = Q3 + iqr_multiplier * IQR
            outside = (scaled_data < lower) | (scaled_data > upper)
            final_predictions = np.where(np.any(outside, axis=1), -1, 1)
            final_scores = np.sum(outside, axis=1) / scaled_data.shape[1]
            progress.progress(85)
        
        # Save results
        status.text("Saving results...")
        
        df['is_anomaly'] = final_predictions
        df['anomaly_score'] = final_scores
        
        # Generate alerts
        alerts = []
        anomaly_indices = np.where(final_predictions == -1)[0]
        
        for idx in anomaly_indices:
            score = final_scores[idx]
            severity = 'high' if score >= 0.8 else 'medium' if score >= 0.5 else 'low'
            
            alert = {
                'id': int(idx),
                'severity': severity,
                'score': float(score),
                'timestamp': datetime.now().isoformat()
            }
            
            if 'transaction_id' in df.columns:
                alert['transaction_id'] = df.iloc[idx]['transaction_id']
            if 'amount' in df.columns:
                alert['amount'] = float(df.iloc[idx]['amount'])
            
            alerts.append(alert)
        
        alerts.sort(key=lambda x: x['score'], reverse=True)
        
        # Update session state
        st.session_state.data = df
        st.session_state.anomaly_count = int(np.sum(final_predictions == -1))
        st.session_state.alerts = alerts
        st.session_state.detection_run = True
        
        progress.progress(100)
        status.empty()
        progress.empty()
        
        st.success(f"✅ Found **{st.session_state.anomaly_count}** anomalies out of **{len(df)}** records!")
        st.balloons()

# ==========================================
# RESULTS DISPLAY
# ==========================================

if 'is_anomaly' in df.columns:
    
    st.markdown("---")
    st.header("🎯 Detection Results")
    
    # Metrics
    total = len(df)
    anomalies = int(np.sum(df['is_anomaly'] == -1))
    normal = total - anomalies
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", f"{total:,}")
    with col2:
        st.metric("Normal", f"{normal:,}")
    with col3:
        st.metric("Anomalies", f"{anomalies:,}")
    with col4:
        avg_score = df[df['is_anomaly'] == -1]['anomaly_score'].mean() if anomalies > 0 else 0
        st.metric("Avg Score", f"{avg_score:.3f}")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Scatter Plot", "📈 Score Distribution", "📋 Anomaly Table"])
    
    with tab1:
        if len(selected_features) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                x_axis = st.selectbox("X-Axis", selected_features, index=0)
            with col2:
                y_axis = st.selectbox("Y-Axis", selected_features, index=min(1, len(selected_features)-1))
            
            fig = px.scatter(
                df, x=x_axis, y=y_axis,
                color=df['is_anomaly'].map({1: 'Normal', -1: 'Anomaly'}),
                color_discrete_map={'Normal': '#00cc96', 'Anomaly': '#ff4b4b'},
                title=f"{x_axis} vs {y_axis}"
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Select at least 2 features for scatter plot")
    
    with tab2:
        fig = px.histogram(
            df, x='anomaly_score',
            color=df['is_anomaly'].map({1: 'Normal', -1: 'Anomaly'}),
            nbins=50,
            color_discrete_map={'Normal': '#00cc96', 'Anomaly': '#ff4b4b'},
            title="Anomaly Score Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        anomaly_df = df[df['is_anomaly'] == -1].sort_values('anomaly_score', ascending=False)
        st.dataframe(anomaly_df.head(50), use_container_width=True, height=400)
        
        st.download_button(
            "📥 Download Anomalies",
            data=anomaly_df.to_csv(index=False),
            file_name="anomalies.csv",
            mime="text/csv"
        )
