import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Fraud Detection Dashboard")

# Check if data exists
if st.session_state.get('data') is None:
    st.warning("⚠️ Please upload data on the home page first!")
    st.stop()

df = st.session_state.data

# Top metrics row
st.subheader("📈 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

# Calculate metrics
total_records = len(df)
numeric_cols = df.select_dtypes(include=[np.number]).columns

if 'amount' in df.columns:
    total_amount = df['amount'].sum()
    avg_amount = df['amount'].mean()
else:
    total_amount = 0
    avg_amount = 0

# Display metrics
with col1:
    st.metric(
        label="Total Transactions",
        value=f"{total_records:,}",
        delta="Live Data"
    )

with col2:
    st.metric(
        label="Total Amount",
        value=f"${total_amount:,.2f}" if total_amount else "N/A",
        delta=None
    )

with col3:
    anomaly_count = st.session_state.get('anomaly_count', 0)
    st.metric(
        label="Detected Anomalies",
        value=f"{anomaly_count:,}",
        delta=f"{(anomaly_count/total_records*100):.1f}%" if total_records > 0 else "0%",
        delta_color="inverse"
    )

with col4:
    st.metric(
        label="High Risk Alerts",
        value=len([a for a in st.session_state.get('alerts', []) if a.get('severity') == 'high']),
        delta="Needs Review",
        delta_color="inverse"
    )

with col5:
    st.metric(
        label="Data Quality Score",
        value=f"{(1 - df.isnull().sum().sum() / df.size) * 100:.1f}%",
        delta="Good" if (1 - df.isnull().sum().sum() / df.size) > 0.9 else "Check Data"
    )

st.markdown("---")

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Transaction Distribution")
    if 'amount' in df.columns:
        fig = px.histogram(
            df, 
            x='amount', 
            nbins=50,
            title="Amount Distribution",
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(
            xaxis_title="Amount",
            yaxis_title="Frequency",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Use first numeric column
        if len(numeric_cols) > 0:
            fig = px.histogram(
                df, 
                x=numeric_cols[0], 
                nbins=50,
                color_discrete_sequence=['#667eea']
            )
            st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🔵 Anomaly Status")
    if 'is_anomaly' in df.columns:
        anomaly_counts = df['is_anomaly'].value_counts()
        labels = ['Normal', 'Anomaly']
        values = [
            anomaly_counts.get(1, 0) + anomaly_counts.get(False, 0),
            anomaly_counts.get(-1, 0) + anomaly_counts.get(True, 0)
        ]
    else:
        labels = ['Pending Analysis']
        values = [total_records]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker_colors=['#00cc96', '#ef553b']
    )])
    fig.update_layout(
        title="Transaction Status",
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Trend Analysis")
    
    # Check for date column
    date_cols = df.select_dtypes(include=['datetime64', 'object']).columns
    date_col = None
    
    for col in date_cols:
        try:
            pd.to_datetime(df[col])
            date_col = col
            break
        except:
            continue
    
    if date_col and 'amount' in df.columns:
        temp_df = df.copy()
        temp_df[date_col] = pd.to_datetime(temp_df[date_col])
        trend_data = temp_df.groupby(temp_df[date_col].dt.date)['amount'].sum().reset_index()
        trend_data.columns = ['date', 'amount']
        
        fig = px.line(
            trend_data,
            x='date',
            y='amount',
            title="Daily Transaction Trend",
            color_discrete_sequence=['#667eea']
        )
        fig.update_traces(mode='lines+markers')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add date column for trend analysis")

with col2:
    st.subheader("🎯 Feature Correlation")
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu",
            title="Feature Correlation Heatmap"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need at least 2 numeric columns for correlation analysis")

# Risk Distribution
st.subheader("⚠️ Risk Level Distribution")

# Simulated risk levels based on data
if len(numeric_cols) > 0:
    # Create risk scores based on z-scores
    from scipy import stats
    
    risk_col = numeric_cols[0] if 'amount' not in df.columns else 'amount'
    z_scores = np.abs(stats.zscore(df[risk_col].fillna(df[risk_col].median())))
    
    risk_levels = pd.cut(
        z_scores,
        bins=[-np.inf, 1, 2, 3, np.inf],
        labels=['Low', 'Medium', 'High', 'Critical']
    )
    
    risk_counts = risk_levels.value_counts()
    
    fig = go.Figure(data=[
        go.Bar(
            x=risk_counts.index.tolist(),
            y=risk_counts.values,
            marker_color=['#00cc96', '#ffa15a', '#ef553b', '#ab63fa']
        )
    ])
    fig.update_layout(
        title="Risk Level Distribution",
        xaxis_title="Risk Level",
        yaxis_title="Count",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# Data Table with Filtering
st.subheader("📋 Transaction Data")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    if 'amount' in df.columns:
        amount_filter = st.slider(
            "Amount Range",
            float(df['amount'].min()),
            float(df['amount'].max()),
            (float(df['amount'].min()), float(df['amount'].max()))
        )
    else:
        amount_filter = None

with col2:
    if 'category' in df.columns:
        categories = ['All'] + df['category'].unique().tolist()
        selected_category = st.selectbox("Category", categories)
    else:
        selected_category = 'All'

with col3:
    show_anomalies_only = st.checkbox("Show Anomalies Only")

# Apply filters
filtered_df = df.copy()

if amount_filter and 'amount' in df.columns:
    filtered_df = filtered_df[
        (filtered_df['amount'] >= amount_filter[0]) & 
        (filtered_df['amount'] <= amount_filter[1])
    ]

if selected_category != 'All' and 'category' in df.columns:
    filtered_df = filtered_df[filtered_df['category'] == selected_category]

if show_anomalies_only and 'is_anomaly' in df.columns:
    filtered_df = filtered_df[filtered_df['is_anomaly'] == -1]

st.dataframe(filtered_df, use_container_width=True, height=400)

# Download button
st.download_button(
    label="📥 Download Filtered Data",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_transactions.csv",
    mime="text/csv"
)
