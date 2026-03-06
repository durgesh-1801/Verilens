"""
Audit Rule Engine
Intelligent auditing layer that applies rule-based logic to detect suspicious transactions.
Enhanced with reasoning categories, risk categorization, and explainable audit intelligence.
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
    'Low': (0, 25),
    'Medium': (26, 50),
    'High': (51, 100)
}

# Risk category mapping
RISK_CATEGORIES = {
    'Financial Risk': ['High Amount Outlier', 'Potential duplicate pattern'],
    'Behavioral Risk': ['Vendor unusually frequent', 'Transaction executed on weekend'],
    'Statistical Risk': ['Statistical anomaly detected']
}


# =====================================================
# MAIN AUDIT FUNCTION
# =====================================================

def generate_audit_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply audit rules to a DataFrame and generate audit flags with risk scores.
    Enhanced with reasoning categories and explanations.
    
    This function processes transactions after the data pipeline and adds:
    - audit_flags: List of human-readable audit reasons
    - audit_risk_score: Numerical risk score (0-100)
    - audit_severity: Categorical severity ("Low", "Medium", "High")
    - audit_reasoning_score: Category-based risk breakdown
    - audit_category: Primary risk category
    - audit_explanation: Human-readable explanation
    
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
    df_audit['financial_risk_score'] = 0
    df_audit['behavioral_risk_score'] = 0
    df_audit['statistical_risk_score'] = 0    
    # Apply each audit rule
    df_audit = _apply_high_amount_outlier_rule(df_audit)
    df_audit = _apply_frequent_vendor_rule(df_audit)
    df_audit = _apply_weekend_transaction_rule(df_audit)
    df_audit = _apply_zscore_anomaly_rule(df_audit)
    df_audit = _apply_duplicate_suspicion_rule(df_audit)
    
    # Cap risk score at 100
    # Combine category scores into total risk score
    df_audit['audit_risk_score'] = (
    df_audit['financial_risk_score'] +
    df_audit['behavioral_risk_score'] +
    df_audit['statistical_risk_score']
    )

    # Cap risk score at 100
    df_audit['audit_risk_score'] = df_audit['audit_risk_score'].clip(upper=100)
    print("Max risk score:", df_audit['audit_risk_score'].max())
    print("Unique risk scores:", df_audit['audit_risk_score'].unique())
    # Assign severity based on risk score
    df_audit['audit_severity'] = df_audit['audit_risk_score'].apply(_calculate_severity)
    
    # Determine primary audit category
    df_audit['audit_category'] = df_audit.apply(_determine_primary_category, axis=1)
    
    # Generate human-readable explanations
    df_audit['audit_explanation'] = df_audit.apply(
        lambda row: generate_audit_explanation(row), axis=1
    )
    df_audit['audit_flags'] = df_audit['audit_flags'].apply(
    lambda x: '; '.join(x) if isinstance(x, list) else x
    )
    return df_audit


# =====================================================
# INDIVIDUAL AUDIT RULES (ENHANCED WITH CATEGORIES)
# =====================================================

def _apply_high_amount_outlier_rule(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rule 1: High Amount Outlier
    
    Flags transactions where the amount exceeds 2.5 times the department average.
    This indicates potentially inflated or fraudulent expenditures.
    
    Risk Level: Major (40 points)
    Category: Financial Risk
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
            df.at[idx, 'financial_risk_score'] += RULE_WEIGHTS['major']
            
            
    
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
    Category: Behavioral Risk
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
            df.at[idx, 'behavioral_risk_score'] += RULE_WEIGHTS['medium']
            
            
    
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
    Category: Behavioral Risk
    """
    if 'is_weekend' not in df.columns:
        return df
    
    try:
        # Identify weekend transactions
        weekend_mask = df['is_weekend'] == 1
        
        # Add flags and scores
        for idx in df[weekend_mask].index:
            df.at[idx, 'audit_flags'].append("Transaction executed on weekend")
            df.at[idx, 'behavioral_risk_score'] += RULE_WEIGHTS['minor']
            
            
    
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
    Category: Statistical Risk
    """
    if 'zscore_amount' not in df.columns:
        return df
    
    try:
        # Identify statistical anomalies (|z-score| > 2)
        anomaly_mask = df['zscore_amount'].abs() > 2
        
        # Add flags and scores
        for idx in df[anomaly_mask].index:
            df.at[idx, 'audit_flags'].append("Statistical anomaly detected")
            df.at[idx, 'statistical_risk_score'] += RULE_WEIGHTS['major']
            
            
    
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
    Category: Financial Risk
    """
    required_cols = ['amount', 'vendor', 'purpose', 'department']
    
    # Check if required columns exist
    if not all(col in df.columns for col in required_cols):
        return df
    
    try:
        # Identify duplicate patterns
        duplicate_mask = df.duplicated(subset=required_cols, keep=False)
        
        # Add flags and scores for duplicates
        for idx in df[duplicate_mask].index:
            df.at[idx, 'audit_flags'].append("Potential duplicate pattern")
            df.at[idx, 'statistical_risk_score'] += RULE_WEIGHTS['medium']
            
            
    
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


def _determine_primary_category(row: pd.Series) -> str:
    scores = {
        "Financial Risk": row.get("financial_risk_score", 0),
        "Behavioral Risk": row.get("behavioral_risk_score", 0),
        "Statistical Risk": row.get("statistical_risk_score", 0),
    }

    primary = max(scores.items(), key=lambda x: x[1])
    return primary[0] if primary[1] > 0 else "None"

def generate_audit_explanation(row: pd.Series) -> str:
    """
    Generate human-readable explanation for audit findings.
    
    Combines multiple risk indicators into a coherent narrative explaining
    why the transaction was flagged and what the risk profile indicates.
    
    Args:
        row: DataFrame row with audit columns
        
    Returns:
        Human-readable explanation string
        
    Example:
        "High financial deviation combined with statistical anomaly indicates 
        elevated fraud probability."
    """
    # Check if row has audit data
    if 'audit_flags' not in row or not row['audit_flags']:
        return "No audit concerns detected."
    
    flags = row['audit_flags']
    if isinstance(flags, str):
        flags = [f.strip() for f in flags.split(";") if f.strip()]
    elif not isinstance(flags, list):
        flags = []
    reasoning = row.get('audit_reasoning_score', {})
    severity = row.get('audit_severity', 'Low')
    category = row.get('audit_category', 'None')
    
    # Build explanation based on flags and categories
    explanations = []
    
    # Categorize flags
    financial_flags = []
    behavioral_flags = []
    statistical_flags = []
    
    for flag in flags:
        if any(cat_flag in flag for cat_flag in RISK_CATEGORIES['Financial Risk']):
            financial_flags.append(flag)
        elif any(cat_flag in flag for cat_flag in RISK_CATEGORIES['Behavioral Risk']):
            behavioral_flags.append(flag)
        elif any(cat_flag in flag for cat_flag in RISK_CATEGORIES['Statistical Risk']):
            statistical_flags.append(flag)
    
    # Build narrative based on combinations
    risk_components = []
    
    if financial_flags:
        if len(financial_flags) > 1:
            risk_components.append("multiple financial irregularities")
        else:
            risk_components.append("financial deviation")
    
    if behavioral_flags:
        if len(behavioral_flags) > 1:
            risk_components.append("suspicious behavioral patterns")
        else:
            risk_components.append("behavioral anomaly")
    
    if statistical_flags:
        risk_components.append("statistical anomaly")
    
    # Construct explanation
    if len(risk_components) == 0:
        explanation = "Transaction flagged for review."
    elif len(risk_components) == 1:
        if severity == "High":
            explanation = f"{severity} severity {risk_components[0]} detected, indicating elevated fraud risk."
        else:
            explanation = f"{risk_components[0].capitalize()} detected, requiring further review."
    elif len(risk_components) == 2:
        explanation = f"{risk_components[0].capitalize()} combined with {risk_components[1]} indicates elevated fraud probability."
    else:
        explanation = f"Multiple risk indicators detected: {', '.join(risk_components)}. Comprehensive investigation recommended."
    
    # Add category emphasis for high-risk cases
    if severity == "High" and category != "None":
        explanation += f" Primary concern: {category}."
    
    # Add specific flag details for context
    if len(flags) <= 2:
        flag_details = " Specifically: " + "; ".join(flags).lower() + "."
        explanation += flag_details
    
    return explanation


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
        - financial_risk_count: Transactions with financial risk
        - behavioral_risk_count: Transactions with behavioral risk
        - statistical_risk_count: Transactions with statistical risk
        
    Example:
        >>> summary = summarize_audit_findings(df_audited)
        >>> print(f"High risk transactions: {summary['high_risk_count']}")
    """
    if 'audit_flags' not in df.columns or 'audit_severity' not in df.columns:
        return {
            'total_flagged': 0,
            'high_risk_count': 0,
            'medium_risk_count': 0,
            'low_risk_count': 0,
            'financial_risk_count': 0,
            'behavioral_risk_count': 0,
            'statistical_risk_count': 0
        }
    
    # Count transactions with at least one flag
    total_flagged = df['audit_flags'].apply(lambda x: len(x) > 0).sum()
    
    # Count by severity
    high_risk_count = (df['audit_severity'] == 'High').sum()
    medium_risk_count = (df['audit_severity'] == 'Medium').sum()
    low_risk_count = (df['audit_severity'] == 'Low').sum()
    
    # Count by category
    financial_risk_count = 0
    behavioral_risk_count = 0
    statistical_risk_count = 0
    
    if 'audit_category' in df.columns:
        financial_risk_count = (df['audit_category'] == 'Financial Risk').sum()
        behavioral_risk_count = (df['audit_category'] == 'Behavioral Risk').sum()
        statistical_risk_count = (df['audit_category'] == 'Statistical Risk').sum()
    
    return {
        'total_flagged': int(total_flagged),
        'high_risk_count': int(high_risk_count),
        'medium_risk_count': int(medium_risk_count),
        'low_risk_count': int(low_risk_count),
        'financial_risk_count': int(financial_risk_count),
        'behavioral_risk_count': int(behavioral_risk_count),
        'statistical_risk_count': int(statistical_risk_count)
    }


def get_audit_rules_documentation() -> List[Dict[str, str]]:
    """
    Return documentation of all audit rules for UI display or reporting.
    Enhanced with category information.
    
    Returns:
        List of rule definitions with descriptions, risk levels, and categories
    """
    return [
        {
            'rule_name': 'High Amount Outlier',
            'description': 'Amount exceeds 2.5× department average',
            'risk_level': 'Major',
            'category': 'Financial Risk',
            'points': RULE_WEIGHTS['major'],
            'flag_message': 'Amount significantly higher than department norm'
        },
        {
            'rule_name': 'Frequent Vendor Risk',
            'description': 'Vendor transaction count in top 5%',
            'risk_level': 'Medium',
            'category': 'Behavioral Risk',
            'points': RULE_WEIGHTS['medium'],
            'flag_message': 'Vendor unusually frequent'
        },
        {
            'rule_name': 'Weekend Transaction',
            'description': 'Transaction executed on Saturday or Sunday',
            'risk_level': 'Minor',
            'category': 'Behavioral Risk',
            'points': RULE_WEIGHTS['minor'],
            'flag_message': 'Transaction executed on weekend'
        },
        {
            'rule_name': 'Z-Score Anomaly',
            'description': 'Statistical outlier (|z-score| > 2)',
            'risk_level': 'Major',
            'category': 'Statistical Risk',
            'points': RULE_WEIGHTS['major'],
            'flag_message': 'Statistical anomaly detected'
        },
        {
            'rule_name': 'Duplicate Suspicion',
            'description': 'Potential duplicate across amount, vendor, purpose, department',
            'risk_level': 'Medium',
            'category': 'Financial Risk',
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


def filter_by_audit_category(df: pd.DataFrame, category: str) -> pd.DataFrame:
    """
    Filter DataFrame to only include transactions of a specific risk category.
    
    Args:
        df: DataFrame with audit columns
        category: Risk category to filter ("Financial Risk", "Behavioral Risk", "Statistical Risk")
        
    Returns:
        Filtered DataFrame
    """
    if 'audit_category' not in df.columns:
        return df
    
    return df[df['audit_category'] == category].copy()


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
    
    flag_counts = df['audit_flags'].apply(
    lambda x: len(x.split(";")) if isinstance(x, str) and x else 0
    )
    return df[flag_counts >= min_flags].copy()


def get_category_breakdown(df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
    """
    Get detailed breakdown of risk categories and their severity distribution.
    
    Args:
        df: DataFrame with audit columns
        
    Returns:
        Nested dictionary with category -> severity -> count
    """
    if 'audit_category' not in df.columns or 'audit_severity' not in df.columns:
        return {}
    
    breakdown = {}
    
    for category in ['Financial Risk', 'Behavioral Risk', 'Statistical Risk']:
        category_df = df[df['audit_category'] == category]
        
        if len(category_df) > 0:
            breakdown[category] = {
                'High': (category_df['audit_severity'] == 'High').sum(),
                'Medium': (category_df['audit_severity'] == 'Medium').sum(),
                'Low': (category_df['audit_severity'] == 'Low').sum(),
                'Total': len(category_df)
            }
    
    return breakdown


# =====================================================
# AUDIT EXPORT UTILITIES
# =====================================================

def export_audit_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a clean audit report DataFrame suitable for export.
    Enhanced with category and explanation columns.
    
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
                  'audit_risk_score', 'audit_severity', 'audit_category',
                  'audit_explanation', 'audit_flags']
    
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
    Enhanced with category information.
    
    Returns:
        Dictionary with engine version, rules count, categories, and configuration
    """
    return {
        'version': '2.0.0',
        'total_rules': 5,
        'rule_weights': RULE_WEIGHTS,
        'severity_thresholds': SEVERITY_THRESHOLDS,
        'risk_categories': list(RISK_CATEGORIES.keys()),
        'max_risk_score': 100,
        'features': [
            'Multi-category risk assessment',
            'Reasoning score breakdown',
            'Automated explanation generation',
            'Category-based filtering'
        ],
        'rules': get_audit_rules_documentation()
    }


# =====================================================
# BACKWARD COMPATIBILITY CHECK
# =====================================================

def is_backward_compatible(df: pd.DataFrame) -> bool:
    """
    Check if DataFrame has the minimum columns for basic audit functionality.
    Enhanced audit features will be skipped if columns are missing.
    
    Args:
        df: DataFrame to check
        
    Returns:
        True if minimum columns exist
    """
    minimum_columns = ['amount', 'department']
    return all(col in df.columns for col in minimum_columns)


# =====================================================
# EXAMPLE USAGE (FOR TESTING)
# =====================================================

if __name__ == "__main__":
    # Example usage
    print("Enhanced Audit Engine Module Loaded")
    print(f"Version: {get_audit_engine_info()['version']}")
    print(f"Available Rules: {len(get_audit_rules_documentation())}")
    print(f"Risk Categories: {', '.join(get_audit_engine_info()['risk_categories'])}")
    print("\nRule Configuration:")
    for rule in get_audit_rules_documentation():
        print(f"  - {rule['rule_name']}: {rule['points']} points ({rule['risk_level']}) - {rule['category']}")
