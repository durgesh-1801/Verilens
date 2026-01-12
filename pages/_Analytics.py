import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")

st.title("📈 Advanced Analytics & Insights")

if st.session_state.get('data') is None:
    st.warning("⚠️ Please upload data on the home page first!")
    st.stop()

df = st.session_state.data.copy()

# Analytics Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔬 Deep Analysis", 
    "📊 Pattern Recognition", 
    "🎯 Feature Importance",
    "📉 Time Series Analysis"
])

with tab1:
    st.subheader("🔬 Statistical Deep Dive")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Descriptive Statistics")
        st.dataframe(df[numeric_cols].describe(), use_container_width=True)
    
    with col2:
        st.markdown("#### Distribution Analysis")
        selected_col = st.selectbox("Select Column", numeric_cols)
        
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Histogram", "Box Plot"))
        
        fig.add_trace(
            go.Histogram(x=df[selected_col], name="Distribution", marker_color='#667eea'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Box(y=df[selected_col], name="Box Plot", marker_color='#764ba2'),
            row=1, col=2
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Correlation Analysis
    st.markdown("#### Correlation Analysis")
    
    if len(numeric_cols) >= 2:
        corr_method = st.selectbox("Correlation Method", ["pearson", "spearman", "kendall"])
        corr_matrix = df[numeric_cols].corr(method=corr_method)
        
        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            aspect="auto",
            color_continuous_scale="RdBu_r",
            title=f"{corr_method.capitalize()} Correlation Matrix"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📊 Pattern Recognition")
    
    if 'is_anomaly' in df.columns:
        st.markdown("#### Anomaly Patterns by Feature")
        
        anomaly_df = df[df['is_anomaly'] == -1]
        normal_df = df[df['is_anomaly'] == 1]
        
        selected_feature = st.selectbox("Select Feature for Pattern Analysis", numeric_cols, key="pattern_feature")
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=normal_df[selected_feature],
            name='Normal',
            opacity=0.7,
            marker_color='#00cc96'
        ))
        
        fig.add_trace(go.Histogram(
            x=anomaly_df[selected_feature],
            name='Anomaly',
            opacity=0.7,
            marker_color='#ef553b'
        ))
        
        fig.update_layout(
            barmode='overlay',
            title=f"Distribution Comparison: {selected_feature}",
            xaxis_title=selected_feature,
            yaxis_title="Count"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Pattern Statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Normal Transaction Statistics**")
            st.dataframe(normal_df[numeric_cols].describe(), use_container_width=True)
        
        with col2:
            st.markdown("**Anomaly Statistics**")
            st.dataframe(anomaly_df[numeric_cols].describe(), use_container_width=True)
    else:
        st.info("Run anomaly detection first to see pattern analysis")

with tab3:
    st.subheader("🎯 Feature Importance Analysis")
    
    if 'is_anomaly' in df.columns and len(numeric_cols) > 0:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder
        
        # Prepare data
        X = df[numeric_cols].fillna(df[numeric_cols].median())
        y = df['is_anomaly']
        
        # Train a simple model to get feature importance
        with st.spinner("Calculating feature importance..."):
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
            rf_model.fit(X, y)
            
            importance_df = pd.DataFrame({
                'Feature': numeric_cols,
                'Importance': rf_model.feature_importances_
            }).sort_values('Importance', ascending=True)
            
            fig = px.bar(
                importance_df,
                x='Importance',
                y='Feature',
                orientation='h',
                title="Feature Importance for Anomaly Detection",
                color='Importance',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Key Insights")
            top_features = importance_df.tail(3)['Feature'].tolist()
            st.success(f"**Top predictive features:** {', '.join(top_features)}")
    else:
        st.info("Run anomaly detection first to see feature importance")

with tab4:
    st.subheader("📉 Time Series Analysis")
    
    # Find date columns
    date_cols = []
    for col in df.columns:
        try:
            pd.to_datetime(df[col])
            date_cols.append(col)
        except:
            continue
    
    if date_cols:
        date_col = st.selectbox("Select Date Column", date_cols)
        value_col = st.selectbox("Select Value Column", numeric_cols, key="ts_value")
        
        temp_df = df.copy()
        temp_df[date_col] = pd.to_datetime(temp_df[date_col])
        temp_df = temp_df.sort_values(date_col)
        
        # Time series plot
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=temp_df[date_col],
            y=temp_df[value_col],
            mode='lines',
            name=value_col,
            line=dict(color='#667eea')
        ))
        
        # Add anomaly markers if available
        if 'is_anomaly' in temp_df.columns:
            anomaly_mask = temp_df['is_anomaly'] == -1
            fig.add_trace(go.Scatter(
                x=temp_df[anomaly_mask][date_col],
                y=temp_df[anomaly_mask][value_col],
                mode='markers',
                name='Anomalies',
                marker=dict(color='red', size=10, symbol='x')
            ))
        
        fig.update_layout(
            title=f"Time Series: {value_col}",
            xaxis_title="Date",
            yaxis_title=value_col,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Rolling statistics
        st.markdown("#### Rolling Statistics")
        window = st.slider("Rolling Window Size", 7, 90, 30)
        
        temp_df['rolling_mean'] = temp_df[value_col].rolling(window=window).mean()
        temp_df['rolling_std'] = temp_df[value_col].rolling(window=window).std()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=temp_df[date_col], y=temp_df[value_col], name='Actual', opacity=0.5))
        fig.add_trace(go.Scatter(x=temp_df[date_col], y=temp_df['rolling_mean'], name='Rolling Mean', line=dict(width=2)))
        fig.add_trace(go.Scatter(x=temp_df[date_col], y=temp_df['rolling_mean'] + 2*temp_df['rolling_std'], 
                                  name='Upper Band', line=dict(dash='dash')))
        fig.add_trace(go.Scatter(x=temp_df[date_col], y=temp_df['rolling_mean'] - 2*temp_df['rolling_std'], 
                                  name='Lower Band', line=dict(dash='dash')))
        
        fig.update_layout(title="Rolling Statistics with Bands", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No date columns detected. Add a date column for time series analysis.")
