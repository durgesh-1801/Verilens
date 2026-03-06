"""
Login Page - Enhanced UX
Improved authentication interface with better error handling and password visibility toggle
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import auth

# Page config
st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

# Custom CSS for better styling
st.markdown("""
<style>
.login-container {
    max-width: 450px;
    margin: 0 auto;
    padding: 2rem;
}
.login-header {
    text-align: center;
    margin-bottom: 2rem;
}
.login-title {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.login-subtitle {
    color: #6c757d;
    font-size: 1rem;
}
.input-label {
    font-weight: 600;
    color: #495057;
    margin-bottom: 0.5rem;
}
.helper-text {
    font-size: 0.875rem;
    color: #6c757d;
    margin-top: 0.25rem;
}
.divider {
    margin: 2rem 0;
    border-top: 1px solid #dee2e6;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="login-container">', unsafe_allow_html=True)
st.markdown('''
<div class="login-header">
    <div class="login-title">🔐 Login</div>
    <div class="login-subtitle">Access AI Fraud Detection System</div>
</div>
''', unsafe_allow_html=True)

# Initialize session state for password visibility
if 'show_password' not in st.session_state:
    st.session_state.show_password = False

# Login form
with st.form("login_form", clear_on_submit=False):
    st.markdown('<p class="input-label">Username</p>', unsafe_allow_html=True)
    username = st.text_input(
        "Username",
        placeholder="Enter your username",
        label_visibility="collapsed",
        key="login_username"
    )
    
    st.markdown('<p class="input-label">Password</p>', unsafe_allow_html=True)
    
    # Password input with visibility toggle
    password_col1, password_col2 = st.columns([6, 1])
    
    with password_col1:
        if st.session_state.show_password:
            password = st.text_input(
                "Password",
                placeholder="Enter your password",
                label_visibility="collapsed",
                key="login_password_visible"
            )
        else:
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                label_visibility="collapsed",
                key="login_password_hidden"
            )
    
    with password_col2:
        # Toggle button for password visibility
        if st.form_submit_button("👁️", use_container_width=True):
            st.session_state.show_password = not st.session_state.show_password
            st.rerun()
    
    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
    
    # Submit button
    submit = st.form_submit_button(
        "🔓 Login",
        type="primary",
        use_container_width=True
    )
    
    if submit:
        # Validation
        if not username or not password:
            st.error("⚠️ Please enter both username and password")
        else:
            # Attempt authentication
            with st.spinner("Authenticating..."):
                user = auth.authenticate_user(username, password)
                
                if user:
                    # Check if user is active
                    if not user.get('is_active', True):
                        st.error("🚫 Your account has been deactivated. Please contact your administrator.")
                    else:
                        # Successful login
                        st.session_state['user'] = user
                        st.session_state['authenticated'] = True
                        
                        st.success(f"✅ Welcome back, {user['username']}!")
                        st.toast("Login successful 🎉")
                        
                        # Display user info
                        role = user.get('role', 'viewer')
                        st.info(f"**Role:** {role.upper()}")
                        
                        # Redirect to home
                        st.markdown("Redirecting to dashboard...")
                        st.switch_page("app.py")
                else:
                    # Authentication failed
                    st.error("❌ Invalid username or password. Please try again.")
                    st.warning("💡 **Tip:** Make sure your username and password are correct and case-sensitive.")

# Divider
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Signup link
st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
st.markdown("Don't have an account?")

if st.button("📝 Create New Account", use_container_width=True):
    st.switch_page("pages/_Signup.py")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('''
<div style="text-align: center; color: #6c757d; font-size: 0.875rem;">
    🛡️ Secure Authentication System<br>
    AI Fraud Detection Platform
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
