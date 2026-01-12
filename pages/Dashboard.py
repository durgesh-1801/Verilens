"""
📊 Dashboard Page
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Fraud Detection Dashboard")

# Check data
if st.session_state.get('data') is None:
    st.warning("⚠️ Please upload data on the Home page first!")
    st.stop()

df = st.session_state.data

# ==========================================
# TOP METRICS
# ==========================================

st.subheader("📈 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

total_records = len(df)
anomaly_count = st.session_state.get('anomaly_count', 0)

with col1:
    st.metric("Total Transactions", f"{total_records:,}")

with col2:
    if 'amount' in df.columns:
        st.metric("Total Amount", f"₹{df['amount'].sum():,.0f}")
    else:
        st.metric("Columns", len(df.columns))

with col3:
    st.metric("Anomalies Detected", f"{anomaly_count:,}")

with col4:
    alerts = st.session_state.get('alerts', [])
    high_alerts = len([a for a in alerts if a.get('severity') == 'high'])
    st.metric("High Risk Alerts", high_alerts)

with col5:
    quality = (1 - df.isnull().sum().sum() / df.size) * 100
    st.metric("Data Quality", f"{quality:.1f}%")

st.markdown("---")

# ==========================================
# CHARTS ROW 1
# ==========================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Amount Distribution")
    
    if 'amount' in df.columns:
        fig = px.histogram(
            df, x='amount', nbins=50,
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(
            xaxis_title="Amount",
            yaxis_title="Count",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No 'amount' column found")

with col2:
    st.subheader("🔵 Transaction Status")
    
    if 'is_anomaly' in df.columns:
        normal = len(df[df['is_anomaly'] == 1])
        anomaly = len(df[df['is_anomaly'] == -1])
        labels = ['Normal', 'Anomaly']
        values = [normal, anomaly]
    else:
        labels = ['Pending Analysis']
        values = [total_records]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker_colors=['#00cc96', '#ff4b4b']
    )])
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# CHARTS ROW 2
# ==========================================

col1, col2 = st.columns(2)

with col1:
    if 'category' in df.columns:
        st.subheader("📂 By Category")
        cat_counts = df['category'].value_counts()
        fig = px.bar(
            x=cat_counts.index,
            y=cat_counts.values,
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(
            xaxis_title="Category",
            yaxis_title="Count",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if 'department' in df.columns:
        st.subheader("🏢 By Department")
        dept_counts = df['department'].value_counts()
        fig = px.pie(
            names=dept_counts.index,
            values=dept_counts.values,
            hole=0.4
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# CORRELATION HEATMAP
# ==========================================

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
exclude_cols = ['is_anomaly', 'anomaly_score']
numeric_cols = [c for c in numeric_cols if c not in exclude_cols]

if len(numeric_cols) >= 2:
    st.subheader("🎯 Feature Correlation")
    
    corr_matrix = df[numeric_cols].corr()
    fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        color_continuous_scale='RdBu_r'
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# DATA TABLE
# ==========================================

st.subheader("📋 Transaction Data")

col1, col2 = st.columns(2)

with col1:
    if 'category' in df.columns:
        categories = ['All'] + df['category'].unique().tolist()
        selected_cat = st.selectbox("Filter by Category", categories)
    else:
        selected_cat = 'All'

with col2:
    show_anomalies = st.checkbox("Show Anomalies Only")

# Apply filters
filtered_df = df.copy()

if selected_cat != 'All' and 'category' in df.columns:
    filtered_df = filtered_df[filtered_df['category'] == selected_cat]

if show_anomalies and 'is_anomaly' in df.columns:
    filtered_df = filtered_df[filtered_df['is_anomaly'] == -1]

st.dataframe(filtered_df.head(100), use_container_width=True, height=400)

st.download_button(
    "📥 Download Filtered Data",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_data.csv",
    mime="text/csv"
)
