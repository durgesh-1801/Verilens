"""
Authentication Module
Secure user authentication with PBKDF2 password hashing
Multi-tenant organization support with RBAC
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime
from typing import Optional, Dict, Tuple
from pathlib import Path

# Database path (same as your existing database.py)
DB_PATH = Path("fraud_detection.db")


# ==========================================
# PASSWORD HASHING (SECURE)
# ==========================================
def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Hash password using SHA-256 with salt (production-ready alternative to bcrypt)
    
    Args:
        password: Plain text password
        salt: Optional salt (generated if not provided)
    
    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        salt = secrets.token_hex(32)  # 64-character hex salt
    
    # Use PBKDF2 with SHA-256 (100,000 iterations for security)
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # iterations
    )
    
    return hashed.hex(), salt


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """
    Verify password against stored hash
    
    Args:
        password: Plain text password to verify
        hashed_password: Stored password hash
        salt: Stored salt
    
    Returns:
        True if password matches, False otherwise
    """
    new_hash, _ = hash_password(password, salt)
    return new_hash == hashed_password


# ==========================================
# USER MANAGEMENT
# ==========================================
def create_user(username: str, email: str, password: str, role: str = 'viewer', organization_id: int = None) -> Tuple[bool, str]:
    """
    Create a new user account with role and organization
    
    Args:
        username: Unique username
        email: User email
        password: Plain text password (will be hashed)
        role: User role ('admin', 'auditor', 'viewer') - default 'viewer'
        organization_id: Organization ID to join
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Validation
    if not username or not email or not password:
        return False, "All fields are required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if '@' not in email:
        return False, "Invalid email format"
    
    if role not in ['admin', 'auditor', 'viewer']:
        role = 'viewer'  # Default to viewer if invalid role
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already exists"
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return False, "Email already registered"
        
        # Hash password
        password_hash, salt = hash_password(password)
        
        # Insert user with organization
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, salt, role, organization_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, email, password_hash, salt, role, organization_id, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return True, "Account created successfully"
    
    except Exception as e:
        return False, f"Error creating account: {str(e)}"


def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[Dict], str]:
    """
    Authenticate user with username and password (returns role and organization)
    
    Args:
        username: Username
        password: Plain text password
    
    Returns:
        Tuple of (success: bool, user_dict: dict or None, message: str)
    """
    if not username or not password:
        return False, None, "Username and password required"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user with role and organization
        cursor.execute("""
            SELECT id, username, email, password_hash, salt, role, organization_id, created_at, is_active
            FROM users
            WHERE username = ?
        """, (username,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False, None, "Invalid username or password"
        
        user_id, username, email, stored_hash, salt, role, organization_id, created_at, is_active = result
        
        # Check if user is active
        if not is_active:
            return False, None, "Account is deactivated. Contact your administrator."
        
        # Verify password
        if verify_password(password, stored_hash, salt):
            user_dict = {
                'id': user_id,
                'username': username,
                'email': email,
                'role': role,
                'organization_id': organization_id,
                'created_at': created_at
            }
            return True, user_dict, "Login successful"
        else:
            return False, None, "Invalid username or password"
    
    except Exception as e:
        return False, None, f"Authentication error: {str(e)}"


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """
    Get user information by ID (includes role and organization)
    
    Args:
        user_id: User ID
    
    Returns:
        User dictionary or None
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, role, organization_id, created_at
            FROM users
            WHERE id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'email': result[2],
                'role': result[3],
                'organization_id': result[4],
                'created_at': result[5]
            }
        return None
    
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None


def update_password(user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
    """
    Update user password
    
    Args:
        user_id: User ID
        old_password: Current password
        new_password: New password
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get current password hash
        cursor.execute("""
            SELECT password_hash, salt
            FROM users
            WHERE id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False, "User not found"
        
        stored_hash, salt = result
        
        # Verify old password
        if not verify_password(old_password, stored_hash, salt):
            conn.close()
            return False, "Current password is incorrect"
        
        # Hash new password
        new_hash, new_salt = hash_password(new_password)
        
        # Update password
        cursor.execute("""
            UPDATE users
            SET password_hash = ?, salt = ?
            WHERE id = ?
        """, (new_hash, new_salt, user_id))
        
        conn.commit()
        conn.close()
        
        return True, "Password updated successfully"
    
    except Exception as e:
        return False, f"Error updating password: {str(e)}"


def logout() -> None:
    """
    Logout current user (to be called from Streamlit)
    This is a placeholder - actual logout happens in Streamlit session state
    """
    pass  # Logout logic handled in Streamlit app


# ==========================================
# INITIALIZATION
# ==========================================
def init_users_table():
    """
    Initialize users table in database
    Called during database initialization
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT DEFAULT 'viewer' NOT NULL,
                organization_id INTEGER,
                created_at TEXT NOT NULL,
                last_login TEXT,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (organization_id) REFERENCES organizations(id)
            )
        """)
        
        conn.commit()
        conn.close()
        print("✓ Users table initialized")
    
    except Exception as e:
        print(f"Error initializing users table: {e}")


# ==========================================
# UTILITY FUNCTIONS
# ==========================================
def get_all_users() -> list:
    """Get all users (admin function)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, role, organization_id, created_at, is_active
            FROM users
            ORDER BY created_at DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'role': row[3],
                'organization_id': row[4],
                'created_at': row[5],
                'is_active': row[6]
            })
        
        conn.close()
        return users
    
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []


def update_last_login(user_id: int):
    """Update user's last login timestamp"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users
            SET last_login = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), user_id))
        
        conn.commit()
        conn.close()
    
    except Exception as e:
        print(f"Error updating last login: {e}")
