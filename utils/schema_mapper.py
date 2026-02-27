"""
Schema Mapper & Dataset Validation Module
Handles column detection, fuzzy matching, and data standardization
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher


# ==========================================
# STANDARD SCHEMA DEFINITION
# ==========================================
STANDARD_SCHEMA = {
    'transaction_id': {
        'required': True,
        'aliases': ['id', 'txn_id', 'trans_id', 'transaction_number', 'receipt_id', 
                   'order_id', 'reference', 'ref_no', 'transaction no', 'txn no'],
        'dtype': 'int64'
    },
    'amount': {
        'required': True,
        'aliases': ['amt', 'transaction_amount', 'value', 'price', 'total', 'cost',
                   'payment', 'sum', 'transaction_value', 'net_amount', 'gross_amount'],
        'dtype': 'float64'
    },
    'date': {
        'required': True,
        'aliases': ['transaction_date', 'txn_date', 'trans_date', 'created_date',
                   'timestamp', 'datetime', 'created_at', 'posted_date', 'effective_date'],
        'dtype': 'datetime64'
    },
    'department': {
        'required': False,
        'aliases': ['dept', 'department_name', 'division', 'unit', 'section',
                   'cost_center', 'business_unit', 'team', 'office'],
        'dtype': 'object'
    },
    'vendor': {
        'required': False,
        'aliases': ['vendor_name', 'supplier', 'payee', 'merchant', 'seller',
                   'provider', 'contractor', 'company', 'entity_name'],
        'dtype': 'object'
    },
    'purpose': {
        'required': False,
        'aliases': ['description', 'desc', 'notes', 'memo', 'category', 'type',
                   'reason', 'expense_type', 'transaction_type', 'narrative'],
        'dtype': 'object'
    }
}


# ==========================================
# FUZZY MATCHING UTILITIES
# ==========================================
def fuzzy_match(text1: str, text2: str, threshold: float = 0.75) -> float:
    """
    Calculate similarity ratio between two strings
    
    Args:
        text1: First string
        text2: Second string
        threshold: Minimum similarity threshold
    
    Returns:
        Similarity ratio (0 to 1)
    """
    text1_clean = text1.lower().strip().replace('_', ' ').replace('-', ' ')
    text2_clean = text2.lower().strip().replace('_', ' ').replace('-', ' ')
    
    return SequenceMatcher(None, text1_clean, text2_clean).ratio()


def find_best_match(column_name: str, candidates: List[str], threshold: float = 0.75) -> Optional[str]:
    """
    Find best matching candidate for a column name
    
    Args:
        column_name: Column to match
        candidates: List of candidate column names
        threshold: Minimum similarity threshold
    
    Returns:
        Best matching candidate or None
    """
    best_match = None
    best_score = 0
    
    for candidate in candidates:
        score = fuzzy_match(column_name, candidate)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = candidate
    
    return best_match


# ==========================================
# COLUMN DETECTION
# ==========================================
def detect_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """
    Auto-detect which columns map to standard schema fields
    
    Args:
        df: Input dataframe
    
    Returns:
        Dictionary mapping standard fields to detected columns
        Example: {'transaction_id': 'ID', 'amount': 'Amount', ...}
    """
    detected_mapping = {}
    available_columns = df.columns.tolist()
    used_columns = set()
    
    for standard_field, config in STANDARD_SCHEMA.items():
        detected_col = None
        
        # First: Check for exact match (case-insensitive)
        for col in available_columns:
            if col.lower() == standard_field.lower() and col not in used_columns:
                detected_col = col
                used_columns.add(col)
                break
        
        # Second: Check aliases (exact match)
        if detected_col is None:
            for alias in config['aliases']:
                for col in available_columns:
                    if col.lower() == alias.lower() and col not in used_columns:
                        detected_col = col
                        used_columns.add(col)
                        break
                if detected_col:
                    break
        
        # Third: Fuzzy matching
        if detected_col is None:
            all_candidates = [standard_field] + config['aliases']
            for col in available_columns:
                if col not in used_columns:
                    best_match = find_best_match(col, all_candidates, threshold=0.75)
                    if best_match:
                        detected_col = col
                        used_columns.add(col)
                        break
        
        detected_mapping[standard_field] = detected_col
    
    return detected_mapping


# ==========================================
# SCHEMA MAPPING & STANDARDIZATION
# ==========================================
def map_to_standard_schema(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Map dataframe columns to standard schema
    
    Args:
        df: Input dataframe
        mapping: Dictionary mapping standard fields to actual column names
                 Example: {'transaction_id': 'ID', 'amount': 'TotalAmount'}
    
    Returns:
        Standardized dataframe with renamed columns
    """
    # Create a copy to avoid modifying original
    df_standardized = df.copy()
    
    # Build rename mapping (only for non-None mappings)
    rename_map = {}
    for standard_field, actual_col in mapping.items():
        if actual_col and actual_col in df.columns:
            rename_map[actual_col] = standard_field
    
    # Rename columns
    df_standardized = df_standardized.rename(columns=rename_map)
    
    # Add missing optional fields as null columns
    for standard_field, config in STANDARD_SCHEMA.items():
        if standard_field not in df_standardized.columns and not config['required']:
            df_standardized[standard_field] = None
    
    # Type conversion with error handling
    df_standardized = convert_data_types(df_standardized)
    
    return df_standardized


def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert columns to expected data types with graceful error handling
    
    Args:
        df: Dataframe to convert
    
    Returns:
        Dataframe with converted types
    """
    df_converted = df.copy()
    
    for standard_field, config in STANDARD_SCHEMA.items():
        if standard_field in df_converted.columns:
            target_dtype = config['dtype']
            
            try:
                if target_dtype == 'int64':
                    # Handle transaction_id - coerce to int, create index if needed
                    if df_converted[standard_field].isnull().all():
                        df_converted[standard_field] = range(len(df_converted))
                    else:
                        df_converted[standard_field] = pd.to_numeric(
                            df_converted[standard_field], errors='coerce'
                        ).fillna(range(len(df_converted))).astype(int)
                
                elif target_dtype == 'float64':
                    # Handle amount - remove currency symbols and convert
                    if df_converted[standard_field].dtype == 'object':
                        # Remove common currency symbols
                        df_converted[standard_field] = df_converted[standard_field].astype(str).str.replace(
                            r'[$,€£¥]', '', regex=True
                        ).str.strip()
                    df_converted[standard_field] = pd.to_numeric(
                        df_converted[standard_field], errors='coerce'
                    )
                
                elif target_dtype == 'datetime64':
                    # Handle dates - try multiple formats
                    df_converted[standard_field] = pd.to_datetime(
                        df_converted[standard_field], errors='coerce', infer_datetime_format=True
                    )
                
                elif target_dtype == 'object':
                    # Convert to string
                    df_converted[standard_field] = df_converted[standard_field].astype(str)
            
            except Exception as e:
                # If conversion fails, leave as-is
                print(f"Warning: Could not convert {standard_field} to {target_dtype}: {e}")
    
    return df_converted


# ==========================================
# VALIDATION
# ==========================================
def validate_required_fields(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate that all required fields are present and have data
    
    Args:
        df: Standardized dataframe to validate
    
    Returns:
        Tuple of (is_valid, list_of_missing_fields)
    """
    missing_fields = []
    
    for standard_field, config in STANDARD_SCHEMA.items():
        if config['required']:
            # Check if column exists
            if standard_field not in df.columns:
                missing_fields.append(f"{standard_field} (column missing)")
            # Check if column has any non-null values
            elif df[standard_field].isnull().all():
                missing_fields.append(f"{standard_field} (all values null)")
    
    is_valid = len(missing_fields) == 0
    return is_valid, missing_fields


def get_data_health_summary(df: pd.DataFrame) -> Dict:
    """
    Generate comprehensive data health summary
    
    Args:
        df: Dataframe to analyze
    
    Returns:
        Dictionary with health metrics
    """
    summary = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'duplicate_rows': df.duplicated().sum(),
        'missing_values': {},
        'data_types': {},
        'value_ranges': {},
        'issues': []
    }
    
    # Missing values per column
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        missing_pct = (missing_count / len(df) * 100) if len(df) > 0 else 0
        
        summary['missing_values'][col] = {
            'count': int(missing_count),
            'percentage': round(missing_pct, 2)
        }
        
        # Flag high missing rate
        if missing_pct > 50:
            summary['issues'].append(f"{col} has {missing_pct:.1f}% missing values")
    
    # Data types
    for col in df.columns:
        summary['data_types'][col] = str(df[col].dtype)
    
    # Value ranges for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col in df.columns:
            summary['value_ranges'][col] = {
                'min': float(df[col].min()) if not df[col].isnull().all() else None,
                'max': float(df[col].max()) if not df[col].isnull().all() else None,
                'mean': float(df[col].mean()) if not df[col].isnull().all() else None
            }
    
    # Duplicate check
    if summary['duplicate_rows'] > 0:
        dup_pct = (summary['duplicate_rows'] / summary['total_rows'] * 100)
        summary['issues'].append(f"Found {summary['duplicate_rows']} duplicate rows ({dup_pct:.1f}%)")
    
    return summary


# ==========================================
# USER-FRIENDLY HELPERS
# ==========================================
def get_available_columns(df: pd.DataFrame) -> List[str]:
    """Get list of available columns with 'None' option"""
    return ['None'] + df.columns.tolist()


def get_mapping_suggestions(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Get top 3 suggestions for each standard field
    
    Args:
        df: Input dataframe
    
    Returns:
        Dictionary with suggestions for each standard field
    """
    suggestions = {}
    
    for standard_field, config in STANDARD_SCHEMA.items():
        field_suggestions = []
        all_candidates = [standard_field] + config['aliases']
        
        # Calculate scores for all columns
        scores = []
        for col in df.columns:
            best_score = 0
            for candidate in all_candidates:
                score = fuzzy_match(col, candidate)
                if score > best_score:
                    best_score = score
            scores.append((col, best_score))
        
        # Get top 3
        top_3 = sorted(scores, key=lambda x: x[1], reverse=True)[:3]
        field_suggestions = [col for col, score in top_3 if score >= 0.5]
        
        suggestions[standard_field] = field_suggestions
    
    return suggestions


def validate_dataset_integrity(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Comprehensive dataset integrity check
    
    Args:
        df: Dataframe to validate
    
    Returns:
        Tuple of (is_valid, list_of_warnings)
    """
    warnings = []
    
    # Check 1: Empty dataframe
    if len(df) == 0:
        warnings.append("⚠️ Dataset is empty")
        return False, warnings
    
    # Check 2: Too few rows
    if len(df) < 10:
        warnings.append(f"⚠️ Only {len(df)} rows - minimum 10 recommended for ML analysis")
    
    # Check 3: All columns are object type (possible parsing issue)
    if all(df[col].dtype == 'object' for col in df.columns):
        warnings.append("⚠️ All columns detected as text - check if data was parsed correctly")
    
    # Check 4: Duplicate column names
    if len(df.columns) != len(set(df.columns)):
        warnings.append("⚠️ Duplicate column names detected")
    
    # Check 5: All values in a column are identical
    for col in df.columns:
        if df[col].nunique() == 1:
            warnings.append(f"⚠️ Column '{col}' has only one unique value")
    
    is_valid = len([w for w in warnings if w.startswith("⚠️ Dataset is empty")]) == 0
    
    return is_valid, warnings
