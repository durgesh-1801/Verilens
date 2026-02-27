"""
Signup Page
User registration with organization selection
"""

import streamlit as st
import auth
import database

st.set_page_config(page_title="Sign Up", page_icon="📝", layout="centered")

# Check if already logged in
if st.session_state.get('user'):
    st.info(f"✓ You're already logged in as {st.session_state['user']['username']}")
    
    if st.button("Go to Home"):
        st.switch_page("app.py")
    
    st.stop()

# ==========================================
# SIGNUP UI
# ==========================================
st.title("📝 Create Account")
st.markdown("Join the AI Fraud Detection platform")

st.markdown("---")

# Signup Form
with st.form("signup_form"):
    st.markdown("### Account Information")
    
    username = st.text_input(
        "Username *",
        placeholder="Choose a unique username (min 3 characters)",
        help="This will be your login ID"
    )
    
    email = st.text_input(
        "Email *",
        placeholder="your.email@company.com",
        help="We'll never share your email"
    )
    
    password = st.text_input(
        "Password *",
        type="password",
        placeholder="Create a strong password (min 6 characters)",
        help="Use a combination of letters, numbers, and symbols"
    )
    
    password_confirm = st.text_input(
        "Confirm Password *",
        type="password",
        placeholder="Re-enter your password"
    )
    
    # ========== NEW: ORGANIZATION SELECTION ==========
    st.markdown("---")
    st.markdown("### Organization")
    
    org_option = st.radio(
        "Choose an option:",
        ["Create New Organization", "Join Existing Organization"],
        help="Create a new organization or join an existing one"
    )
    
    org_id = None
    org_name = None
    
    if org_option == "Create New Organization":
        org_name = st.text_input(
            "Organization Name *",
            placeholder="Enter your organization name",
            help="This will be your organization's identifier"
        )
    else:
        # Load existing organizations
        existing_orgs = database.get_all_organizations()
        
        if existing_orgs:
            org_names = [org['name'] for org in existing_orgs]
            selected_org_name = st.selectbox(
                "Select Organization *",
                org_names,
                help="Choose the organization you want to join"
            )
            
            # Get org_id from selected name
            org_id = next((org['id'] for org in existing_orgs if org['name'] == selected_org_name), None)
        else:
            st.warning("No organizations available. Please create a new one.")
            org_option = "Create New Organization"
            org_name = st.text_input(
                "Organization Name *",
                placeholder="Enter your organization name",
                key="fallback_org_name"
            )
    # ========== END ORGANIZATION SELECTION ==========
    
    st.markdown("---")
    
    agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        submit = st.form_submit_button("✅ Create Account", use_container_width=True, type="primary")
    
    with col2:
        if st.form_submit_button("🔐 Back to Login", use_container_width=True):
            st.switch_page("pages/_Login.py")

# Handle Signup
if submit:
    # Validation
    if not username or not email or not password or not password_confirm:
        st.error("❌ All fields are required")
    elif not agree:
        st.error("❌ You must agree to the Terms of Service")
    elif password != password_confirm:
        st.error("❌ Passwords do not match")
    elif org_option == "Create New Organization" and not org_name:
        st.error("❌ Organization name is required")
    else:
        with st.spinner("Creating your account..."):
            # ========== NEW: CREATE ORGANIZATION IF NEEDED ==========
            if org_option == "Create New Organization":
                success, result = database.create_organization(org_name)
                if success:
                    org_id = result
                    st.info(f"✓ Organization '{org_name}' created successfully")
                else:
                    st.error(f"❌ {result}")
                    st.stop()
            # ========== END ORGANIZATION CREATION ==========
            
            # ========== MODIFIED: CREATE USER WITH ORGANIZATION ==========
            success, message = auth.create_user(username, email, password, role='viewer', organization_id=org_id)
            # ========== END MODIFIED USER CREATION ==========
            
            if success:
                st.success(f"✓ {message}")
                st.success("You can now login with your credentials!")
                st.balloons()
                
                # Auto-login
                auto_login = st.checkbox("Login automatically", value=True)
                
                if auto_login:
                    success, user_dict, _ = auth.authenticate_user(username, password)
                    if success:
                        st.session_state['user'] = user_dict
                        st.session_state['authenticated'] = True
                        st.info("Redirecting to dashboard...")
                        st.rerun()
                else:
                    if st.button("Go to Login"):
                        st.switch_page("pages/_Login.py")
            else:
                st.error(f"❌ {message}")

st.markdown("---")

# Info Section
with st.expander("ℹ️ Password Requirements"):
    st.markdown("""
    **Strong Password Guidelines:**
    - Minimum 6 characters (longer is better)
    - Mix of uppercase and lowercase letters
    - Include numbers
    - Consider using symbols
    
    **Account Security:**
    - Your password is encrypted using PBKDF2-SHA256
    - We never store passwords in plain text
    - You can change your password anytime after login
    
    **Organization Notes:**
    - Creating a new organization makes you the first member
    - Joining an existing organization connects you with your team
    - Your organization admin can manage your permissions
    """)

# Footer
st.markdown("---")
st.caption("🛡️ AI Fraud Detection System · Secure Registration")
