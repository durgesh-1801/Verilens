"""
📈 Analytics Page
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")

st.title("📈 Advanced Analytics")

if st.session_state.get('data') is None:
    st.warning("⚠️ Please upload data on the Home page first!")
    st.stop()

df = st.session_state.data.copy()
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
exclude = ['is_anomaly', 'anomaly_score']
numeric_cols = [c for c in numeric_cols if c not in exclude]

# Tabs
tab1, tab2, tab3 = st.tabs(["🔬 Statistics", "📊 Patterns", "🎯 Feature Importance"])

with tab1:
    st.subheader("🔬 Statistical Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Descriptive Statistics")
        if numeric_cols:
            st.dataframe(df[numeric_cols].describe().round(2), use_container_width=True)
    
    with col2:
        st.markdown("#### Distribution")
        if numeric_cols:
            selected_col = st.selectbox("Select Column", numeric_cols)
            
            fig = make_subplots(rows=1, cols=2, subplot_titles=("Histogram", "Box Plot"))
            fig.add_trace(go.Histogram(x=df[selected_col], marker_color='#667eea'), row=1, col=1)
            fig.add_trace(go.Box(y=df[selected_col], marker_color='#764ba2'), row=1, col=2)
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Correlation
    if len(numeric_cols) >= 2:
        st.markdown("#### Correlation Matrix")
        corr = df[numeric_cols].corr()
        fig = px.imshow(corr, text_auto='.2f', color_continuous_scale='RdBu_r')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📊 Pattern Recognition")
    
    if 'is_anomaly' in df.columns:
        anomaly_df = df[df['is_anomaly'] == -1]
        normal_df = df[df['is_anomaly'] == 1]
        
        if numeric_cols:
            feature = st.selectbox("Select Feature", numeric_cols, key="pattern_feat")
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=normal_df[feature], name='Normal', opacity=0.7, marker_color='#00cc96'))
            fig.add_trace(go.Histogram(x=anomaly_df[feature], name='Anomaly', opacity=0.7, marker_color='#ff4b4b'))
            fig.update_layout(barmode='overlay', title=f"Distribution: {feature}", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Normal Statistics**")
                st.dataframe(normal_df[numeric_cols].describe().round(2), use_container_width=True)
            with col2:
                st.markdown("**Anomaly Statistics**")
                if len(anomaly_df) > 0:
                    st.dataframe(anomaly_df[numeric_cols].describe().round(2), use_container_width=True)
                else:
                    st.info("No anomalies detected")
    else:
        st.info("Run anomaly detection first")

with tab3:
    st.subheader("🎯 Feature Importance")
    
    if 'is_anomaly' in df.columns and numeric_cols:
        from sklearn.ensemble import RandomForestClassifier
        
        X = df[numeric_cols].fillna(df[numeric_cols].median())
        y = df['is_anomaly']
        
        with st.spinner("Calculating..."):
            rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
            rf.fit(X, y)
            
            importance_df = pd.DataFrame({
                'Feature': numeric_cols,
                'Importance': rf.feature_importances_
            }).sort_values('Importance', ascending=True)
            
            fig = px.bar(
                importance_df, x='Importance', y='Feature',
                orientation='h', color='Importance',
                color_continuous_scale='Viridis',
                title="Feature Importance"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            top_features = importance_df.tail(3)['Feature'].tolist()
            st.success(f"**Top Features:** {', '.join(top_features)}")
    else:
        st.info("Run anomaly detection first")
