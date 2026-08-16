"""
CSV validation and normalization for baby and adult food items.
"""
import pandas as pd
from typing import Tuple, Optional, Dict, List


BABY_REQUIRED_HEADERS = ["food_id", "food_item", "texture_stage", "safe_preparation", "allergen"]
ADULT_REQUIRED_HEADERS = ["food_item", "allergen", "measurable_quantity"]


def validate_baby_csv(df: pd.DataFrame) -> Tuple[bool, str, pd.DataFrame]:
    """
    Validate and normalize baby food CSV.
    
    Returns: (is_valid, error_message, cleaned_df)
    """
    # Check for empty file
    if df.empty:
        return False, "CSV file is empty.", df
    
    # Normalize headers: lowercase, strip whitespace
    df.columns = df.columns.str.lower().str.strip()
    
    # Check for required headers
    missing_headers = [h for h in BABY_REQUIRED_HEADERS if h not in df.columns]
    if missing_headers:
        return False, f"Missing required headers: {', '.join(missing_headers)}", df
    
    # Select only required columns
    df = df[BABY_REQUIRED_HEADERS].copy()
    
    # Check for duplicate headers
    if len(df.columns) != len(set(df.columns)):
        return False, "Duplicate column headers found.", df
    
    # Check for blank required fields
    for col in BABY_REQUIRED_HEADERS:
        if df[col].isna().any() or df[col].astype(str).str.strip().eq("").any():
            return False, f"Column '{col}' contains blank values.", df
    
    # Trim whitespace from text fields
    for col in BABY_REQUIRED_HEADERS:
        df[col] = df[col].astype(str).str.strip()
    
    # Check for duplicate food_ids
    duplicates = df[df.duplicated(subset=["food_id"], keep=False)]
    if not duplicates.empty:
        dup_ids = duplicates["food_id"].unique()
        return False, f"Duplicate food_id values found: {', '.join(dup_ids)}", df
    
    # Normalize blank allergens to 'no'
    df.loc[df["allergen"].str.lower().isin(["", "nan", "none"]), "allergen"] = "no"
    
    return True, "", df


def validate_adult_csv(df: pd.DataFrame) -> Tuple[bool, str, pd.DataFrame]:
    """
    Validate and normalize adult food CSV.
    
    Returns: (is_valid, error_message, cleaned_df)
    """
    # Check for empty file
    if df.empty:
        return False, "CSV file is empty.", df
    
    # Normalize headers: lowercase, strip whitespace
    df.columns = df.columns.str.lower().str.strip()
    
    # Check for required headers
    missing_headers = [h for h in ADULT_REQUIRED_HEADERS if h not in df.columns]
    if missing_headers:
        return False, f"Missing required headers: {', '.join(missing_headers)}", df
    
    # Select only required columns
    df = df[ADULT_REQUIRED_HEADERS].copy()
    
    # Check for duplicate headers
    if len(df.columns) != len(set(df.columns)):
        return False, "Duplicate column headers found.", df
    
    # Check for blank required fields
    for col in ADULT_REQUIRED_HEADERS:
        if df[col].isna().any() or df[col].astype(str).str.strip().eq("").any():
            return False, f"Column '{col}' contains blank values.", df
    
    # Trim whitespace from text fields
    for col in ADULT_REQUIRED_HEADERS:
        df[col] = df[col].astype(str).str.strip()
    
    # Normalize blank allergens to 'none'
    df.loc[df["allergen"].str.lower().isin(["", "nan", "no"]), "allergen"] = "none"
    
    return True, "", df


def load_default_csvs() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load default baby and adult CSVs from data/ folder.
    
    Returns: (baby_df, adult_df)
    """
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    baby_path = os.path.join(base_dir, "data", "baby_food_items_under_12_months.csv")
    adult_path = os.path.join(base_dir, "data", "adult_food_items.csv")
    
    baby_df = pd.read_csv(baby_path)
    adult_df = pd.read_csv(adult_path)
    
    # Validate and normalize defaults
    _, _, baby_df = validate_baby_csv(baby_df)
    _, _, adult_df = validate_adult_csv(adult_df)
    
    return baby_df, adult_df


def load_and_validate_csv(file_path: str, csv_type: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """
    Load and validate a CSV file.
    
    Args:
        file_path: Path to CSV file
        csv_type: "baby" or "adult"
    
    Returns: (is_valid, error_message, dataframe)
    """
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return False, f"Failed to read CSV: {str(e)}", None
    
    if csv_type == "baby":
        return validate_baby_csv(df)
    elif csv_type == "adult":
        return validate_adult_csv(df)
    else:
        return False, f"Unknown CSV type: {csv_type}", None
