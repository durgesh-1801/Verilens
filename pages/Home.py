"""
Verilens - Landing Page
AI-Powered Continuous Audit Platform
"""

import streamlit as st

# Page config
st.set_page_config(
    page_title="Verilens - AI Audit Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for landing page
st.markdown("""
<style>
/* Hide sidebar on landing page */
[data-testid="stSidebar"] {
    display: none;
}

/* Landing page styles */
.landing-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 3rem 2rem;
    text-align: center;
}

.hero-title {
    font-size: 4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
    letter-spacing: -2px;
}

.hero-subtitle {
    font-size: 1.3rem;
    color: #6c757d;
    line-height: 1.8;
    margin-bottom: 3rem;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
}

.button-container {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    margin: 3rem 0;
}

.features-section {
    margin-top: 5rem;
    padding: 3rem 2rem;
    background: rgba(30, 41, 59, 0.6);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.08);
}

.features-title {
    font-size: 2rem;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 2rem;
}

.feature-list {
    text-align: left;
    max-width: 600px;
    margin: 0 auto;
}

.feature-item {
    font-size: 1.1rem;
    color: #4a5568;
    margin: 1.2rem 0;
    padding-left: 1.5rem;
    position: relative;
}

.feature-item:before {
    content: "•";
    position: absolute;
    left: 0;
    color: #667eea;
    font-size: 1.5rem;
    font-weight: bold;
}

.badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    background: #667eea;
    color: white;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 2rem;
}

.footer {
    margin-top: 5rem;
    padding-top: 2rem;
    border-top: 1px solid #e2e8f0;
    color: #a0aec0;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# Main landing page content
st.markdown('<div class="landing-container">', unsafe_allow_html=True)

# Badge
st.markdown('<div class="badge">🛡️ AI-Powered Audit Intelligence</div>', unsafe_allow_html=True)

# Hero section
st.markdown('<h1 class="hero-title">Verilens</h1>', unsafe_allow_html=True)

st.markdown('''
<p class="hero-subtitle">
AI-powered continuous audit platform that detects suspicious financial transactions 
using anomaly detection and intelligent audit rules.
</p>
''', unsafe_allow_html=True)

# Action buttons
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    button_col1, button_col2 = st.columns(2)
    
    with button_col1:
        if st.button("🔐 Login", use_container_width=True, type="primary", key="landing_login"):
            st.switch_page("pages/_Login.py")
    
    with button_col2:
        if st.button("📝 Sign Up", use_container_width=True, key="landing_signup"):
            st.switch_page("pages/_Signup.py")

# Features section
st.markdown('''
<div class="features-section">
    <h2 class="features-title">What Verilens Does</h2>
    <div class="feature-list">
        <div class="feature-item">
            Detect anomalous financial transactions using AI
        </div>
        <div class="feature-item">
            Apply intelligent audit rule analysis
        </div>
        <div class="feature-item">
            Generate fraud alerts for auditors
        </div>
        <div class="feature-item">
            Provide investigation tools and reporting
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

# Feature highlights (visual cards)
st.markdown('<div style="margin-top: 4rem;"></div>', unsafe_allow_html=True)

feat_col1, feat_col2, feat_col3 = st.columns(3)

with feat_col1:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size:3rem;margin-bottom:1rem;">🤖</div>
        <h3>AI Detection</h3>
        <p>Machine learning models identify unusual transaction patterns</p>
    </div>
    """, unsafe_allow_html=True)

with feat_col2:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size:3rem;margin-bottom:1rem;">🔍</div>
        <h3>Smart Audits</h3>
        <p>Rule-based engine applies audit intelligence automatically</p>
    </div>
    """, unsafe_allow_html=True)

with feat_col3:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size:3rem;margin-bottom:1rem;">📊</div>
        <h3>Real-time Insights</h3>
        <p>Live dashboards and executive analytics</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown('''
<div class="footer">
    <p>Built by Quantum Crew</p>
    <p>Secure • Intelligent • Continuous</p>
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Check if user is already logged in (redirect to app)
if st.session_state.get('authenticated'):
    st.info("✅ You are already logged in. Redirecting to dashboard...")
    if st.button("Go to Dashboard"):
        st.switch_page("app.py")
