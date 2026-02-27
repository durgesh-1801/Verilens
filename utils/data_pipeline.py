"""
Data Pipeline Module for AI Fraud Detection System
Handles auto-detection, cleaning, validation, and feature enrichment
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import re
from datetime import datetime
from scipy import stats


# ==========================================
# AUTO-DETECT COLUMNS
# ==========================================
def auto_detect_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """
    Automatically detect which columns map to standard fields using
    keyword similarity and data type heuristics.
    
    Args:
        df: Input dataframe with any column names
    
    Returns:
        Dictionary mapping standard fields to detected column names
        Example: {
            'transaction_id': 'ID',
            'amount': 'Total_Amount',
            'date': 'Transaction_Date',
            'department': 'Dept',
            'vendor': 'Supplier_Name',
            'purpose': 'Description'
        }
    """
    detected = {
        'transaction_id': None,
        'amount': None,
        'date': None,
        'department': None,
        'vendor': None,
        'purpose': None
    }
    
    # Keywords for each field type
    keywords = {
        'transaction_id': ['id', 'transaction_id', 'txn_id', 'trans_id', 'receipt', 'reference', 'ref_no'],
        'amount': ['amount', 'amt', 'total', 'value', 'price', 'cost', 'payment', 'sum'],
        'date': ['date', 'datetime', 'timestamp', 'created', 'trans_date', 'transaction_date'],
        'department': ['department', 'dept', 'division', 'unit', 'section', 'office'],
        'vendor': ['vendor', 'supplier', 'payee', 'merchant', 'seller', 'company', 'provider'],
        'purpose': ['purpose', 'description', 'desc', 'category', 'type', 'reason', 'memo', 'notes']
    }
    
    columns_lower = {col: col.lower().replace('_', '').replace(' ', '') for col in df.columns}
    
    for field, field_keywords in keywords.items():
        best_match = None
        best_score = 0
        
        for col, col_clean in columns_lower.items():
            # Calculate match score
            score = 0
            for keyword in field_keywords:
                keyword_clean = keyword.replace('_', '').replace(' ', '')
                if keyword_clean in col_clean:
                    score += len(keyword_clean)
                elif col_clean in keyword_clean:
                    score += len(col_clean)
            
            # Boost score based on data type heuristics
            if field == 'transaction_id' and _is_id_column(df[col]):
                score += 10
            elif field == 'amount' and _is_numeric_column(df[col]):
                score += 10
            elif field == 'date' and _is_date_column(df[col]):
                score += 10
            elif field in ['department', 'vendor', 'purpose'] and _is_categorical_column(df[col]):
                score += 5
            
            if score > best_score:
                best_score = score
                best_match = col
        
        detected[field] = best_match if best_score > 0 else None
    
    return detected


def _is_id_column(series: pd.Series) -> bool:
    """Check if column is likely an ID (unique integers or strings)"""
    try:
        # Check if mostly numeric
        numeric_series = pd.to_numeric(series, errors='coerce')
        if numeric_series.notna().sum() / len(series) > 0.8:
            # Check uniqueness
            return series.nunique() / len(series) > 0.9
    except:
        pass
    return False


def _is_numeric_column(series: pd.Series) -> bool:
    """Check if column contains numeric values (possibly with currency symbols)"""
    # Try to convert to numeric after removing common symbols
    test_series = series.astype(str).str.replace(r'[$,€£¥]', '', regex=True).str.strip()
    numeric_series = pd.to_numeric(test_series, errors='coerce')
    return numeric_series.notna().sum() / len(series) > 0.7


def _is_date_column(series: pd.Series) -> bool:
    """Check if column contains date values"""
    try:
        date_series = pd.to_datetime(series, errors='coerce')
        return date_series.notna().sum() / len(series) > 0.7
    except:
        return False


def _is_categorical_column(series: pd.Series) -> bool:
    """Check if column is categorical (limited unique values, text)"""
    if series.dtype == 'object':
        unique_ratio = series.nunique() / len(series)
        return 0.01 < unique_ratio < 0.5  # Between 1% and 50% unique
    return False


# ==========================================
# CLEAN DATASET
# ==========================================
def clean_dataset(df: pd.DataFrame, column_map: Dict[str, str]) -> pd.DataFrame:
    """
    Clean and standardize dataset based on column mappings.
    
    Fixes:
    - Currency symbols in amount columns
    - Commas in numbers
    - Invalid dates
    - Empty strings to NaN
    - Trims whitespace
    - Standardizes column names
    
    Args:
        df: Raw dataframe
        column_map: Dictionary mapping standard fields to actual column names
                   Example: {'amount': 'Total_Amount', 'date': 'Trans_Date'}
    
    Returns:
        Cleaned dataframe with standardized column names
    """
    df_clean = df.copy()
    
    # Step 1: Rename columns to standard names
    rename_map = {v: k for k, v in column_map.items() if v is not None}
    df_clean = df_clean.rename(columns=rename_map)
    # 🚨 Fix duplicate columns created after renaming
    if df_clean.columns.duplicated().any():
        print("Warning: duplicate columns after schema mapping — keeping first occurrence")
        df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]

    
    # Step 2: Clean each field type
    
    # Transaction ID
    if 'transaction_id' in df_clean.columns:
        df_clean['transaction_id'] = _clean_id_column(df_clean['transaction_id'])
    else:
        # Generate transaction IDs if missing
        df_clean['transaction_id'] = range(len(df_clean))
    
    # Amount
    if 'amount' in df_clean.columns:
        df_clean['amount'] = _clean_amount_column(df_clean['amount'])
    
    # Date
    if 'date' in df_clean.columns:
        df_clean['date'] = _clean_date_column(df_clean['date'])
    
    # Text fields (department, vendor, purpose)
    for field in ['department', 'vendor', 'purpose']:
        if field in df_clean.columns:
            df_clean[field] = _clean_text_column(df_clean[field])
    
    # Step 3: Replace empty strings with NaN globally
    df_clean = df_clean.replace(r'^\s*$', np.nan, regex=True)
    
    # Step 4: Remove leading/trailing whitespace from all object columns
    for col in df_clean.select_dtypes(include=['object']).columns:
        df_clean[col] = df_clean[col].astype(str).str.strip()
        df_clean[col] = df_clean[col].replace('nan', np.nan)
    
    return df_clean


def _clean_id_column(series: pd.Series) -> pd.Series:
    """Clean ID column - ensure integer values"""
    try:
        # Try to convert to numeric
        numeric_series = pd.to_numeric(series, errors='coerce')
        
        # Fill NaN with sequential IDs
        mask = numeric_series.isna()
        if mask.any():
            max_id = numeric_series.max() if numeric_series.notna().any() else 0
            numeric_series[mask] = range(int(max_id) + 1, int(max_id) + 1 + mask.sum())
        
        return numeric_series.astype(int)
    except:
        # If conversion fails, return sequential IDs
        return pd.Series(range(len(series)))


def _clean_amount_column(series: pd.Series) -> pd.Series:
    """
    Clean amount column - remove currency symbols, commas, convert to float
    
    Handles:
    - $1,234.56
    - €1.234,56 (European format)
    - £1,234
    - 1234.56
    """
    cleaned = series.astype(str).copy()
    
    # Remove currency symbols
    cleaned = cleaned.str.replace(r'[$€£¥₹]', '', regex=True)
    
    # Remove whitespace
    cleaned = cleaned.str.strip()
    
    # Detect European format (1.234,56) vs US format (1,234.56)
    # If more periods than commas, likely European
    sample = cleaned.head(100)
    period_count = sample.str.count(r'\.').sum()
    comma_count = sample.str.count(',').sum()
    
    if comma_count > period_count:
        # Likely European format - swap comma and period
        cleaned = cleaned.str.replace('.', '', regex=False)  # Remove thousand separator
        cleaned = cleaned.str.replace(',', '.', regex=False)  # Decimal separator
    else:
        # US format - remove commas
        cleaned = cleaned.str.replace(',', '', regex=False)
    
    # Convert to float
    numeric_series = pd.to_numeric(cleaned, errors='coerce')
    
    # Replace negative values with absolute (assuming amounts are positive)
    numeric_series = numeric_series.abs()
    
    return numeric_series


def _clean_date_column(series: pd.Series) -> pd.Series:
    """
    Clean date column - parse various date formats
    
    Handles:
    - YYYY-MM-DD
    - MM/DD/YYYY
    - DD/MM/YYYY
    - Various other formats
    """
    # Try pandas automatic parsing
    date_series = pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
    
    # If too many NaT values, try alternative formats
    if date_series.isna().sum() / len(date_series) > 0.3:
        # Try common formats explicitly
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%m-%d-%Y',
            '%d.%m.%Y',
            '%Y%m%d'
        ]
        
        for fmt in formats:
            try:
                alt_series = pd.to_datetime(series, format=fmt, errors='coerce')
                if alt_series.notna().sum() > date_series.notna().sum():
                    date_series = alt_series
            except:
                continue
    
    return date_series


def _clean_text_column(series: pd.Series) -> pd.Series:
    """Clean text columns - trim, standardize, handle nulls"""
    cleaned = series.astype(str).copy()
    
    # Trim whitespace
    cleaned = cleaned.str.strip()
    
    # Replace common null representations
    null_values = ['nan', 'null', 'none', 'n/a', 'na', '', 'unknown', '-']
    cleaned = cleaned.replace(null_values, np.nan)
    
    # Standardize case (title case)
    cleaned = cleaned.str.title()
    
    return cleaned


# ==========================================
# COMPUTE HEALTH SCORE
# ==========================================
def compute_health_score(df: pd.DataFrame) -> Dict[str, float]:
    """
    Compute comprehensive data health metrics.
    
    Args:
        df: Dataframe to analyze
    
    Returns:
        Dictionary with health metrics:
        {
            "completeness": 85.5,      # % of non-null values
            "validity": 92.3,          # % of values with correct datatypes
            "duplicates": 15,          # Count of duplicate rows
            "consistency": 88.0,       # % of consistent values (no outliers)
            "overall_score": 87.2      # Weighted average (0-100)
        }
    """
    total_cells = df.size
    total_rows = len(df)
    
    # 1. Completeness Score (% non-null)
    non_null_cells = df.notna().sum().sum()
    completeness = (non_null_cells / total_cells * 100) if total_cells > 0 else 0
    
    # 2. Validity Score (% correct datatypes)
    validity_scores = []
    
    # Check transaction_id
    if 'transaction_id' in df.columns:
        try:
            valid = pd.to_numeric(df['transaction_id'], errors='coerce').notna().sum()
            validity_scores.append(valid / len(df) * 100)
        except:
            validity_scores.append(0)
    
    # Check amount
    if 'amount' in df.columns:
        try:
            valid = pd.to_numeric(df['amount'], errors='coerce').notna().sum()
            validity_scores.append(valid / len(df) * 100)
        except:
            validity_scores.append(0)
    
    # Check date
    if 'date' in df.columns:
        try:
            valid = pd.to_datetime(df['date'], errors='coerce').notna().sum()
            validity_scores.append(valid / len(df) * 100)
        except:
            validity_scores.append(0)
    
    validity = np.mean(validity_scores) if validity_scores else 100
    
    # 3. Duplicate Count
    duplicates = df.duplicated().sum()
    duplicate_score = max(0, 100 - (duplicates / total_rows * 100)) if total_rows > 0 else 100
    
    # 4. Consistency Score (outlier detection for numeric columns)
    consistency_scores = []
    
    if 'amount' in df.columns:
        try:
            amounts = pd.to_numeric(df['amount'], errors='coerce').dropna()
            if len(amounts) > 0:
                z_scores = np.abs(stats.zscore(amounts))
                outliers = (z_scores > 3).sum()
                consistency_scores.append(max(0, 100 - (outliers / len(amounts) * 100)))
        except:
            pass
    
    consistency = np.mean(consistency_scores) if consistency_scores else 100
    
    # 5. Overall Score (weighted average)
    overall_score = (
        completeness * 0.4 +      # 40% weight on completeness
        validity * 0.3 +           # 30% weight on validity
        duplicate_score * 0.15 +   # 15% weight on duplicates
        consistency * 0.15         # 15% weight on consistency
    )
    
    return {
        "completeness": round(completeness, 2),
        "validity": round(validity, 2),
        "duplicates": int(duplicates),
        "consistency": round(consistency, 2),
        "overall_score": round(overall_score, 2)
    }


# ==========================================
# ENRICH FEATURES
# ==========================================
def enrich_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived features for enhanced ML analysis.
    
    Adds:
    - monthly_spend_per_department: Total spending per department per month
    - vendor_transaction_count: Number of transactions per vendor
    - zscore_amount: Z-score of transaction amount (for outlier detection)
    - amount_percentile: Percentile rank of transaction amount
    
    Args:
        df: Cleaned dataframe
    
    Returns:
        Dataframe with additional enriched features
    """
    df_enriched = df.copy()
    
    # Feature 1: Monthly spend per department
    if 'department' in df.columns and 'amount' in df.columns and 'date' in df.columns:
        try:
            # Extract year-month
            df_enriched['year_month'] = pd.to_datetime(df_enriched['date'], errors='coerce').dt.to_period('M')
            
            # Calculate monthly spend per department
            monthly_dept_spend = df_enriched.groupby(['department', 'year_month'])['amount'].transform('sum')
            df_enriched['monthly_spend_per_department'] = monthly_dept_spend
            
            # Drop temporary column
            df_enriched = df_enriched.drop('year_month', axis=1)
        except Exception as e:
            print(f"Warning: Could not compute monthly_spend_per_department: {e}")
            df_enriched['monthly_spend_per_department'] = np.nan
    else:
        df_enriched['monthly_spend_per_department'] = np.nan
    
    # Feature 2: Vendor transaction count
    if 'vendor' in df.columns:
        try:
            vendor_counts = df_enriched.groupby('vendor')['vendor'].transform('count')
            df_enriched['vendor_transaction_count'] = vendor_counts
        except Exception as e:
            print(f"Warning: Could not compute vendor_transaction_count: {e}")
            df_enriched['vendor_transaction_count'] = np.nan
    else:
        df_enriched['vendor_transaction_count'] = np.nan
    
    # Feature 3: Z-score of amount (standardized)
    if 'amount' in df.columns:
        try:
            amounts = pd.to_numeric(df_enriched['amount'], errors='coerce')
            
            # Only compute z-scores for valid amounts
            valid_amounts = amounts.dropna()
            if len(valid_amounts) > 0 and valid_amounts.std() > 0:
                z_scores = (amounts - amounts.mean()) / amounts.std()
                df_enriched['zscore_amount'] = z_scores
            else:
                df_enriched['zscore_amount'] = 0
        except Exception as e:
            print(f"Warning: Could not compute zscore_amount: {e}")
            df_enriched['zscore_amount'] = np.nan
    else:
        df_enriched['zscore_amount'] = np.nan
    
    # Feature 4: Amount percentile
    if 'amount' in df.columns:
        try:
            amounts = pd.to_numeric(df_enriched['amount'], errors='coerce')
            percentiles = amounts.rank(pct=True) * 100
            df_enriched['amount_percentile'] = percentiles
        except Exception as e:
            print(f"Warning: Could not compute amount_percentile: {e}")
            df_enriched['amount_percentile'] = np.nan
    else:
        df_enriched['amount_percentile'] = np.nan
    
    # Feature 5: Transaction day of week (0=Monday, 6=Sunday)
    if 'date' in df.columns:
        try:
            dates = pd.to_datetime(df_enriched['date'], errors='coerce')
            df_enriched['day_of_week'] = dates.dt.dayofweek
            df_enriched['is_weekend'] = (dates.dt.dayofweek >= 5).astype(int)
        except Exception as e:
            print(f"Warning: Could not compute date features: {e}")
            df_enriched['day_of_week'] = np.nan
            df_enriched['is_weekend'] = np.nan
    else:
        df_enriched['day_of_week'] = np.nan
        df_enriched['is_weekend'] = np.nan
    
    return df_enriched


# ==========================================
# COMPLETE PIPELINE
# ==========================================
def run_complete_pipeline(df: pd.DataFrame, column_map: Optional[Dict[str, str]] = None):

    # 🚨 Fix duplicate columns (dirty real-world datasets)
    if df.columns.duplicated().any():
        print("Warning: duplicate columns detected and removed")

    df = df.loc[:, ~df.columns.duplicated()]

    # Step 1: Auto-detect columns if not provided
    if column_map is None:
        column_map = auto_detect_columns(df)

    # Step 2: Clean dataset
    df_clean = clean_dataset(df, column_map)

    # Step 3: Enrich with features
    df_enriched = enrich_features(df_clean)

    # Step 4: Compute health score
    health = compute_health_score(df_enriched)

    return df_enriched, health


# ==========================================
# HELPER: VALIDATE PIPELINE OUTPUT
# ==========================================
def validate_pipeline_output(df: pd.DataFrame) -> Tuple[bool, list]:
    """
    Validate that pipeline output has required fields for ML.
    
    Args:
        df: Pipeline output dataframe
    
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check required columns
    required = ['transaction_id', 'amount']
    for col in required:
        if col not in df.columns:
            issues.append(f"Missing required column: {col}")
        elif df[col].isna().all():
            issues.append(f"Column '{col}' has all null values")
    
    # Check minimum rows
    if len(df) < 10:
        issues.append(f"Dataset too small: {len(df)} rows (minimum 10 required)")
    
    # Check amount validity
    if 'amount' in df.columns:
        valid_amounts = pd.to_numeric(df['amount'], errors='coerce').notna().sum()
        if valid_amounts / len(df) < 0.5:
            issues.append(f"Less than 50% valid amounts ({valid_amounts}/{len(df)})")
    
    is_valid = len(issues) == 0
    return is_valid, issues
