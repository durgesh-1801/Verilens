"""
Authentication Module
Handles user registration, login, and password management
Enhanced with email validation and password strength requirements
"""

import hashlib
import os
import sqlite3
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path("fraud_detection.db")


def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)


def hash_password(password: str, salt: bytes = None) -> tuple:
    """
    Hash password using PBKDF2-SHA256
    
    Args:
        password: Plain text password
        salt: Optional salt (generated if not provided)
        
    Returns:
        Tuple of (password_hash, salt)
    """
    if salt is None:
        salt = os.urandom(32)
    
    # Use PBKDF2-SHA256 with 100,000 iterations
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    
    return password_hash.hex(), salt.hex()


def init_users_table():
    """Initialize users table with role and organization_id columns"""
    conn = get_connection()
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
    
    # Create indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
    """)
    
    conn.commit()
    conn.close()


def create_user(username: str, email: str, password: str, role: str = 'viewer', organization_id: int = None) -> tuple:
    """
    Create a new user with enhanced validation
    
    Args:
        username: Unique username
        email: User email (must be unique)
        password: Plain text password (will be hashed)
        role: User role (viewer, auditor, admin) - default 'viewer'
        organization_id: Optional organization ID
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Validation
    if not username or not email or not password:
        return False, "Username, email, and password are required"
    
    # Validate password length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Validate email format (basic check)
    if '@' not in email:
        return False, "Invalid email format"
    
    # Validate role
    valid_roles = ['viewer', 'auditor', 'admin']
    if role not in valid_roles:
        return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}"
    
    try:
        conn = get_connection()
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
            return False, "Email address already registered"
        
        # Hash password
        password_hash, salt = hash_password(password)
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, salt, role, organization_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, email, password_hash, salt, role, organization_id, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return True, "User created successfully"
    
    except Exception as e:
        return False, f"Error creating user: {str(e)}"


def authenticate_user(username: str, password: str) -> dict:
    """
    Authenticate user and return user data
    
    Args:
        username: Username
        password: Plain text password
        
    Returns:
        User dict if authenticated, None otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, password_hash, salt, role, organization_id, is_active
            FROM users
            WHERE username = ?
        """, (username,))
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
        
        user_id, db_username, email, stored_hash, salt, role, organization_id, is_active = result
        
        # Check if user is active
        if not is_active:
            conn.close()
            return None
        
        # Verify password
        password_hash, _ = hash_password(password, bytes.fromhex(salt))
        
        if password_hash != stored_hash:
            conn.close()
            return None
        
        # Update last login
        cursor.execute("""
            UPDATE users SET last_login = ? WHERE id = ?
        """, (datetime.now().isoformat(), user_id))
        
        conn.commit()
        conn.close()
        
        return {
            'id': user_id,
            'username': db_username,
            'email': email,
            'role': role,
            'organization_id': organization_id,
            'is_active': is_active
        }
    
    except Exception as e:
        print(f"Authentication error: {e}")
        return None


def get_user_by_id(user_id: int) -> dict:
    """
    Get user by ID
    
    Args:
        user_id: User ID
        
    Returns:
        User dict or None
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, role, organization_id, created_at, last_login, is_active
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
                'created_at': result[5],
                'last_login': result[6],
                'is_active': result[7]
            }
        
        return None
    
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None


def get_all_users() -> list:
    """
    Get all users
    
    Returns:
        List of user dicts
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, role, organization_id, created_at, last_login, is_active
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
                'last_login': row[6],
                'is_active': row[7]
            })
        
        conn.close()
        return users
    
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []


def change_password(user_id: int, old_password: str, new_password: str) -> tuple:
    """
    Change user password
    
    Args:
        user_id: User ID
        old_password: Current password
        new_password: New password
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Validate new password length
    if len(new_password) < 8:
        return False, "New password must be at least 8 characters long"
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get current password hash and salt
        cursor.execute("""
            SELECT password_hash, salt FROM users WHERE id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, "User not found"
        
        stored_hash, salt = result
        
        # Verify old password
        old_hash, _ = hash_password(old_password, bytes.fromhex(salt))
        
        if old_hash != stored_hash:
            conn.close()
            return False, "Current password is incorrect"
        
        # Hash new password
        new_hash, new_salt = hash_password(new_password)
        
        # Update password
        cursor.execute("""
            UPDATE users SET password_hash = ?, salt = ? WHERE id = ?
        """, (new_hash, new_salt, user_id))
        
        conn.commit()
        conn.close()
        
        return True, "Password changed successfully"
    
    except Exception as e:
        return False, f"Error changing password: {str(e)}"
