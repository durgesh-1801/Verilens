"""
Organization Admin Page
Manage users, roles, and permissions within your organization
"""

import streamlit as st
import database
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Organization Admin", page_icon="👥", layout="wide")

# ========== AUTHENTICATION & ADMIN CHECK ==========
if not st.session_state.get('authenticated'):
    st.error("🔒 Access Denied - Please login first")
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/_Login.py")
    st.stop()

# Get user info
user_id = st.session_state['user']['id']
user_role = st.session_state['user'].get('role', 'viewer')
organization_id = st.session_state['user'].get('organization_id')

# Only admins can access this page
if user_role != 'admin':
    st.error("🚫 Access Denied - Admin role required")
    st.info("This page is only accessible to organization administrators.")
    st.stop()

if not organization_id:
    st.error("❌ No organization associated with your account")
    st.stop()
# ========== END CHECKS ==========

# ==========================================
# HEADER
# ==========================================
st.title("👥 Organization Administration")

# Get organization details
org = database.get_organization_by_id(organization_id)
if org:
    st.info(f"🏢 Managing: **{org['name']}**")

st.markdown("---")

# ==========================================
# ORGANIZATION USERS
# ==========================================
st.header("Organization Members")

# Get all users in organization
users = database.get_organization_users(organization_id)

if not users:
    st.warning("No users found in your organization")
else:
    st.success(f"Total Members: {len(users)}")
    
    # Display users in a table with actions
    for user in users:
        with st.expander(f"👤 {user['username']} - {user['role'].upper()}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Email:** {user['email']}")
                st.markdown(f"**Role:** {user['role'].upper()}")
                st.markdown(f"**Status:** {'✅ Active' if user['is_active'] else '❌ Inactive'}")
                st.markdown(f"**Joined:** {user['created_at'][:10]}")
                if user['last_login']:
                    st.markdown(f"**Last Login:** {user['last_login'][:10]}")
            
            with col2:
                # Prevent admin from modifying themselves
                if user['id'] == user_id:
                    st.info("👑 This is you (admin)")
                else:
                    st.markdown("### Actions")
                    
                    # Role Management
                    st.markdown("**Change Role:**")
                    new_role = st.selectbox(
                        "Select new role",
                        ["viewer", "auditor", "admin"],
                        index=["viewer", "auditor", "admin"].index(user['role']),
                        key=f"role_{user['id']}",
                        label_visibility="collapsed"
                    )
                    
                    if st.button("Update Role", key=f"update_{user['id']}", use_container_width=True):
                        success, message = database.update_user_role(user['id'], new_role)
                        if success:
                            st.success(f"✓ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    
                    # User Activation/Deactivation
                    st.markdown("---")
                    if user['is_active']:
                        if st.button("🚫 Deactivate User", key=f"deactivate_{user['id']}", use_container_width=True):
                            success, message = database.deactivate_user(user['id'])
                            if success:
                                st.success(f"✓ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                    else:
                        if st.button("✅ Activate User", key=f"activate_{user['id']}", use_container_width=True, type="primary"):
                            success, message = database.activate_user(user['id'])
                            if success:
                                st.success(f"✓ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")

st.markdown("---")

# ==========================================
# ORGANIZATION STATISTICS
# ==========================================
st.header("Organization Statistics")

col1, col2, col3, col4 = st.columns(4)

active_users = sum(1 for u in users if u['is_active'])
admins = sum(1 for u in users if u['role'] == 'admin' and u['is_active'])
auditors = sum(1 for u in users if u['role'] == 'auditor' and u['is_active'])
viewers = sum(1 for u in users if u['role'] == 'viewer' and u['is_active'])

with col1:
    st.metric("Total Users", len(users), delta=f"{active_users} active")

with col2:
    st.metric("Admins", admins, delta="🔴")

with col3:
    st.metric("Auditors", auditors, delta="🟡")

with col4:
    st.metric("Viewers", viewers, delta="🟢")

# Role distribution chart
st.markdown("### Role Distribution")

role_data = pd.DataFrame({
    'Role': ['Admin', 'Auditor', 'Viewer'],
    'Count': [admins, auditors, viewers]
})

st.bar_chart(role_data.set_index('Role'))

st.markdown("---")

# ==========================================
# ORGANIZATION INFO
# ==========================================
st.header("Organization Information")

if org:
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown(f"**Organization ID:** {org['id']}")
        st.markdown(f"**Name:** {org['name']}")
    
    with info_col2:
        st.markdown(f"**Created:** {org['created_at'][:10]}")
        st.markdown(f"**Status:** {'✅ Active' if org['is_active'] else '❌ Inactive'}")

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.caption("🛡️ AI Fraud Detection System · Organization Administration")
