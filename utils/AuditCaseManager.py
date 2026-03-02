"""
Audit Case Manager
Converts flagged transactions into manageable audit cases for investigation
"""

import pandas as pd
from datetime import datetime


def create_audit_cases(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create audit cases for high and medium severity transactions.
    
    Args:
        df: DataFrame with audit_severity column
        
    Returns:
        DataFrame with audit case columns added
    """
    df_cases = df.copy()
    
    # Initialize audit case columns
    df_cases['audit_case_id'] = None
    df_cases['audit_status'] = None
    df_cases['assigned_to'] = None
    df_cases['auditor_comment'] = ""
    df_cases['resolution'] = None
    df_cases['case_created_at'] = None
    
    # Check if audit_severity exists
    if 'audit_severity' not in df_cases.columns:
        return df_cases
    
    # Get current year
    current_year = datetime.now().year
    
    # Filter for High and Medium severity
    flagged_mask = df_cases['audit_severity'].isin(['High', 'Medium'])
    flagged_indices = df_cases[flagged_mask].index
    
    # Generate case IDs
    for idx, row_idx in enumerate(flagged_indices, start=1):
        case_id = f"CASE-{current_year}-{idx:04d}"
        
        df_cases.at[row_idx, 'audit_case_id'] = case_id
        df_cases.at[row_idx, 'audit_status'] = 'Open'
        df_cases.at[row_idx, 'assigned_to'] = None
        df_cases.at[row_idx, 'auditor_comment'] = ""
        df_cases.at[row_idx, 'resolution'] = 'Pending'
        df_cases.at[row_idx, 'case_created_at'] = datetime.now().isoformat()
    
    return df_cases


def update_case_status(df: pd.DataFrame, case_id: str, status: str) -> pd.DataFrame:
    """
    Update the status of an audit case.
    
    Args:
        df: DataFrame with audit cases
        case_id: Case ID to update
        status: New status ('Open', 'Under Review', 'Escalated', 'Closed')
        
    Returns:
        Updated DataFrame
    """
    df_updated = df.copy()
    
    if 'audit_case_id' in df_updated.columns:
        mask = df_updated['audit_case_id'] == case_id
        df_updated.loc[mask, 'audit_status'] = status
        
        # Update resolution based on status
        if status == 'Closed':
            df_updated.loc[mask, 'resolution'] = 'Resolved'
    
    return df_updated


def assign_case(df: pd.DataFrame, case_id: str, auditor_name: str) -> pd.DataFrame:
    """
    Assign an audit case to an auditor.
    
    Args:
        df: DataFrame with audit cases
        case_id: Case ID to assign
        auditor_name: Name of auditor
        
    Returns:
        Updated DataFrame
    """
    df_updated = df.copy()
    
    if 'audit_case_id' in df_updated.columns:
        mask = df_updated['audit_case_id'] == case_id
        df_updated.loc[mask, 'assigned_to'] = auditor_name
        
        # Auto-update status if assigning an open case
        if df_updated.loc[mask, 'audit_status'].iloc[0] == 'Open':
            df_updated.loc[mask, 'audit_status'] = 'Under Review'
    
    return df_updated


def add_case_comment(df: pd.DataFrame, case_id: str, comment: str) -> pd.DataFrame:
    """
    Add a comment to an audit case.
    
    Args:
        df: DataFrame with audit cases
        case_id: Case ID to comment on
        comment: Comment text
        
    Returns:
        Updated DataFrame
    """
    df_updated = df.copy()
    
    if 'audit_case_id' in df_updated.columns:
        mask = df_updated['audit_case_id'] == case_id
        
        # Append comment with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        existing_comment = df_updated.loc[mask, 'auditor_comment'].iloc[0]
        
        if existing_comment:
            new_comment = f"{existing_comment}\n[{timestamp}] {comment}"
        else:
            new_comment = f"[{timestamp}] {comment}"
        
        df_updated.loc[mask, 'auditor_comment'] = new_comment
    
    return df_updated


def get_case_summary(df: pd.DataFrame) -> dict:
    """
    Get summary statistics of audit cases.
    
    Args:
        df: DataFrame with audit cases
        
    Returns:
        Dictionary with case counts by status
    """
    if 'audit_case_id' not in df.columns:
        return {
            'total_cases': 0,
            'open_cases': 0,
            'under_review': 0,
            'escalated': 0,
            'closed_cases': 0
        }
    
    # Filter only rows with case IDs
    cases_df = df[df['audit_case_id'].notna()]
    
    summary = {
        'total_cases': len(cases_df),
        'open_cases': (cases_df['audit_status'] == 'Open').sum(),
        'under_review': (cases_df['audit_status'] == 'Under Review').sum(),
        'escalated': (cases_df['audit_status'] == 'Escalated').sum(),
        'closed_cases': (cases_df['audit_status'] == 'Closed').sum()
    }
    
    return summary
