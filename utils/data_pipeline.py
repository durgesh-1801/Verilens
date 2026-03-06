"""
Data Pipeline - Real Production-Grade Implementation
Automated column detection, cleaning, enrichment, and validation
Enhanced with Data Quality & Validation Layer
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple, List


# =====================================================
# STANDARD SCHEMA DEFINITION
# =====================================================

STANDARD_SCHEMA = {
    'transaction_id': {'aliases': ['id', 'trans_id', 'transaction_number', 'txn_id'], 'required': False},
    'amount': {'aliases': ['transaction_amount', 'value', 'total', 'sum'], 'required': True},
    'department': {'aliases': ['dept', 'division', 'unit'], 'required': True},
    'vendor': {'aliases': ['supplier', 'vendor_name', 'payee', 'merchant'], 'required': True},
    'purpose': {'aliases': ['description', 'memo', 'notes', 'reason'], 'required': False},
    'date': {'aliases': ['transaction_date', 'trans_date', 'date_of_transaction'], 'required': False},
    'payment_method': {'aliases': ['payment_type', 'method'], 'required': False},
    'approval_status': {'aliases': ['status', 'approval'], 'required': False}
}


# =====================================================
# COLUMN AUTO-DETECTION
# =====================================================

def auto_detect_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    Automatically detect which columns map to standard schema
    
    Args:
        df: Raw input DataFrame
        
    Returns:
        Dictionary mapping standard fields to detected column names
    """
    detected = {}
    
    for standard_field, config in STANDARD_SCHEMA.items():
        # Check exact match first
        if standard_field in df.columns:
            detected[standard_field] = standard_field
            continue
        
        # Check aliases
        for alias in config['aliases']:
            if alias in df.columns:
                detected[standard_field] = alias
                break
            
            # Case-insensitive search
            for col in df.columns:
                if col.lower() == alias.lower():
                    detected[standard_field] = col
                    break
    
    return detected


# =====================================================
# DATA CLEANING
# =====================================================

def clean_dataset(df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Clean and standardize dataset
    
    Args:
        df: Raw DataFrame
        column_mapping: Mapping of standard fields to actual column names
        
    Returns:
        Cleaned DataFrame with standardized column names
    """
    df_clean = df.copy()
    
    # Rename columns to standard names
    rename_dict = {v: k for k, v in column_mapping.items() if v in df.columns}
    df_clean = df_clean.rename(columns=rename_dict)
    
    # Clean amount column
    if 'amount' in df_clean.columns:
        df_clean['amount'] = pd.to_numeric(df_clean['amount'], errors='coerce')
        df_clean['amount'] = df_clean['amount'].fillna(0)
    
    # Clean date column
    if 'date' in df_clean.columns:
        df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')
        # Fill missing dates with today's date
        df_clean['date'] = df_clean['date'].fillna(pd.Timestamp.now())
    
    # Clean text columns
    text_cols = ['department', 'vendor', 'purpose', 'payment_method', 'approval_status']
    for col in text_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna('Unknown')
            df_clean[col] = df_clean[col].astype(str).str.strip()
    
    return df_clean


# =====================================================
# DATA QUALITY & VALIDATION LAYER (NEW)
# =====================================================

def validate_data_quality(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate data quality and add quality flags and scores.
    
    This function detects data quality issues including:
    - Missing critical fields (amount, department, vendor)
    - Negative amounts
    - Extreme outliers (top 1% amounts)
    
    Adds columns:
    - data_quality_flags: List of quality issues detected
    - data_quality_score: Risk score (0-100) where higher = more issues
    
    Scoring:
    - Missing critical field: +40 points
    - Negative amount: +50 points
    - Extreme outlier: +30 points
    
    Args:
        df: DataFrame to validate
        
    Returns:
        DataFrame with quality flags and scores
    """
    df_validated = df.copy()
    
    # Initialize quality columns
    df_validated['data_quality_flags'] = [[] for _ in range(len(df_validated))]
    df_validated['data_quality_score'] = 0
    
    critical_fields = ['amount', 'department', 'vendor']
    
    # Rule 1: Missing Critical Fields
    for field in critical_fields:
        if field in df_validated.columns:
            # Check for missing values
            missing_mask = df_validated[field].isna() | (df_validated[field] == '') | (df_validated[field] == 'Unknown')
            
            for idx in df_validated[missing_mask].index:
                df_validated.at[idx, 'data_quality_flags'].append(f"Missing critical field: {field}")
                df_validated.at[idx, 'data_quality_score'] += 40
        else:
            # Field doesn't exist in dataframe
            for idx in df_validated.index:
                df_validated.at[idx, 'data_quality_flags'].append(f"Missing critical field: {field}")
                df_validated.at[idx, 'data_quality_score'] += 40
    
    # Rule 2: Negative Amounts
    if 'amount' in df_validated.columns:
        negative_mask = df_validated['amount'] < 0
        
        for idx in df_validated[negative_mask].index:
            df_validated.at[idx, 'data_quality_flags'].append("Negative amount detected")
            df_validated.at[idx, 'data_quality_score'] += 50
    
    # Rule 3: Extreme Outliers (Top 1%)
    if 'amount' in df_validated.columns:
        try:
            # Calculate 99th percentile threshold
            threshold = df_validated['amount'].quantile(0.99)
            
            # Identify extreme outliers
            outlier_mask = df_validated['amount'] > threshold
            
            for idx in df_validated[outlier_mask].index:
                df_validated.at[idx, 'data_quality_flags'].append(f"Extreme amount outlier (>${threshold:,.2f})")
                df_validated.at[idx, 'data_quality_score'] += 30
        except Exception as e:
            print(f"Warning: Could not calculate outlier threshold - {e}")
    
    # Cap score at 100
    df_validated['data_quality_score'] = df_validated['data_quality_score'].clip(upper=100)
    
    # Debug prints
    print(f"Data quality validation complete:")
    print(f"  - Total records validated: {len(df_validated)}")
    print(f"  - Records with quality issues: {(df_validated['data_quality_score'] > 0).sum()}")
    print(f"  - Data quality max score: {df_validated['data_quality_score'].max()}")
    print(f"  - Data quality mean score: {df_validated['data_quality_score'].mean():.2f}")
    
    return df_validated


# =====================================================
# FEATURE ENRICHMENT
# =====================================================

def enrich_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived features for better anomaly detection
    
    Args:
        df: Cleaned DataFrame
        
    Returns:
        DataFrame with additional engineered features
    """
    df_enriched = df.copy()
    
    # Feature 1: Monthly spend per department
    if 'amount' in df_enriched.columns and 'department' in df_enriched.columns:
        df_enriched['monthly_spend_per_department'] = df_enriched.groupby('department')['amount'].transform('sum')
    
    # Feature 2: Vendor transaction count
    if 'vendor' in df_enriched.columns:
        df_enriched['vendor_transaction_count'] = df_enriched.groupby('vendor')['vendor'].transform('count')
    
    # Feature 3: Z-score of amount
    if 'amount' in df_enriched.columns:
        mean_amount = df_enriched['amount'].mean()
        std_amount = df_enriched['amount'].std()
        
        if std_amount > 0:
            df_enriched['zscore_amount'] = (df_enriched['amount'] - mean_amount) / std_amount
        else:
            df_enriched['zscore_amount'] = 0
    
    # Feature 4: Amount percentile
    if 'amount' in df_enriched.columns:
        df_enriched['amount_percentile'] = df_enriched['amount'].rank(pct=True) * 100
    
    # Feature 5: Day of week (if date exists)
    if 'date' in df_enriched.columns:
        df_enriched['day_of_week'] = pd.to_datetime(df_enriched['date']).dt.dayofweek
        df_enriched['is_weekend'] = df_enriched['day_of_week'].isin([5, 6]).astype(int)
    
    return df_enriched


# =====================================================
# HEALTH SCORE CALCULATION
# =====================================================

def compute_health_score(df: pd.DataFrame) -> Dict:
    """
    Calculate data quality health metrics
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Dictionary with health metrics
    """
    total_rows = len(df)
    total_cells = df.size
    
    # Completeness: % of non-null values
    non_null = df.count().sum()
    completeness = (non_null / total_cells * 100) if total_cells > 0 else 0
    
    # Validity: % of valid amounts (non-negative, non-zero)
    valid_amounts = 0
    if 'amount' in df.columns:
        valid_amounts = ((df['amount'] > 0) & (df['amount'].notna())).sum()
        validity = (valid_amounts / total_rows * 100) if total_rows > 0 else 0
    else:
        validity = 0
    
    # Duplicates
    duplicates = df.duplicated().sum()
    
    # Overall score (weighted average)
    overall_score = (completeness * 0.4 + validity * 0.4 + (100 - (duplicates / total_rows * 100) if total_rows > 0 else 100) * 0.2)
    
    return {
        'completeness': round(completeness, 2),
        'validity': round(validity, 2),
        'duplicates': int(duplicates),
        'overall_score': round(overall_score, 2)
    }


# =====================================================
# COMPLETE PIPELINE
# =====================================================

def run_complete_pipeline(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Run complete data pipeline: detect, clean, validate, enrich, and score
    Enhanced with data quality validation layer
    
    Args:
        df: Raw input DataFrame
        
    Returns:
        Tuple of (processed DataFrame, health metrics dictionary)
    """
    print("Starting complete data pipeline...")
    
    # Step 1: Auto-detect columns
    print("Step 1/5: Auto-detecting columns...")
    column_mapping = auto_detect_columns(df)
    print(f"  Detected {len(column_mapping)} standard fields")
    
    # Step 2: Clean dataset
    print("Step 2/5: Cleaning dataset...")
    df_clean = clean_dataset(df, column_mapping)
    print(f"  Cleaned {len(df_clean)} records")
    
    # Step 3: Validate data quality (NEW)
    print("Step 3/5: Validating data quality...")
    df_validated = validate_data_quality(df_clean)
    
    # Step 4: Enrich with features
    print("Step 4/5: Enriching features...")
    df_enriched = enrich_features(df_validated)

    # Add transaction_id if missing
    if 'transaction_id' not in df_enriched.columns:
        df_enriched['transaction_id'] = range(1, len(df_enriched) + 1)

    # 🔥 Convert list flags BEFORE computing health score
    if 'data_quality_flags' in df_enriched.columns:
        df_enriched['data_quality_flags'] = df_enriched['data_quality_flags'].apply(
        lambda x: '; '.join(x) if isinstance(x, list) and x else 'No issues'
        )

    # Step 5: Compute health score
    print("Step 5/5: Computing health score...")
    health = compute_health_score(df_enriched)
    # Convert lists to strings for database compatibility
    # Convert list flags to string and DROP list column
    if 'data_quality_flags' in df_enriched.columns:
        df_enriched['data_quality_flags'] = df_enriched['data_quality_flags'].apply(
        lambda x: '; '.join(x) if isinstance(x, list) and x else 'No issues'
        )
        # Keep the list version for in-memory processing, but add string version for DB
    
    print("Pipeline complete!")
    print(f"Final dataset: {len(df_enriched)} rows, {len(df_enriched.columns)} columns")
    
    return df_enriched, health


# =====================================================
# VALIDATION
# =====================================================

def validate_pipeline_output(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate pipeline output meets requirements
    
    Args:
        df: Processed DataFrame
        
    Returns:
        Tuple of (is_valid: bool, issues: List[str])
    """
    issues = []
    
    # Check required columns
    required_cols = ['transaction_id', 'amount', 'department', 'vendor']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        issues.append(f"Missing required columns: {', '.join(missing_cols)}")
    
    # Check for enriched features
    enriched_features = ['monthly_spend_per_department', 'vendor_transaction_count', 'zscore_amount']
    missing_features = [feat for feat in enriched_features if feat not in df.columns]
    
    if missing_features:
        issues.append(f"Missing enriched features: {', '.join(missing_features)}")
    
    # Check for data quality columns
    quality_cols = ['data_quality_flags', 'data_quality_score']
    missing_quality = [col for col in quality_cols if col not in df.columns]
    
    if missing_quality:
        issues.append(f"Missing data quality columns: {', '.join(missing_quality)}")
    
    # Check for nulls in critical columns
    if 'amount' in df.columns:
        null_amounts = df['amount'].isna().sum()
        if null_amounts > 0:
            issues.append(f"{null_amounts} null values in amount column")
    
    is_valid = len(issues) == 0
    
    return is_valid, issues


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def get_pipeline_info() -> Dict:
    """
    Get information about pipeline capabilities
    
    Returns:
        Dictionary with pipeline information
    """
    return {
        'version': '2.0.0',
        'features': [
            'Auto column detection',
            'Data cleaning',
            'Data quality validation',
            'Feature enrichment',
            'Health scoring',
            'Quality flags and scores'
        ],
        'standard_schema': list(STANDARD_SCHEMA.keys()),
        'enriched_features': [
            'monthly_spend_per_department',
            'vendor_transaction_count',
            'zscore_amount',
            'amount_percentile',
            'day_of_week',
            'is_weekend',
            'data_quality_flags',
            'data_quality_score'
        ],
        'quality_checks': [
            'Missing critical fields',
            'Negative amounts',
            'Extreme outliers (top 1%)'
        ]
    }


def convert_lists_to_strings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert any list columns to string format for database storage.
    This prevents unhashable type errors when saving to database.
    
    Args:
        df: DataFrame with potential list columns
        
    Returns:
        DataFrame with lists converted to strings
    """
    df_converted = df.copy()
    
    for col in df_converted.columns:
        # Check if column contains lists
        if df_converted[col].dtype == 'object':
            # Check first non-null value
            first_value = df_converted[col].dropna().iloc[0] if len(df_converted[col].dropna()) > 0 else None
            
            if isinstance(first_value, list):
                # Convert list to semicolon-separated string
                df_converted[col] = df_converted[col].apply(
                    lambda x: '; '.join(map(str, x)) if isinstance(x, list) and x else 'None'
                )
                print(f"Converted column '{col}' from list to string format")
    
    return df_converted


def prepare_for_database(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare DataFrame for database insertion by converting incompatible types.
    
    Args:
        df: Processed DataFrame
        
    Returns:
        Database-ready DataFrame
    """
    df_db = df.copy()
    
    # Convert data_quality_flags list to string if it exists
    if 'data_quality_flags' in df_db.columns:
        df_db['data_quality_flags'] = df_db['data_quality_flags'].apply(
            lambda x: '; '.join(x) if isinstance(x, list) and x else 'No issues'
        )
    
    # Convert any remaining list columns
    df_db = convert_lists_to_strings(df_db)
    
    # Convert dates to ISO format strings
    if 'date' in df_db.columns:
        df_db['date'] = df_db['date'].apply(
            lambda x: x.isoformat() if pd.notna(x) else None
        )
    
    print("DataFrame prepared for database storage")
    
    return df_db


def get_data_quality_summary(df: pd.DataFrame) -> Dict:
    """
    Get summary of data quality issues.
    
    Args:
        df: DataFrame with data_quality_flags and data_quality_score
        
    Returns:
        Dictionary with quality summary
    """
    if 'data_quality_score' not in df.columns:
        return {
            'total_records': len(df),
            'records_with_issues': 0,
            'max_quality_score': 0,
            'mean_quality_score': 0,
            'common_issues': []
        }
    
    records_with_issues = (df['data_quality_score'] > 0).sum()
    max_score = df['data_quality_score'].max()
    mean_score = df['data_quality_score'].mean()
    
    # Get common issues
    common_issues = []
    if 'data_quality_flags' in df.columns:
        all_flags = []
        for flags in df['data_quality_flags']:
            if isinstance(flags, list):
                all_flags.extend(flags)
        
        if all_flags:
            from collections import Counter
            flag_counts = Counter(all_flags)
            common_issues = [{'issue': issue, 'count': count} for issue, count in flag_counts.most_common(5)]
    
    return {
        'total_records': len(df),
        'records_with_issues': int(records_with_issues),
        'max_quality_score': float(max_score),
        'mean_quality_score': round(float(mean_score), 2),
        'common_issues': common_issues
    }


# =====================================================
# EXAMPLE USAGE
# =====================================================

if __name__ == "__main__":
    print("Data Pipeline Module Loaded")
    print(f"Version: {get_pipeline_info()['version']}")
    print(f"Features: {', '.join(get_pipeline_info()['features'])}")
    print(f"Quality Checks: {', '.join(get_pipeline_info()['quality_checks'])}")
