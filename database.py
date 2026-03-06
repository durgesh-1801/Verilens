"""
Database Layer for AI Fraud Detection System
SQLite-based persistence for transactions and audit actions
Enhanced with Audit Case Lifecycle Management and Safe Migration
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Database file location
DB_PATH = Path("fraud_detection.db")


# =====================================================
# CONNECTION
# =====================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


# =====================================================
# AUDIT CASES TABLE (ENHANCED WITH SAFE MIGRATION)
# =====================================================

def init_audit_cases_table():
    """Initialize audit cases table with all columns"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='audit_cases'
    """)
    table_exists = cursor.fetchone() is not None
    
    if not table_exists:
        # Create new table with all columns
        cursor.execute("""
            CREATE TABLE audit_cases (
                case_id TEXT PRIMARY KEY,
                transaction_id INTEGER,
                status TEXT,
                case_priority TEXT,
                assigned_to TEXT,
                auditor_comment TEXT,
                resolution TEXT,
                created_at TEXT,
                due_date TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_cases_status 
            ON audit_cases(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_cases_transaction 
            ON audit_cases(transaction_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_cases_priority 
            ON audit_cases(case_priority)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_cases_due_date 
            ON audit_cases(due_date)
        """)
        
        print("✓ Created audit_cases table with priority and SLA columns")
    else:
        # Table exists - migration will be handled separately
        print("✓ Audit_cases table exists - checking for migrations")
    
    conn.commit()
    conn.close()


def migrate_audit_cases_table():
    """
    Safely migrate audit_cases table to add new columns.
    Preserves all existing data.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='audit_cases'
        """)
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("✓ No migration needed - table will be created fresh")
            conn.close()
            return
        
        # Get current table structure
        cursor.execute("PRAGMA table_info(audit_cases)")
        columns = [row[1] for row in cursor.fetchall()]
        
        migrations_needed = []
        
        # Check for missing columns
        if 'case_priority' not in columns:
            migrations_needed.append('case_priority')
        
        if 'due_date' not in columns:
            migrations_needed.append('due_date')
        
        if not migrations_needed:
            print("✓ No migrations needed for audit_cases table")
            conn.close()
            return
        
        print(f"⚠️ Migration needed: Adding columns {migrations_needed}")
        
        # SQLite doesn't support adding multiple columns at once
        # and doesn't support adding columns with constraints
        # So we need to recreate the table
        
        # Step 1: Rename old table
        cursor.execute("ALTER TABLE audit_cases RENAME TO audit_cases_old")
        print("  → Renamed old table to audit_cases_old")
        
        # Step 2: Create new table with all columns
        cursor.execute("""
            CREATE TABLE audit_cases (
                case_id TEXT PRIMARY KEY,
                transaction_id INTEGER,
                status TEXT,
                case_priority TEXT,
                assigned_to TEXT,
                auditor_comment TEXT,
                resolution TEXT,
                created_at TEXT,
                due_date TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  → Created new audit_cases table with new columns")
        
        # Step 3: Copy data from old table
        # Get columns from old table
        cursor.execute("PRAGMA table_info(audit_cases_old)")
        old_columns = [row[1] for row in cursor.fetchall()]
        old_columns_str = ', '.join(old_columns)
        
        # Build INSERT statement with matching columns
        cursor.execute(f"""
            INSERT INTO audit_cases ({old_columns_str})
            SELECT {old_columns_str} FROM audit_cases_old
        """)
        
        rows_migrated = cursor.rowcount
        print(f"  → Copied {rows_migrated} rows from old table")
        
        # Step 4: Update NULL values for new columns with defaults
        if 'case_priority' in migrations_needed:
            cursor.execute("UPDATE audit_cases SET case_priority = 'Medium' WHERE case_priority IS NULL")
            print("  → Added case_priority column with default 'Medium'")
        
        if 'due_date' in migrations_needed:
            # Calculate due dates for existing cases based on default 5 days
            cursor.execute("""
                UPDATE audit_cases 
                SET due_date = datetime(created_at, '+5 days')
                WHERE due_date IS NULL AND created_at IS NOT NULL
            """)
            print("  → Added due_date column with default +5 days from created_at")
        
        # Step 5: Drop old table
        cursor.execute("DROP TABLE audit_cases_old")
        print("  → Dropped old table")
        
        # Step 6: Recreate indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_cases_status 
            ON audit_cases(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_cases_transaction 
            ON audit_cases(transaction_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_cases_priority 
            ON audit_cases(case_priority)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_cases_due_date 
            ON audit_cases(due_date)
        """)
        
        print("  → Recreated indexes")
        
        conn.commit()
        print("✓ Migration completed successfully")
        
    except Exception as e:
        print(f"⚠️ Migration error: {e}")
        # Rollback if error occurs
        try:
            cursor.execute("DROP TABLE IF EXISTS audit_cases")
            cursor.execute("ALTER TABLE audit_cases_old RENAME TO audit_cases")
            conn.commit()
            print("✓ Rolled back migration - old table restored")
        except Exception as rollback_error:
            print(f"❌ Rollback failed: {rollback_error}")
            print("   Manual intervention may be needed")
    
    finally:
        conn.close()


# =====================================================
# INITIALIZATION
# =====================================================

def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Organizations table
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
    
    # Transactions table
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
    
    # Audit actions table
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
    
    # Audit history table
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
    
    # Users table
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
        CREATE INDEX IF NOT EXISTS idx_users_username 
        ON users(username)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_email 
        ON users(email)
    """)
    
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
    
    conn.commit()
    conn.close()
    
    # Initialize audit cases table (separate connection)
    init_audit_cases_table()
    
    # Run migration (separate connection)
    migrate_audit_cases_table()
    
    print("✓ Database initialized successfully")


# =====================================================
# ORGANIZATION MANAGEMENT
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
# DATAFRAME INSERT
# =====================================================

def insert_dataframe(df: pd.DataFrame, user_id=None, organization_id=None):
    """
    Insert dataframe with user_id and organization_id
    
    Args:
        df: DataFrame to insert
        user_id: Optional user ID
        organization_id: Optional organization ID
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
# TRANSACTION SAVE / UPDATE
# =====================================================

def save_transaction(transaction_data, user_id=None, organization_id=None):
    """
    Save or update transaction with user_id and organization_id
    
    Args:
        transaction_data: Dictionary with transaction details
        user_id: Optional user ID
        organization_id: Optional organization ID
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
# FETCH FUNCTIONS
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
    """
    conn = get_connection()
    
    query = "SELECT * FROM transactions"
    params = []
    conditions = []
    
    # Organization filtering
    if organization_id is not None:
        conditions.append("organization_id = ?")
        params.append(organization_id)
    
    # RBAC
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


def get_user_transactions(user_id, filters=None):
    """Get transactions for a specific user"""
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


# =====================================================
# DASHBOARD SUMMARY
# =====================================================

def get_audit_summary(user_id=None, user_role=None, organization_id=None):
    """Get audit summary with RBAC and organization filtering"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Build WHERE clause
    where_clauses = []
    params = []
    
    if organization_id is not None:
        where_clauses.append("organization_id = ?")
        params.append(organization_id)
    
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
# AUDIT CASES FUNCTIONS
# =====================================================

def insert_audit_cases(df: pd.DataFrame):
    """
    Insert or update audit cases from DataFrame.
    Enhanced to include priority and due_date.
    
    Args:
        df: DataFrame with audit case columns
    """
    if 'audit_case_id' not in df.columns:
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Filter rows that have case IDs
    cases_df = df[df['audit_case_id'].notna()].copy()
    
    for _, row in cases_df.iterrows():
        case_id = row.get('audit_case_id')
        
        if not case_id:
            continue
        
        # Check if case exists
        cursor.execute("SELECT case_id FROM audit_cases WHERE case_id = ?", (case_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing case
            cursor.execute("""
                UPDATE audit_cases SET
                    status = ?,
                    case_priority = ?,
                    assigned_to = ?,
                    auditor_comment = ?,
                    resolution = ?,
                    due_date = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE case_id = ?
            """, (
                row.get('audit_status', 'Open'),
                row.get('case_priority'),
                row.get('assigned_to'),
                row.get('auditor_comment', ''),
                row.get('resolution', 'Pending'),
                row.get('due_date'),
                case_id
            ))
        else:
            # Insert new case
            cursor.execute("""
                INSERT INTO audit_cases (
                    case_id, transaction_id, status, case_priority, assigned_to, 
                    auditor_comment, resolution, created_at, due_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                case_id,
                int(row.get('transaction_id', 0)),
                row.get('audit_status', 'Open'),
                row.get('case_priority'),
                row.get('assigned_to'),
                row.get('auditor_comment', ''),
                row.get('resolution', 'Pending'),
                row.get('case_created_at', datetime.now().isoformat()),
                row.get('due_date')
            ))
    
    conn.commit()
    conn.close()


def get_audit_cases(status_filter=None, priority_filter=None):
    """
    Get audit cases from database.
    
    Args:
        status_filter: Optional status to filter by
        priority_filter: Optional priority to filter by
        
    Returns:
        DataFrame of audit cases
    """
    conn = get_connection()
    
    query = "SELECT * FROM audit_cases WHERE 1=1"
    params = []
    
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    
    if priority_filter:
        query += " AND case_priority = ?"
        params.append(priority_filter)
    
    query += " ORDER BY created_at DESC"
    
    if params:
        df = pd.read_sql_query(query, conn, params=params)
    else:
        df = pd.read_sql_query(query, conn)
    
    conn.close()
    return df


def get_overdue_cases_from_db():
    """
    Get overdue cases from database.
    
    Returns:
        DataFrame of overdue cases
    """
    conn = get_connection()
    
    # Get all non-closed cases
    query = """
        SELECT * FROM audit_cases 
        WHERE status != 'Closed' 
        AND due_date IS NOT NULL
        ORDER BY due_date ASC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if len(df) == 0:
        return df
    
    # Filter overdue
    now = datetime.now()
    overdue_mask = []
    
    for idx, row in df.iterrows():
        try:
            due_date = datetime.fromisoformat(row['due_date'])
            overdue_mask.append(now > due_date)
        except:
            overdue_mask.append(False)
    
    return df[overdue_mask].copy()


def update_audit_case(case_id: str, field: str, value):
    """
    Update a specific field of an audit case.
    
    Args:
        case_id: Case ID to update
        field: Field name to update
        value: New value
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    allowed_fields = ['status', 'case_priority', 'assigned_to', 'auditor_comment', 'resolution', 'due_date']
    
    if field not in allowed_fields:
        return False, f"Field '{field}' cannot be updated"
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = f"UPDATE audit_cases SET {field} = ?, updated_at = CURRENT_TIMESTAMP WHERE case_id = ?"
        cursor.execute(query, (value, case_id))
        
        conn.commit()
        conn.close()
        
        return True, f"Case {case_id} updated successfully"
    
    except Exception as e:
        return False, f"Error updating case: {str(e)}"


def get_case_summary_from_db():
    """
    Get summary of audit cases from database.
    Enhanced with priority and SLA metrics.
    
    Returns:
        Dictionary with case counts
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM audit_cases")
    total_cases = cursor.fetchone()[0]
    
    cursor.execute("SELECT status, COUNT(*) FROM audit_cases GROUP BY status")
    status_counts = dict(cursor.fetchall())
    
    cursor.execute("SELECT case_priority, COUNT(*) FROM audit_cases GROUP BY case_priority")
    priority_counts = dict(cursor.fetchall())
    
    # Count overdue cases
    cursor.execute("""
        SELECT COUNT(*) FROM audit_cases 
        WHERE status != 'Closed' 
        AND due_date IS NOT NULL 
        AND due_date < ?
    """, (datetime.now().isoformat(),))
    overdue_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_cases': total_cases,
        'open_cases': status_counts.get('Open', 0),
        'under_review': status_counts.get('Under Review', 0),
        'escalated': status_counts.get('Escalated', 0),
        'closed_cases': status_counts.get('Closed', 0),
        'high_priority': priority_counts.get('High', 0),
        'medium_priority': priority_counts.get('Medium', 0),
        'low_priority': priority_counts.get('Low', 0),
        'overdue_cases': overdue_count
    }


# =====================================================
# MAINTENANCE
# =====================================================

def vacuum_database():
    """Optimize database by running VACUUM"""
    conn = get_connection()
    conn.execute("VACUUM")
    conn.close()


def get_database_stats():
    """Get database statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM transactions")
    trans_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM audit_actions")
    actions_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM organizations")
    orgs_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM audit_cases")
    cases_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'transactions': trans_count,
        'audit_actions': actions_count,
        'users': users_count,
        'organizations': orgs_count,
        'audit_cases': cases_count
    }
