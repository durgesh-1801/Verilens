"""
Login Page
Secure user authentication
"""

import streamlit as st
import auth

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

# Check if already logged in
if st.session_state.get('user'):
    st.success(f"✓ Already logged in as {st.session_state['user']['username']}")
    st.info("Navigate to other pages using the sidebar")
    
    if st.button("Go to Home"):
        st.switch_page("app.py")
    
    st.stop()

# ==========================================
# LOGIN UI
# ==========================================
st.title("🔐 Login")
st.markdown("Access your AI Fraud Detection dashboard")

st.markdown("---")

# Login Form
with st.form("login_form"):
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        submit = st.form_submit_button("🔓 Login", use_container_width=True, type="primary")
    
    with col2:
        if st.form_submit_button("📝 Create Account", use_container_width=True):
            st.switch_page("pages/_Signup.py")

# Handle Login
if submit:
    if not username or not password:
        st.error("❌ Please enter both username and password")
    else:
        with st.spinner("Authenticating..."):
            success, user_dict, message = auth.authenticate_user(username, password)
            
            if success:
                # Store user in session state
                st.session_state['user'] = user_dict
                st.session_state['authenticated'] = True
                
                # Update last login
                auth.update_last_login(user_dict['id'])
                
                st.success(f"✓ {message}")
                st.success(f"Welcome back, {user_dict['username']}!")
                
                
                # Redirect to home
                st.info("Redirecting to dashboard...")
                st.rerun()
            else:
                st.error(f"❌ {message}")

st.markdown("---")

# Info Section
with st.expander("ℹ️ Need Help?"):
    st.markdown("""
    **First time here?**
    - Click "Create Account" to sign up
    - Use a strong password (min 6 characters)
    
    **Forgot Password?**
    - Contact your system administrator
    
    **Security Notice:**
    - Your password is encrypted using industry-standard hashing
    - Never share your credentials
    """)

# Footer
st.markdown("---")
st.caption("🛡️ AI Fraud Detection System · Secure Authentication")
