"""
Data cleaning and validation operations for processed bee data.

This module handles:
- Removing duplicate State-Date combinations
- Fixing logical inconsistencies
- Data quality checks
"""

import pandas as pd


def remove_duplicates(df: pd.DataFrame, subset: list, keep: str = "last") -> tuple[pd.DataFrame, int]:
    """
    Remove duplicate rows based on specified columns.
    
    Args:
        df: DataFrame to deduplicate
        subset: List of column names to identify duplicates
        keep: Which duplicate to keep ('first', 'last', or False)
        
    Returns:
        Tuple of (cleaned_df, num_removed)
    """
    before_count = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep=keep)
    removed_count = before_count - len(df_clean)
    
    return df_clean, removed_count


def clean_bee_data(varroa_df: pd.DataFrame, colonies_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Apply all cleaning operations to varroa and colonies dataframes.
    
    Multiple releases contain overlapping historical data, so we remove
    duplicates keeping the most recent release (which may have corrections).
    
    Args:
        varroa_df: Raw varroa dataframe
        colonies_df: Raw colonies dataframe
        
    Returns:
        Tuple of (cleaned_varroa_df, cleaned_colonies_df)
    """
    print("Removing duplicate State-Date combinations...")
    
    # Remove duplicates (keep last = most recent release)
    varroa_clean, varroa_removed = remove_duplicates(
        varroa_df, 
        subset=["State", "date"], 
        keep="last"
    )
    
    colonies_clean, colonies_removed = remove_duplicates(
        colonies_df,
        subset=["State", "date"],
        keep="last"
    )
    
    if varroa_removed > 0:
        print(f"  Removed {varroa_removed} duplicate varroa rows ({varroa_removed/len(varroa_df)*100:.1f}%)")
    if colonies_removed > 0:
        print(f"  Removed {colonies_removed} duplicate colonies rows ({colonies_removed/len(colonies_df)*100:.1f}%)")
    
    return varroa_clean, colonies_clean
