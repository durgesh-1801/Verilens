"""
Audit Rule Engine
Intelligent auditing layer that applies rule-based logic to detect suspicious transactions.
This module works on DataFrames after pipeline processing and adds audit intelligence.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


# =====================================================
# AUDIT RULE CONFIGURATION
# =====================================================

# Risk scoring weights for each rule type
RULE_WEIGHTS = {
    'minor': 15,    # Low-impact rules (e.g., weekend transactions)
    'medium': 25,   # Medium-impact rules (e.g., frequent vendor)
    'major': 40     # High-impact rules (e.g., statistical anomalies, high outliers)
}

# Severity thresholds
SEVERITY_THRESHOLDS = {
    'Low': (0, 30),
    'Medium': (31, 70),
    'High': (71, 100)
}


# =====================================================
# MAIN AUDIT FUNCTION
# =====================================================

def generate_audit_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply audit rules to a DataFrame and generate audit flags with risk scores.
    
    This function processes transactions after the data pipeline and adds:
    - audit_flags: List of human-readable audit reasons
    - audit_risk_score: Numerical risk score (0-100)
    - audit_severity: Categorical severity ("Low", "Medium", "High")
    
    Args:
        df: DataFrame with processed transaction data
        
    Returns:
        DataFrame with additional audit columns
        
    Example:
        >>> df_audited = generate_audit_flags(df_processed)
        >>> high_risk = df_audited[df_audited['audit_severity'] == 'High']
    """
    # Create a copy to avoid modifying original
    df_audit = df.copy()
    
    # Initialize audit columns
    df_audit['audit_flags'] = [[] for _ in range(len(df_audit))]
    df_audit['audit_risk_score'] = 0
    
    # Apply each audit rule
    df_audit = _apply_high_amount_outlier_rule(df_audit)
    df_audit = _apply_frequent_vendor_rule(df_audit)
    df_audit = _apply_weekend_transaction_rule(df_audit)
    df_audit = _apply_zscore_anomaly_rule(df_audit)
    df_audit = _apply_duplicate_suspicion_rule(df_audit)
    
    # Cap risk score at 100
    df_audit['audit_risk_score'] = df_audit['audit_risk_score'].clip(upper=100)
    
    # Assign severity based on risk score
    df_audit['audit_severity'] = df_audit['audit_risk_score'].apply(_calculate_severity)
    # ✅ Convert list flags to string (prevents pandas hashing errors)
    df_audit['audit_flags'] = df_audit['audit_flags'].apply(
    lambda x: '; '.join(x) if isinstance(x, list) else str(x)
    )
    return df_audit


# =====================================================
# INDIVIDUAL AUDIT RULES
# =====================================================

def _apply_high_amount_outlier_rule(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rule 1: High Amount Outlier
    
    Flags transactions where the amount exceeds 2.5 times the department average.
    This indicates potentially inflated or fraudulent expenditures.
    
    Risk Level: Major (40 points)
    """
    if 'amount' not in df.columns or 'department' not in df.columns:
        return df
    
    try:
        # Calculate department averages
        dept_avg = df.groupby('department')['amount'].transform('mean')
        
        # Identify outliers (amount > 2.5 × department average)
        outlier_mask = df['amount'] > (2.5 * dept_avg)
        
        # Add flags and scores for outliers
        for idx in df[outlier_mask].index:
            df.at[idx, 'audit_flags'].append("Amount significantly higher than department norm")
            df.at[idx, 'audit_risk_score'] += RULE_WEIGHTS['major']
    
    except Exception as e:
        print(f"Warning: High amount outlier rule failed - {e}")
    
    return df


def _apply_frequent_vendor_rule(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rule 2: Frequent Vendor Risk
    
    Flags vendors whose transaction count is in the top 5%.
    Unusually frequent transactions with a single vendor may indicate:
    - Vendor favoritism
    - Shell company transactions
    - Kickback schemes
    
    Risk Level: Medium (25 points)
    """
    if 'vendor_transaction_count' not in df.columns:
        return df
    
    try:
        # Calculate 95th percentile threshold
        threshold = df['vendor_transaction_count'].quantile(0.95)
        
        # Identify frequent vendors
        frequent_mask = df['vendor_transaction_count'] >= threshold
        
        # Add flags and scores
        for idx in df[frequent_mask].index:
            df.at[idx, 'audit_flags'].append("Vendor unusually frequent")
            df.at[idx, 'audit_risk_score'] += RULE_WEIGHTS['medium']
    
    except Exception as e:
        print(f"Warning: Frequent vendor rule failed - {e}")
    
    return df


def _apply_weekend_transaction_rule(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rule 3: Weekend Transaction
    
    Flags transactions executed on weekends (Saturday or Sunday).
    Weekend transactions are unusual for most government/business operations
    and may indicate:
    - Unauthorized access
    - Backdating attempts
    - After-hours fraud
    
    Risk Level: Minor (15 points)
    """
    if 'is_weekend' not in df.columns:
        return df
    
    try:
        # Identify weekend transactions
        weekend_mask = df['is_weekend'] == 1
        
        # Add flags and scores
        for idx in df[weekend_mask].index:
            df.at[idx, 'audit_flags'].append("Transaction executed on weekend")
            df.at[idx, 'audit_risk_score'] += RULE_WEIGHTS['minor']
    
    except Exception as e:
        print(f"Warning: Weekend transaction rule failed - {e}")
    
    return df


def _apply_zscore_anomaly_rule(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rule 4: Z-Score Statistical Anomaly
    
    Flags transactions with z-scores beyond ±2 standard deviations.
    Z-score measures how many standard deviations a value is from the mean.
    Values beyond ±2 are statistically rare (occur in ~5% of normal distributions).
    
    Risk Level: Major (40 points)
    """
    if 'zscore_amount' not in df.columns:
        return df
    
    try:
        # Identify statistical anomalies (|z-score| > 2)
        anomaly_mask = df['zscore_amount'].abs() > 2
        
        # Add flags and scores
        for idx in df[anomaly_mask].index:
            df.at[idx, 'audit_flags'].append("Statistical anomaly detected")
            df.at[idx, 'audit_risk_score'] += RULE_WEIGHTS['major']
    
    except Exception as e:
        print(f"Warning: Z-score anomaly rule failed - {e}")
    
    return df


def _apply_duplicate_suspicion_rule(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rule 5: Duplicate Suspicion
    
    Flags potential duplicate transactions based on multiple matching fields.
    Duplicates may indicate:
    - Double billing
    - Duplicate payment fraud
    - Data entry errors exploited maliciously
    
    Checks for duplicates across: amount, vendor, purpose, department
    
    Risk Level: Medium (25 points)
    """
    required_cols = ['amount', 'vendor', 'purpose', 'department']
    
    # Check if required columns exist
    if not all(col in df.columns for col in required_cols):
        return df
    
    try:
        # Identify duplicate patterns
        # Duplicates are defined as rows with identical values across key fields
        duplicate_mask = df.duplicated(subset=required_cols, keep=False)
        
        # Add flags and scores for duplicates
        for idx in df[duplicate_mask].index:
            df.at[idx, 'audit_flags'].append("Potential duplicate pattern")
            df.at[idx, 'audit_risk_score'] += RULE_WEIGHTS['medium']
    
    except Exception as e:
        print(f"Warning: Duplicate suspicion rule failed - {e}")
    
    return df


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def _calculate_severity(risk_score: float) -> str:
    """
    Determine severity level based on risk score.
    
    Args:
        risk_score: Numerical risk score (0-100)
        
    Returns:
        Severity category: "Low", "Medium", or "High"
    """
    for severity, (min_score, max_score) in SEVERITY_THRESHOLDS.items():
        if min_score <= risk_score <= max_score:
            return severity
    
    # Default to High if score exceeds 100 (shouldn't happen due to clipping)
    return "High"


def summarize_audit_findings(df: pd.DataFrame) -> Dict[str, int]:
    """
    Generate summary statistics of audit findings.
    
    Provides a high-level overview of how many transactions were flagged
    and their severity distribution. Useful for dashboard metrics and reporting.
    
    Args:
        df: DataFrame with audit columns (must have run generate_audit_flags first)
        
    Returns:
        Dictionary with audit statistics:
        - total_flagged: Number of transactions with at least one flag
        - high_risk_count: Number of high-severity transactions
        - medium_risk_count: Number of medium-severity transactions
        - low_risk_count: Number of low-severity transactions
        
    Example:
        >>> summary = summarize_audit_findings(df_audited)
        >>> print(f"High risk transactions: {summary['high_risk_count']}")
    """
    if 'audit_flags' not in df.columns or 'audit_severity' not in df.columns:
        return {
            'total_flagged': 0,
            'high_risk_count': 0,
            'medium_risk_count': 0,
            'low_risk_count': 0
        }
    
    # Count transactions with at least one flag
    total_flagged = df['audit_flags'].apply(lambda x: len(x) > 0).sum()
    
    # Count by severity
    high_risk_count = (df['audit_severity'] == 'High').sum()
    medium_risk_count = (df['audit_severity'] == 'Medium').sum()
    low_risk_count = (df['audit_severity'] == 'Low').sum()
    
    return {
        'total_flagged': int(total_flagged),
        'high_risk_count': int(high_risk_count),
        'medium_risk_count': int(medium_risk_count),
        'low_risk_count': int(low_risk_count)
    }


def get_audit_rules_documentation() -> List[Dict[str, str]]:
    """
    Return documentation of all audit rules for UI display or reporting.
    
    Returns:
        List of rule definitions with descriptions and risk levels
    """
    return [
        {
            'rule_name': 'High Amount Outlier',
            'description': 'Amount exceeds 2.5× department average',
            'risk_level': 'Major',
            'points': RULE_WEIGHTS['major'],
            'flag_message': 'Amount significantly higher than department norm'
        },
        {
            'rule_name': 'Frequent Vendor Risk',
            'description': 'Vendor transaction count in top 5%',
            'risk_level': 'Medium',
            'points': RULE_WEIGHTS['medium'],
            'flag_message': 'Vendor unusually frequent'
        },
        {
            'rule_name': 'Weekend Transaction',
            'description': 'Transaction executed on Saturday or Sunday',
            'risk_level': 'Minor',
            'points': RULE_WEIGHTS['minor'],
            'flag_message': 'Transaction executed on weekend'
        },
        {
            'rule_name': 'Z-Score Anomaly',
            'description': 'Statistical outlier (|z-score| > 2)',
            'risk_level': 'Major',
            'points': RULE_WEIGHTS['major'],
            'flag_message': 'Statistical anomaly detected'
        },
        {
            'rule_name': 'Duplicate Suspicion',
            'description': 'Potential duplicate across amount, vendor, purpose, department',
            'risk_level': 'Medium',
            'points': RULE_WEIGHTS['medium'],
            'flag_message': 'Potential duplicate pattern'
        }
    ]


def filter_by_audit_severity(df: pd.DataFrame, severity: str) -> pd.DataFrame:
    """
    Filter DataFrame to only include transactions of a specific severity.
    
    Args:
        df: DataFrame with audit columns
        severity: Severity level to filter ("Low", "Medium", or "High")
        
    Returns:
        Filtered DataFrame
    """
    if 'audit_severity' not in df.columns:
        return df
    
    return df[df['audit_severity'] == severity].copy()


def get_flagged_transactions(df: pd.DataFrame, min_flags: int = 1) -> pd.DataFrame:
    """
    Get transactions with at least a minimum number of audit flags.
    
    Args:
        df: DataFrame with audit columns
        min_flags: Minimum number of flags required (default: 1)
        
    Returns:
        DataFrame with only flagged transactions
    """
    if 'audit_flags' not in df.columns:
        return pd.DataFrame()
    
    flag_counts = df['audit_flags'].apply(len)
    return df[flag_counts >= min_flags].copy()


# =====================================================
# AUDIT EXPORT UTILITIES
# =====================================================

def export_audit_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a clean audit report DataFrame suitable for export.
    
    Includes only essential audit columns with exploded flags for readability.
    
    Args:
        df: DataFrame with audit columns
        
    Returns:
        Clean DataFrame with audit essentials
    """
    if 'audit_flags' not in df.columns:
        return df
    
    # Select relevant columns
    audit_cols = ['transaction_id', 'department', 'amount', 'vendor', 
                  'audit_risk_score', 'audit_severity', 'audit_flags']
    
    available_cols = [col for col in audit_cols if col in df.columns]
    
    report_df = df[available_cols].copy()
    
    # Convert flags list to string for better readability
    if 'audit_flags' in report_df.columns:
        report_df['audit_flags'] = report_df['audit_flags'].apply(
            lambda x: '; '.join(x) if x else 'No flags'
        )
    
    return report_df


# =====================================================
# VALIDATION
# =====================================================

def validate_dataframe_for_audit(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate that a DataFrame has the necessary columns for audit processing.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Tuple of (is_valid: bool, missing_columns: List[str])
    """
    recommended_columns = [
        'amount', 'department', 'vendor', 'purpose',
        'vendor_transaction_count', 'is_weekend', 'zscore_amount'
    ]
    
    missing = [col for col in recommended_columns if col not in df.columns]
    
    is_valid = len(missing) == 0
    
    return is_valid, missing


# =====================================================
# MODULE INFORMATION
# =====================================================

def get_audit_engine_info() -> Dict[str, any]:
    """
    Return metadata about the audit engine for system documentation.
    
    Returns:
        Dictionary with engine version, rules count, and configuration
    """
    return {
        'version': '1.0.0',
        'total_rules': 5,
        'rule_weights': RULE_WEIGHTS,
        'severity_thresholds': SEVERITY_THRESHOLDS,
        'max_risk_score': 100,
        'rules': get_audit_rules_documentation()
    }


# =====================================================
# EXAMPLE USAGE (FOR TESTING)
# =====================================================

if __name__ == "__main__":
    # Example usage
    print("Audit Engine Module Loaded")
    print(f"Available Rules: {len(get_audit_rules_documentation())}")
    print("\nRule Configuration:")
    for rule in get_audit_rules_documentation():
        print(f"  - {rule['rule_name']}: {rule['points']} points ({rule['risk_level']})")
