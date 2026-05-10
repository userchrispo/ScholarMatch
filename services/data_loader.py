"""
Data loading and cleaning pipeline for ScholarMatch.
Handles CSV I/O, Pandas-based data cleaning, validation, and deduplication.
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import date, timedelta
from models.scholarship import Scholarship


# ──────────────────────────────────────────────────────────────
# CSV I/O
# ──────────────────────────────────────────────────────────────

def load_raw_data(filepath):
    """Load raw scholarship CSV into a DataFrame."""
    try:
        df = pd.read_csv(filepath, encoding="utf-8")
        return df
    except FileNotFoundError:
        print(f"   [DATA] File not found: {filepath}")
        return None


def cache_to_csv(df, filepath):
    """Save a cleaned DataFrame to CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False, encoding="utf-8")
    print(f"   [DATA] Cached {len(df)} records to: {filepath}")


# ──────────────────────────────────────────────────────────────
# Cleaning pipeline
# ──────────────────────────────────────────────────────────────

def clean_scholarships(df):
    """
    Full Pandas cleaning pipeline for scholarship data.
    
    Handles:
    1. Missing values — fill or drop depending on field criticality
    2. Type mismatches — coerce amounts to float, deadlines to datetime
    3. Duplicate detection — drop exact duplicates, flag near-duplicates
    4. Validation — ensure amount_min <= amount_max, deadlines are future
    
    Returns:
        Cleaned DataFrame and a report dict
    """
    report = {
        "rows_before": len(df),
        "nulls_filled": 0,
        "nulls_dropped": 0,
        "type_fixes": 0,
        "duplicates_removed": 0,
        "validation_fixes": 0,
        "rows_after": 0
    }
    
    print("\n   ╔══════════════════════════════════════════════════╗")
    print("   ║          PANDAS DATA CLEANING REPORT            ║")
    print("   ╚══════════════════════════════════════════════════╝")
    print(f"\n   [CLEAN] Starting with {len(df)} rows")
    
    # ── Step 1: Replace empty strings with NaN ──
    df = df.replace("", np.nan)
    df = df.replace("None", np.nan)
    
    # ── Step 2: Handle missing values ──
    # Critical fields — drop rows where these are missing
    critical_fields = ["name", "provider"]
    before_drop = len(df)
    df = df.dropna(subset=critical_fields)
    rows_dropped = before_drop - len(df)
    report["nulls_dropped"] = rows_dropped
    print(f"   [CLEAN] Dropped {rows_dropped} rows with missing name/provider")
    
    # Non-critical fields — fill with defaults
    fill_count = 0
    
    if df["description"].isna().any():
        count = df["description"].isna().sum()
        df["description"] = df["description"].fillna("No description available.")
        fill_count += count
    
    if df["url"].isna().any():
        count = df["url"].isna().sum()
        df["url"] = df["url"].fillna("https://scholarships.ontario.ca")
        fill_count += count
    
    if df["citizenship_requirement"].isna().any():
        count = df["citizenship_requirement"].isna().sum()
        df["citizenship_requirement"] = df["citizenship_requirement"].fillna("any")
        fill_count += count
    
    if df["eligibility"].isna().any():
        count = df["eligibility"].isna().sum()
        default_elig = json.dumps({"education_level": ["university", "college"], "provinces": ["ontario"]})
        df["eligibility"] = df["eligibility"].fillna(default_elig)
        fill_count += count
    
    if df["field_of_studys"].isna().any():
        count = df["field_of_studys"].isna().sum()
        df["field_of_studys"] = df["field_of_studys"].fillna("[]")
        fill_count += count
    
    report["nulls_filled"] = fill_count
    print(f"   [CLEAN] Filled {fill_count} missing values with defaults")
    
    # ── Step 3: Fix type mismatches ──
    type_fixes = 0
    
    # Coerce amounts to numeric
    df["amount_min"] = pd.to_numeric(df["amount_min"], errors="coerce")
    df["amount_max"] = pd.to_numeric(df["amount_max"], errors="coerce")
    
    # Count how many were coerced (became NaN)
    amount_nans = df["amount_min"].isna().sum() + df["amount_max"].isna().sum()
    
    # Fill NaN amounts with median of valid values
    if df["amount_min"].isna().any():
        median_min = df["amount_min"].median()
        count = df["amount_min"].isna().sum()
        df["amount_min"] = df["amount_min"].fillna(median_min)
        type_fixes += count
    
    if df["amount_max"].isna().any():
        median_max = df["amount_max"].median()
        count = df["amount_max"].isna().sum()
        df["amount_max"] = df["amount_max"].fillna(median_max)
        type_fixes += count
    
    # Coerce deadline to datetime
    df["deadline"] = pd.to_datetime(df["deadline"], errors="coerce")
    
    # Fill missing deadlines with 6 months from now
    if df["deadline"].isna().any():
        count = df["deadline"].isna().sum()
        default_deadline = pd.Timestamp(date.today() + timedelta(days=180))
        df["deadline"] = df["deadline"].fillna(default_deadline)
        type_fixes += count
    
    # Ensure ID is integer
    df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    
    report["type_fixes"] = type_fixes
    print(f"   [CLEAN] Fixed {type_fixes} type mismatches (coerced to numeric/datetime)")
    
    # ── Step 4: Remove duplicates ──
    before_dedup = len(df)
    
    # Exact duplicates
    df = df.drop_duplicates()
    exact_dups = before_dedup - len(df)
    
    # Near-duplicates: same name + provider
    before_near = len(df)
    df = df.drop_duplicates(subset=["name", "provider"], keep="first")
    near_dups = before_near - len(df)
    
    report["duplicates_removed"] = exact_dups + near_dups
    print(f"   [CLEAN] Removed {exact_dups} exact duplicates")
    print(f"   [CLEAN] Removed {near_dups} near-duplicates (same name + provider)")
    
    # ── Step 5: Validation fixes ──
    validation_fixes = 0
    
    # Ensure amount_min <= amount_max
    swapped = df["amount_min"] > df["amount_max"]
    if swapped.any():
        count = swapped.sum()
        df.loc[swapped, ["amount_min", "amount_max"]] = df.loc[swapped, ["amount_max", "amount_min"]].values
        validation_fixes += count
        print(f"   [CLEAN] Swapped {count} rows where amount_min > amount_max")
    
    # Remove rows with past deadlines
    today = pd.Timestamp(date.today())
    past_deadlines = df["deadline"] < today
    if past_deadlines.any():
        count = past_deadlines.sum()
        df = df[~past_deadlines]
        validation_fixes += count
        print(f"   [CLEAN] Removed {count} rows with past deadlines")
    
    # Ensure amounts are positive
    non_positive = (df["amount_min"] <= 0) | (df["amount_max"] <= 0)
    if non_positive.any():
        count = non_positive.sum()
        df = df[~non_positive]
        validation_fixes += count
        print(f"   [CLEAN] Removed {count} rows with non-positive amounts")
    
    # Reassign clean sequential IDs
    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    
    report["validation_fixes"] = validation_fixes
    report["rows_after"] = len(df)
    
    # ── Summary ──
    print(f"\n   ┌─────────────────────────────────────────────────┐")
    print(f"   │  Rows before:          {report['rows_before']:>6}                  │")
    print(f"   │  Nulls filled:         {report['nulls_filled']:>6}                  │")
    print(f"   │  Rows dropped (nulls): {report['nulls_dropped']:>6}                  │")
    print(f"   │  Type fixes:           {report['type_fixes']:>6}                  │")
    print(f"   │  Duplicates removed:   {report['duplicates_removed']:>6}                  │")
    print(f"   │  Validation fixes:     {report['validation_fixes']:>6}                  │")
    print(f"   │  Rows after:           {report['rows_after']:>6}                  │")
    print(f"   └─────────────────────────────────────────────────┘")
    
    return df, report


# ──────────────────────────────────────────────────────────────
# High-level data access
# ──────────────────────────────────────────────────────────────

def get_clean_dataframe(raw_path, cache_path=None):
    """
    Load raw data, clean it, optionally cache the result.
    
    Args:
        raw_path: Path to raw CSV
        cache_path: Optional path to save cleaned CSV
    
    Returns:
        Cleaned DataFrame
    """
    df = load_raw_data(raw_path)
    if df is None:
        return None
    
    df, report = clean_scholarships(df)
    
    if cache_path:
        cache_to_csv(df, cache_path)
    
    return df


def load_from_cache(filepath):
    """Load cleaned data from cache CSV."""
    try:
        df = pd.read_csv(filepath, parse_dates=["deadline"])
        return df
    except FileNotFoundError:
        print("   [DATA] Cache not found")
        return None


def convert_to_scholarships(df):
    """Convert a DataFrame to a list of Scholarship objects."""
    scholarships = []
    for _, row in df.iterrows():
        try:
            # Parse eligibility and fields from JSON strings
            eligibility = row["eligibility"]
            if isinstance(eligibility, str):
                eligibility = json.loads(eligibility)
            
            fields = row["field_of_studys"]
            if isinstance(fields, str):
                fields = json.loads(fields)
            
            # Convert deadline
            deadline = row["deadline"]
            if isinstance(deadline, pd.Timestamp):
                deadline = deadline.date()
            elif isinstance(deadline, str):
                deadline = pd.to_datetime(deadline).date()
            
            scholarship = Scholarship(
                id=int(row["id"]),
                name=row["name"],
                provider=row["provider"],
                amount_min=float(row["amount_min"]),
                amount_max=float(row["amount_max"]),
                deadline=deadline,
                eligibility=eligibility,
                field_of_studys=fields,
                url=row["url"],
                description=row["description"],
                citizenship_requirement=row.get("citizenship_requirement", "any")
            )
            scholarships.append(scholarship)
        except (ValueError, KeyError) as e:
            # Skip scholarships that fail validation (e.g., past deadline after clock drift)
            continue
    
    return scholarships