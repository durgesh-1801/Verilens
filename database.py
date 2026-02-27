"""
Database Layer for AI Fraud Detection System
SQLite-based persistence for transactions and audit actions
"""

import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

# Database file location
DB_PATH = Path("fraud_detection.db")


# =====================================================
# CONNECTION
# =====================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


# =====================================================
# INITIALIZATION
# =====================================================

def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # ========== NEW: ORGANIZATIONS TABLE ==========
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_organizations_name 
        ON organizations(name)
    """)
    # ========== END ORGANIZATIONS TABLE ==========
    
    # ========== MODIFIED: TRANSACTIONS TABLE WITH USER_ID AND ORGANIZATION_ID ==========
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            organization_id INTEGER,
            department TEXT,
            amount REAL,
            vendor TEXT,
            purpose TEXT,
            transaction_date TEXT,
            risk_score REAL,
            severity TEXT,
            ai_reason TEXT,
            detection_timestamp TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (organization_id) REFERENCES organizations(id)
        )
    """)
    # ========== END MODIFIED TRANSACTIONS TABLE ==========
    
    # Existing audit_actions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER,
            status TEXT,
            auditor_notes TEXT,
            review_timestamp TEXT,
            action_type TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
        )
    """)
    
    # Existing audit_history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER,
            field_changed TEXT,
            old_value TEXT,
            new_value TEXT,
            changed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
        )
    """)
    
    # ========== MODIFIED: USERS TABLE WITH ROLE AND ORGANIZATION_ID ==========
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
    # ========== END MODIFIED USERS TABLE ==========
    
    # Create indexes for faster user lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_username 
        ON users(username)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_email 
        ON users(email)
    """)
    
    # ========== NEW: INDEXES FOR USER_ID AND ORGANIZATION_ID ==========
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_user_id 
        ON transactions(user_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_organization_id 
        ON transactions(organization_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_organization_id 
        ON users(organization_id)
    """)
    # ========== END NEW INDEXES ==========
    
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully")


# =====================================================
# ORGANIZATION MANAGEMENT (NEW)
# =====================================================

def create_organization(name):
    """
    Create a new organization
    
    Args:
        name: Organization name
    
    Returns:
        Tuple of (success: bool, org_id or error_message)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if organization already exists
        cursor.execute("SELECT id FROM organizations WHERE name = ?", (name,))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return False, "Organization name already exists"
        
        # Create organization
        cursor.execute("""
            INSERT INTO organizations (name, created_at)
            VALUES (?, ?)
        """, (name, datetime.now().isoformat()))
        
        org_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return True, org_id
    
    except Exception as e:
        return False, f"Error creating organization: {str(e)}"


def get_organization_by_id(org_id):
    """Get organization details by ID"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, created_at, is_active
            FROM organizations
            WHERE id = ?
        """, (org_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'created_at': result[2],
                'is_active': result[3]
            }
        return None
    
    except Exception as e:
        print(f"Error fetching organization: {e}")
        return None


def get_all_organizations():
    """Get all active organizations"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, created_at, is_active
            FROM organizations
            WHERE is_active = 1
            ORDER BY name
        """)
        
        orgs = []
        for row in cursor.fetchall():
            orgs.append({
                'id': row[0],
                'name': row[1],
                'created_at': row[2],
                'is_active': row[3]
            })
        
        conn.close()
        return orgs
    
    except Exception as e:
        print(f"Error fetching organizations: {e}")
        return []


def get_organization_users(org_id):
    """Get all users in an organization"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, role, created_at, last_login, is_active
            FROM users
            WHERE organization_id = ?
            ORDER BY created_at DESC
        """, (org_id,))
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'role': row[3],
                'created_at': row[4],
                'last_login': row[5],
                'is_active': row[6]
            })
        
        conn.close()
        return users
    
    except Exception as e:
        print(f"Error fetching organization users: {e}")
        return []


def update_user_role(user_id, new_role):
    """Update user's role (admin function)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users
            SET role = ?
            WHERE id = ?
        """, (new_role, user_id))
        
        conn.commit()
        conn.close()
        
        return True, "Role updated successfully"
    
    except Exception as e:
        return False, f"Error updating role: {str(e)}"


def deactivate_user(user_id):
    """Deactivate a user (admin function)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users
            SET is_active = 0
            WHERE id = ?
        """, (user_id,))
        
        conn.commit()
        conn.close()
        
        return True, "User deactivated successfully"
    
    except Exception as e:
        return False, f"Error deactivating user: {str(e)}"


def activate_user(user_id):
    """Reactivate a user (admin function)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users
            SET is_active = 1
            WHERE id = ?
        """, (user_id,))
        
        conn.commit()
        conn.close()
        
        return True, "User activated successfully"
    
    except Exception as e:
        return False, f"Error activating user: {str(e)}"


# =====================================================
# DATAFRAME INSERT - MODIFIED WITH USER_ID AND ORGANIZATION_ID
# =====================================================

def insert_dataframe(df: pd.DataFrame, user_id=None, organization_id=None):
    """
    Insert dataframe with optional user_id and organization_id
    
    Args:
        df: DataFrame to insert
        user_id: Optional user ID to associate with all transactions
        organization_id: Optional organization ID to associate with all transactions
    """
    df = df.copy()

    # Auto-create transaction_id if missing
    if "transaction_id" not in df.columns:
        df["transaction_id"] = range(1, len(df) + 1)

    required = ["transaction_id", "department", "amount", "vendor", "purpose", "transaction_date"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    for _, row in df.iterrows():
        save_transaction({
            "transaction_id": int(row["transaction_id"]),
            "department": row.get("department"),
            "amount": float(row.get("amount", 0)),
            "vendor": row.get("vendor"),
            "purpose": row.get("purpose"),
            "transaction_date": row.get("transaction_date"),
            "risk_score": row.get("risk_score"),
            "severity": row.get("severity"),
            "ai_reason": row.get("ai_reason"),
            "detection_timestamp": row.get("detection_timestamp")
        }, user_id=user_id, organization_id=organization_id)


# =====================================================
# TRANSACTION SAVE / UPDATE - MODIFIED WITH USER_ID AND ORGANIZATION_ID
# =====================================================

def save_transaction(transaction_data, user_id=None, organization_id=None):
    """
    Save or update transaction with optional user_id and organization_id
    
    Args:
        transaction_data: Dictionary with transaction details
        user_id: Optional user ID to associate with transaction
        organization_id: Optional organization ID to associate with transaction
    """
    for key, value in transaction_data.items():
        if isinstance(value, pd.Timestamp):
             transaction_data[key] = value.isoformat()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT transaction_id FROM transactions WHERE transaction_id = ?",
        (transaction_data['transaction_id'],)
    )
    exists = cursor.fetchone()
    
    if exists:
        # Update existing transaction
        if user_id is not None and organization_id is not None:
            cursor.execute("""
                UPDATE transactions SET
                    user_id = ?,
                    organization_id = ?,
                    department = ?,
                    amount = ?,
                    vendor = ?,
                    purpose = ?,
                    transaction_date = ?,
                    risk_score = ?,
                    severity = ?,
                    ai_reason = ?,
                    detection_timestamp = ?
                WHERE transaction_id = ?
            """, (
                user_id,
                organization_id,
                transaction_data.get('department'),
                transaction_data.get('amount'),
                transaction_data.get('vendor'),
                transaction_data.get('purpose'),
                transaction_data.get('transaction_date'),
                transaction_data.get('risk_score'),
                transaction_data.get('severity'),
                transaction_data.get('ai_reason'),
                transaction_data.get('detection_timestamp'),
                transaction_data['transaction_id']
            ))
        else:
            # Preserve existing values if not provided
            cursor.execute("""
                UPDATE transactions SET
                    department = ?,
                    amount = ?,
                    vendor = ?,
                    purpose = ?,
                    transaction_date = ?,
                    risk_score = ?,
                    severity = ?,
                    ai_reason = ?,
                    detection_timestamp = ?
                WHERE transaction_id = ?
            """, (
                transaction_data.get('department'),
                transaction_data.get('amount'),
                transaction_data.get('vendor'),
                transaction_data.get('purpose'),
                transaction_data.get('transaction_date'),
                transaction_data.get('risk_score'),
                transaction_data.get('severity'),
                transaction_data.get('ai_reason'),
                transaction_data.get('detection_timestamp'),
                transaction_data['transaction_id']
            ))
    else:
        # Insert new transaction
        cursor.execute("""
            INSERT INTO transactions (
                transaction_id, user_id, organization_id, department, amount, vendor, purpose,
                transaction_date, risk_score, severity, ai_reason, detection_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction_data['transaction_id'],
            user_id,
            organization_id,
            transaction_data.get('department'),
            transaction_data.get('amount'),
            transaction_data.get('vendor'),
            transaction_data.get('purpose'),
            transaction_data.get('transaction_date'),
            transaction_data.get('risk_score'),
            transaction_data.get('severity'),
            transaction_data.get('ai_reason'),
            transaction_data.get('detection_timestamp')
        ))
    
    conn.commit()
    conn.close()


# =====================================================
# AUDIT ACTIONS
# =====================================================

def save_audit_action(transaction_id, status, auditor_notes, review_timestamp, action_type="update"):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO audit_actions (
            transaction_id, status, auditor_notes, review_timestamp, action_type
        ) VALUES (?, ?, ?, ?, ?)
    """, (transaction_id, status, auditor_notes, review_timestamp, action_type))
    
    conn.commit()
    conn.close()


def get_audit_status(transaction_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT status, auditor_notes, review_timestamp, action_type
        FROM audit_actions
        WHERE transaction_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (transaction_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'status': result[0],
            'auditor_notes': result[1],
            'review_timestamp': result[2],
            'action_type': result[3]
        }
    return None


# =====================================================
# FETCH FUNCTIONS - MODIFIED WITH RBAC AND ORGANIZATION
# =====================================================

def get_transaction_with_audit(transaction_id):
    conn = get_connection()
    
    trans_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE transaction_id = ?",
        conn,
        params=(transaction_id,)
    )
    
    audit_df = pd.read_sql_query(
        "SELECT * FROM audit_actions WHERE transaction_id = ? ORDER BY created_at DESC",
        conn,
        params=(transaction_id,)
    )
    
    conn.close()
    
    if len(trans_df) == 0:
        return None
    
    return {
        'transaction': trans_df.to_dict('records')[0],
        'audit_actions': audit_df.to_dict('records')
    }


def get_all_transactions(filters=None, user_id=None, user_role=None, organization_id=None):
    """
    Get transactions with RBAC and organization filtering
    
    Args:
        filters: Optional filters (department, severity)
        user_id: Current user's ID for RBAC
        user_role: Current user's role ('admin', 'auditor', 'viewer')
        organization_id: Organization ID for multi-tenant filtering
    
    Returns:
        DataFrame of transactions (filtered by role and organization)
    """
    conn = get_connection()
    
    query = "SELECT * FROM transactions"
    params = []
    conditions = []
    
    # Organization filtering (always applied if provided)
    if organization_id is not None:
        conditions.append("organization_id = ?")
        params.append(organization_id)
    
    # RBAC: Non-admins can only see their own data
    if user_role != 'admin' and user_id is not None:
        conditions.append("user_id = ?")
        params.append(user_id)
    
    # Additional filters
    if filters:
        if filters.get('department'):
            conditions.append("department = ?")
            params.append(filters['department'])
        if filters.get('severity'):
            conditions.append("severity = ?")
            params.append(filters['severity'])
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    df = pd.read_sql_query(query, conn, params=params if params else None)
    conn.close()
    
    return df


# ========== MODIFIED: GET USER-SPECIFIC TRANSACTIONS ==========
def get_user_transactions(user_id, filters=None):
    """
    Get transactions for a specific user
    
    Args:
        user_id: User ID to filter by
        filters: Optional additional filters (department, severity)
    
    Returns:
        DataFrame of user's transactions
    """
    conn = get_connection()
    
    query = "SELECT * FROM transactions WHERE user_id = ?"
    params = [user_id]
    
    if filters:
        if filters.get('department'):
            query += " AND department = ?"
            params.append(filters['department'])
        if filters.get('severity'):
            query += " AND severity = ?"
            params.append(filters['severity'])
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df
# ========== END FUNCTION ==========


# =====================================================
# DASHBOARD SUMMARY - MODIFIED WITH RBAC AND ORGANIZATION
# =====================================================

def get_audit_summary(user_id=None, user_role=None, organization_id=None):
    """
    Get audit summary with RBAC and organization filtering
    
    Args:
        user_id: Current user's ID
        user_role: Current user's role
        organization_id: Organization ID for multi-tenant filtering
    
    Returns:
        Dictionary with summary metrics
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Build WHERE clause
    where_clauses = []
    params = []
    
    # Organization filtering (always applied if provided)
    if organization_id is not None:
        where_clauses.append("organization_id = ?")
        params.append(organization_id)
    
    # RBAC filtering
    if user_role != 'admin' and user_id is not None:
        where_clauses.append("user_id = ?")
        params.append(user_id)
    
    where_clause = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    # Total transactions
    cursor.execute(f"SELECT COUNT(*) FROM transactions{where_clause}", params)
    total_trans = cursor.fetchone()[0]
    
    # Severity counts
    cursor.execute(f"SELECT severity, COUNT(*) FROM transactions{where_clause} GROUP BY severity", params)
    severity_counts = dict(cursor.fetchall())
    
    # Status counts
    if where_clauses:
        cursor.execute(f"""
            SELECT status, COUNT(DISTINCT transaction_id)
            FROM audit_actions
            WHERE transaction_id IN (SELECT transaction_id FROM transactions{where_clause})
            AND id IN (SELECT MAX(id) FROM audit_actions GROUP BY transaction_id)
            GROUP BY status
        """, params)
    else:
        cursor.execute("""
            SELECT status, COUNT(DISTINCT transaction_id)
            FROM audit_actions
            WHERE id IN (SELECT MAX(id) FROM audit_actions GROUP BY transaction_id)
            GROUP BY status
        """)
    
    status_counts = dict(cursor.fetchall())
    
    conn.close()
    
    return {
        'total_transactions': total_trans,
        'severity_counts': severity_counts,
        'status_counts': status_counts
    }


# =====================================================
# HISTORY LOGGING
# =====================================================

def log_audit_history(transaction_id, field_changed, old_value, new_value):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO audit_history (transaction_id, field_changed, old_value, new_value)
        VALUES (?, ?, ?, ?)
    """, (transaction_id, str(field_changed), str(old_value), str(new_value)))
    
    conn.commit()
    conn.close()


# =====================================================
# EXPORT
# =====================================================

def export_transactions_to_csv(filepath, filters=None):
    df = get_all_transactions(filters)
    df.to_csv(filepath, index=False)
    return filepath


# =====================================================
# MAINTENANCE
# =====================================================

def clear_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM audit_history")
    cursor.execute("DELETE FROM audit_actions")
    cursor.execute("DELETE FROM transactions")
    # Note: We don't delete users or organizations tables for security reasons
    
    conn.commit()
    conn.close()
    print("✓ Database cleared (users and organizations tables preserved)")


# =====================================================
# INIT
# =====================================================

if __name__ == "__main__":
    init_database()
