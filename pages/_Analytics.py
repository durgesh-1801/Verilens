import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Authentication check
if not st.session_state.get('authenticated'):
    st.error("🔒 Access Denied - Please login first")
    
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/_Login.py")
    
    st.stop()
# ========== END AUTHENTICATION CHECK ==========


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
        
        fig.add_trace(go.Histogram(x=df[selected_col]), row=1, col=1)
        fig.add_trace(go.Box(y=df[selected_col]), row=1, col=2)
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
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
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📊 Pattern Recognition")
    
    if 'is_anomaly' in df.columns:
        anomaly_df = df[df['is_anomaly'] == -1]
        normal_df = df[df['is_anomaly'] == 1]
        
        selected_feature = st.selectbox(
            "Select Feature for Pattern Analysis", 
            numeric_cols, 
            key="pattern_feature"
        )
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(x=normal_df[selected_feature], name='Normal', opacity=0.7))
        fig.add_trace(go.Histogram(x=anomaly_df[selected_feature], name='Anomaly', opacity=0.7))
        
        fig.update_layout(barmode='overlay')
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(normal_df[numeric_cols].describe(), use_container_width=True)
        with col2:
            st.dataframe(anomaly_df[numeric_cols].describe(), use_container_width=True)
    else:
        st.info("Run anomaly detection first to see pattern analysis")

with tab3:
    st.subheader("🎯 Feature Importance Analysis")
    
    if 'is_anomaly' in df.columns and len(numeric_cols) > 0:
        from sklearn.ensemble import RandomForestClassifier
        
        X = df[numeric_cols].fillna(df[numeric_cols].median())
        y = df['is_anomaly']
        
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
            color='Importance',
            color_continuous_scale='Turbo',
            title="Feature Importance (Higher = More Risk Influence)"
        )

        fig.update_layout(
            coloraxis_showscale=True,
            height=450
)

        st.plotly_chart(fig, use_container_width=True)
        
        top_features = importance_df.tail(3)['Feature'].tolist()
        st.success(f"Top predictive features: {', '.join(top_features)}")
    else:
        st.info("Run anomaly detection first to see feature importance")

with tab4:
    st.subheader("📉 Time Series Analysis")
    
    date_cols = []
    for col in df.columns:
        try:
            pd.to_datetime(df[col])
            date_cols.append(col)
        except:
            pass
    
    if date_cols:
        date_col = st.selectbox("Select Date Column", date_cols)
        value_col = st.selectbox("Select Value Column", numeric_cols, key="ts_value")
        
        if value_col is None:
            st.stop()
        
        temp_df = df.copy()
        temp_df[date_col] = pd.to_datetime(temp_df[date_col], errors='coerce')
        temp_df = temp_df.sort_values(date_col)
        
        # Ensure numeric values
        temp_df[value_col] = pd.to_numeric(temp_df[value_col], errors='coerce')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=temp_df[date_col],
            y=temp_df[value_col],
            mode='lines',
            name=value_col
        ))
        
        if 'is_anomaly' in temp_df.columns:
            anomaly_mask = temp_df['is_anomaly'] == -1
            fig.add_trace(go.Scatter(
                x=temp_df[anomaly_mask][date_col],
                y=temp_df[anomaly_mask][value_col],
                mode='markers',
                name='Anomalies'
            ))
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### Rolling Statistics")
        window = st.slider("Rolling Window Size", 7, 90, 30)
        
        temp_df['rolling_mean'] = (
            temp_df[value_col]
            .fillna(0)
            .rolling(window=window)
            .mean()
        )
        
        temp_df['rolling_std'] = (
            temp_df[value_col]
            .fillna(0)
            .rolling(window=window)
            .std()
        )
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=temp_df[date_col],
            y=temp_df[value_col],
            name='Actual',
            opacity=0.5
        ))
        
        fig.add_trace(go.Scatter(
            x=temp_df[date_col],
            y=temp_df['rolling_mean'],
            name='Rolling Mean'
        ))
        
        fig.add_trace(go.Scatter(
            x=temp_df[date_col],
            y=temp_df['rolling_mean'] + 2 * temp_df['rolling_std'],
            name='Upper Band',
            line=dict(dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=temp_df[date_col],
            y=temp_df['rolling_mean'] - 2 * temp_df['rolling_std'],
            name='Lower Band',
            line=dict(dash='dash')
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No date columns detected. Add a date column for time series analysis.")
