"""
Signup Page - Enhanced UX
Improved registration interface with role selection and better validation
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import auth
import database

# Page config
st.set_page_config(page_title="Sign Up", page_icon="📝", layout="centered")

# Custom CSS for better styling
st.markdown("""
<style>
.signup-container {
    max-width: 500px;
    margin: 0 auto;
    padding: 2rem;
}
.signup-header {
    text-align: center;
    margin-bottom: 2rem;
}
.signup-title {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.signup-subtitle {
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
.info-box {
    background-color: rgba(30,41,59,0.6)
    border-left: 4px solid #667eea;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 10px;
    color: #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="signup-container">', unsafe_allow_html=True)
st.markdown('''
<div class="signup-header">
    <div class="signup-title">📝 Sign Up</div>
    <div class="signup-subtitle">Create your account to get started</div>
</div>
''', unsafe_allow_html=True)

# Initialize session state for password visibility
if 'show_signup_password' not in st.session_state:
    st.session_state.show_signup_password = False

if 'show_confirm_password' not in st.session_state:
    st.session_state.show_confirm_password = False

# Signup form
with st.form("signup_form", clear_on_submit=False):
    # Username
    st.markdown('<p class="input-label">Username</p>', unsafe_allow_html=True)
    username = st.text_input(
        "Username",
        placeholder="Choose a unique username",
        label_visibility="collapsed",
        key="signup_username"
    )
    st.markdown('<p class="helper-text">This will be your login identifier</p>', unsafe_allow_html=True)
    
    # Email
    st.markdown('<p class="input-label">Email Address</p>', unsafe_allow_html=True)
    email = st.text_input(
        "Email",
        placeholder="your.email@example.com",
        label_visibility="collapsed",
        key="signup_email"
    )
    st.markdown('<p class="helper-text">We\'ll use this for account recovery</p>', unsafe_allow_html=True)
    
    # Password
    st.markdown('<p class="input-label">Password</p>', unsafe_allow_html=True)
    password_col1, password_col2 = st.columns([6, 1])
    
    with password_col1:
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a strong password (min 8 characters)",
            label_visibility="collapsed",
            key="signup_password"
        )
    
    
    
    st.markdown('<p class="helper-text">⚠️ Minimum 8 characters required</p>', unsafe_allow_html=True)
    
    # Confirm Password
    st.markdown('<p class="input-label">Confirm Password</p>', unsafe_allow_html=True)
    confirm_col1, confirm_col2 = st.columns([6, 1])
    
    with confirm_col1:
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            label_visibility="collapsed",
            key="signup_confirm_password"
        )
    
    
    
    # Role Selection (NEW)
    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
    st.markdown('<p class="input-label">Select Your Role</p>', unsafe_allow_html=True)
    
    role = st.selectbox(
        "Role",
        options=["viewer", "auditor"],
        index=0,
        format_func=lambda x: f"👤 Viewer - Read-only access" if x == "viewer" else "🔍 Auditor - Can manage alerts and cases",
        label_visibility="collapsed",
        key="signup_role"
    )
    
    # Role information
    if role == "viewer":
        st.markdown('''
        <div class="info-box">
            <strong>👤 Viewer Role</strong><br>
            • View dashboards and analytics<br>
            • Access reports<br>
            • Limited permissions
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="info-box">
            <strong>🔍 Auditor Role</strong><br>
            • All viewer permissions<br>
            • Manage alerts and cases<br>
            • Conduct investigations<br>
            • Update audit status
        </div>
        ''', unsafe_allow_html=True)
    
    # Organization section
    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
    st.markdown('<p class="input-label">Organization</p>', unsafe_allow_html=True)
    
    org_choice = st.radio(
        "Organization Choice",
        options=["Create New Organization", "Join Existing Organization"],
        label_visibility="collapsed",
        horizontal=True,
        key="org_choice"
    )
    
    organization_id = None
    
    if org_choice == "Create New Organization":
        org_name = st.text_input(
            "Organization Name",
            placeholder="Enter your organization name",
            key="new_org_name"
        )
        st.markdown('<p class="helper-text">You will be the first member of this organization</p>', unsafe_allow_html=True)
    else:
        # Get existing organizations
        existing_orgs = database.get_all_organizations()
        
        if existing_orgs:
            org_options = {org['name']: org['id'] for org in existing_orgs}
            selected_org = st.selectbox(
                "Select Organization",
                options=list(org_options.keys()),
                key="existing_org"
            )
            organization_id = org_options[selected_org]
            st.markdown(f'<p class="helper-text">Join {selected_org}</p>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ No organizations available. Please create a new organization.")
            org_name = st.text_input(
                "Organization Name",
                placeholder="Enter your organization name",
                key="fallback_org_name"
            )
    
    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
    
    # Submit button
    submit = st.form_submit_button(
        "🚀 Create Account",
        type="primary",
        use_container_width=True
    )
    
    if submit:
        # Comprehensive validation
        errors = []
        
        # Check required fields
        if not username:
            errors.append("Username is required")
        
        if not email:
            errors.append("Email is required")
        
        if not password:
            errors.append("Password is required")
        
        if not confirm_password:
            errors.append("Please confirm your password")
        
        # Validate email format
        if email and '@' not in email:
            errors.append("Please enter a valid email address")
        
        # Validate password length
        if password and len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        # Check password match
        if password and confirm_password and password != confirm_password:
            errors.append("Passwords do not match")
        
        # Organization validation
        if org_choice == "Create New Organization":
            if 'org_name' not in locals() or not org_name:
                errors.append("Organization name is required")
        
        # Display errors
        if errors:
            st.error("⚠️ Please fix the following errors:")
            for error in errors:
                st.error(f"  • {error}")
        else:
            # Proceed with signup
            with st.spinner("Creating your account..."):
                # Handle organization
                if org_choice == "Create New Organization":
                    success, result = database.create_organization(org_name)
                    
                    if success:
                        organization_id = result
                        st.success(f"✅ Organization '{org_name}' created successfully!")
                    else:
                        st.error(f"❌ Error creating organization: {result}")
                        st.stop()
                
                # Create user with role
                success, message = auth.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role,
                    organization_id=organization_id
                )
                
                if success:
                    st.success("✅ Account created successfully!")
                    
                    
                    # Show success message with role
                    st.info(f"**Username:** {username}\n\n**Role:** {role.upper()}\n\n**Email:** {email}")
                    
                    # Auto-login
                    user = auth.authenticate_user(username, password)
                    
                    if user:
                        st.session_state['user'] = user
                        st.session_state['authenticated'] = True
                        
                        st.success("🎉 Logging you in automatically...")
                        
                        # Redirect to home
                        st.switch_page("app.py")
                    else:
                        st.warning("Account created but auto-login failed. Please login manually.")
                        
                        if st.button("Go to Login"):
                            st.switch_page("pages/_Login.py")
                else:
                    # Handle errors
                    if "duplicate" in message.lower() or "already exists" in message.lower():
                        if "email" in message.lower():
                            st.error("❌ This email address is already registered. Please use a different email or try logging in.")
                        else:
                            st.error("❌ This username is already taken. Please choose a different username.")
                    else:
                        st.error(f"❌ Signup failed: {message}")

# Divider
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Login link
st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
st.markdown("Already have an account?")

if st.button("🔐 Login", use_container_width=True):
    st.switch_page("pages/_Login.py")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('''
<div style="text-align: center; color: #6c757d; font-size: 0.875rem;">
    🛡️ Secure Registration System<br>
    AI Fraud Detection Platform
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
