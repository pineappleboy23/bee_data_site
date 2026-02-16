"""
Process USDA bee colony data from CSV files.

Based on the working Google Colab notebook processing workflow.
Data source: https://usda.library.cornell.edu/concern/publications/rn301137d

USDA CSV files contain multiple tables with different shapes in one file:
- Colony count tables (colonies, max, lost, percent, added, renovated)
- Varroa/stressor tables (varroa mites, parasites, diseases, pesticides, other, unknown)

This processor classifies each table and builds two separate output files.
"""

import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
from datetime import datetime
import json
import re

# Import cleaning operations
from clean_data import clean_bee_data


# Column definitions for output DataFrames# Column definitions for classification
VARROA_KEYWORDS = ['State', 'Varroa', 'parasites', "Diseases", "Pesticides", "Other", "Unknown"]
COLONIES_KEYWORDS = ['State', 'max', 'Lost', "Percent", "Added", "Renovated"]

# Standard column names for output
VARROA_COLUMNS = ["table", 'State', 'Varroa_mites', 'Other_pests_and_parasites', 
                  "Diseases", "Pesticides", "Other", "Unknown", "date"]
COLONIES_COLUMNS = ["table", 'State', 'Starting_Colonies', "Max_Colonies", 'Lost_colonies', 
                    "Percent_lost", "Added_colonies", "Renovated_colonies", "Percent_renovated", "date"]

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def load_csv_files(directory):
    """
    Load all CSV files from directory and subdirectories (recursive) with encoding detection.
    Returns dict of {file_path: dataframe}
    
    Uses fixed column approach to handle variable USDA CSV formats.
    """
    dataframes = {}
    file_paths = glob.glob(os.path.join(directory, '**', '*.csv'), recursive=True)
    
    if not file_paths:
        print(f"⚠ No CSV files found in {directory}")
        return dataframes
    
    encodings_to_try = ['windows-1252', 'utf-8', 'latin-1', 'iso-8859-1']
    
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        
        # Skip .gitkeep and hidden files
        if file_name.startswith('.'):
            continue
        
        for encoding in encodings_to_try:
            try:
                # Read with fixed 20 columns - USDA files have varying column counts
                columns = [f'Col_{i}' for i in range(20)]
                df = pd.read_csv(file_path, encoding=encoding, names=columns, header=None, 
                                on_bad_lines='skip')
                dataframes[file_path] = df
                print(f"✓ Loaded: {file_name} ({len(df)} rows, {len(df.columns)} cols, {encoding})")
                break
            except (UnicodeDecodeError, Exception) as e:
                if encoding == encodings_to_try[-1]:
                    print(f"✗ Could not load {file_name}: {e}")
                continue
    
    return dataframes


def data_rows_count(df):
    """Count rows where the second column (Col_1) equals 'd' (data rows)"""
    if len(df.columns) < 2:
        return 0
    return sum(1 for _, row in df.iterrows() if row['Col_1'] == 'd')


def filter_df_by_second_column(df, value):
    """Filter DataFrame to include only rows where second column (Col_1) matches value"""
    if 'Col_1' not in df.columns:
        return pd.DataFrame()
    return df[df['Col_1'] == value].copy()


def check_strings_in_df(df, strings):
    """Check if all strings from list are present somewhere in the DataFrame"""
    flat_set = set(str(cell).lower() for row in df.itertuples(index=False) 
                   for cell in row if isinstance(cell, str))
    strings = [s.lower() for s in strings]
    return all(any(s in cell for cell in flat_set) for s in strings)


def classify_dataframe(df):
    """
    Classifies a DataFrame based on keywords:
    Returns: 'v' (varroa), 'c' (colonies), or 'o' (other)
    """
    if check_strings_in_df(df, VARROA_KEYWORDS):
        return 'v'
    elif check_strings_in_df(df, COLONIES_KEYWORDS):
        return 'c'
    else:
        return 'o'


def get_first_month(df):
    """Finds the first month mentioned in header rows (Col_1 is 'h')"""
    if 'Col_1' not in df.columns:
        return None
    
    for index, row in df.iterrows():
        if row['Col_1'] == "h":
            for cell in row:
                if isinstance(cell, str):
                    for month in MONTHS:
                        if month in cell:
                            return month
    
    # Check second row as fallback for varroa dfs
    if len(df) > 1:
        for cell in df.iloc[1]:
            if isinstance(cell, str):
                for month in MONTHS:
                    if month in cell:
                        return month
    
    return None


def find_earliest_year(df):
    """Search through DataFrame to find the earliest year (YYYY format)"""
    year_regex = re.compile(r"\b(\d{4})\b")
    earliest_year = None
    
    if 'Col_1' not in df.columns:
        return None
    
    for index, row in df.iterrows():
        # Skip data and footer rows
        if row['Col_1'] in ['d', 'f']:
            continue
        
        for cell in row:
            if isinstance(cell, str):
                found_years = year_regex.findall(cell)
                found_years = [int(year) for year in found_years 
                              if 1000 < int(year) <= 9999]
                
                if found_years:
                    min_year = min(found_years)
                    if earliest_year is None or min_year < earliest_year:
                        earliest_year = min_year
    
    return earliest_year


def convert_month_year_to_date(month, year):
    """Converts month name and year to datetime object"""
    if isinstance(month, str):
        month = datetime.strptime(month, "%B").month
    
    date_str = f"{year}-{month:02d}"
    return pd.to_datetime(date_str, format="%Y-%m")


def process_dataframe(df, date_object, classification):
    """
    Process DataFrame:
    1. Drop second column (type marker Col_1)
    2. Remove rows with 3 or fewer non-null values
    3. Remove trailing empty columns
    4. Rename columns based on classification
    5. Add Date column
    """
    # Drop the Col_1 column (type marker)
    if 'Col_1' in df.columns:
        df = df.drop('Col_1', axis=1).copy()
    
    # Remove rows with 3 or fewer non-null values
    df = df[df.apply(lambda row: row.notnull().sum() > 3, axis=1)]
    
    # Drop trailing empty columns
    while not df.empty and df.iloc[:, -1].isnull().all():
        df = df.iloc[:, :-1]
    
    # Rename columns based on classification
    if classification == 'v':
        # Varroa/stressor data
        num_cols = min(len(df.columns), len(VARROA_COLUMNS) - 1)
        df.columns = VARROA_COLUMNS[:num_cols]
    elif classification == 'c':
        # Colony count data
        num_cols = min(len(df.columns), len(COLONIES_COLUMNS) - 1)
        df.columns = COLONIES_COLUMNS[:num_cols]
    
    # Add date column
    df['date'] = date_object
    
    return df


def apply_special_value_replacements(df):
    """Replace USDA special notation with standard values"""
    replacements = {
        "(Z)": 0.25,
        "(X)": np.nan,
        "(NA)": np.nan,
        "-": 0
    }
    return df.replace(replacements)


def convert_specific_columns(df, exclude_columns):
    """Convert all columns except specified ones to numeric"""
    columns_to_convert = df.columns.difference(exclude_columns)
    for col in columns_to_convert:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def process_usda_data(raw_data_dir, output_dir):
    """
    Main processing function following the Colab workflow.
    
    Creates two separate output files:
    - colonies_df.csv: Colony count data (colonies, max, lost, added, renovated)
    - varroa_df.csv: Stressor data (varroa, parasites, diseases, pesticides, other, unknown)
    """
    print("=" * 60)
    print("USDA BEE DATA PROCESSING (Classification-Based)")
    print("=" * 60)
    print()
    
    # Load all CSV files
    print(f"Loading CSV files from: {raw_data_dir}")
    dataframes = load_csv_files(raw_data_dir)
    
    if not dataframes:
        print("✗ No CSV files found!")
        return None
    
    print(f"\n✓ Loaded {len(dataframes)} file(s)")
    print()
    
    # Filter dataframes by data row count (35-70 rows typical for state-level data)
    print("Filtering dataframes by row count...")
    filtered_dataframes = []
    
    for file_path, df in dataframes.items():
        data_rows = data_rows_count(df)
        if 35 <= data_rows <= 70:
            filtered_dataframes.append((file_path, df))
            file_name = os.path.basename(file_path)
            classification = classify_dataframe(df)
            print(f"  ✓ {file_name}: {data_rows} data rows, classification: {classification}")
    
    print(f"\n✓ Filtered to {len(filtered_dataframes)} usable files")
    print()
    
    # Initialize output dataframes
    varroa_df = pd.DataFrame(columns=VARROA_COLUMNS)
    colonies_df = pd.DataFrame(columns=COLONIES_COLUMNS)
    
    skipped_count = 0
    processed_varroa = 0
    processed_colonies = 0
    
    # Process each filtered dataframe
    print("Processing dataframes...")
    for file_path, df in filtered_dataframes:
        file_name = os.path.basename(file_path)
        
        # Extract date information
        month = get_first_month(df)
        year = find_earliest_year(df)
        classification = classify_dataframe(df)
        
        # Skip if missing date or classification is 'other'
        if year is None or month is None or classification == 'o':
            skipped_count += 1
            continue
        
        try:
            # Create datetime object
            datetime_obj = convert_month_year_to_date(month, year)
            
            # Filter to only data rows ('d')
            data_only = filter_df_by_second_column(df, 'd')
            
            if data_only.empty:
                skipped_count += 1
                continue
            
            # Process the data
            processed = process_dataframe(data_only, datetime_obj, classification)
            
            # Append to appropriate output dataframe
            if classification == 'v':
                varroa_df = pd.concat([varroa_df, processed], ignore_index=True, axis=0)
                processed_varroa += 1
                print(f"  ✓ {file_name} → varroa_df ({month} {year})")
            elif classification == 'c':
                colonies_df = pd.concat([colonies_df, processed], ignore_index=True, axis=0)
                processed_colonies += 1
                print(f"  ✓ {file_name} → colonies_df ({month} {year})")
        
        except Exception as e:
            print(f"  ✗ {file_name}: {e}")
            skipped_count += 1
    
    print()
    print(f"Processed: {processed_colonies} colony files, {processed_varroa} varroa files")
    print(f"Skipped: {skipped_count} files")
    print()
    
    # Apply special value replacements
    print("Applying special value replacements...")
    varroa_df = apply_special_value_replacements(varroa_df)
    colonies_df = apply_special_value_replacements(colonies_df)
    
    # Convert to numeric (excluding State and date)
    print("Converting to numeric types...")
    varroa_df = convert_specific_columns(varroa_df, ["State", "date"])
    colonies_df = convert_specific_columns(colonies_df, ["State", "date"])
    
    # Clean data (remove duplicates, fix inconsistencies)
    varroa_df, colonies_df = clean_bee_data(varroa_df, colonies_df)
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Varroa DataFrame: {varroa_df.shape[0]} rows, {varroa_df.shape[1]} columns")
    print(f"Colonies DataFrame: {colonies_df.shape[0]} rows, {colonies_df.shape[1]} columns")
    
    # Save output files
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Save varroa data
        varroa_csv = output_dir / "varroa_df.csv"
        varroa_df.to_csv(varroa_csv, index=False)
        print(f"\n✓ Saved: {varroa_csv}")
        
        # Save colonies data
        colonies_csv = output_dir / "colonies_df.csv"
        colonies_df.to_csv(colonies_csv, index=False)
        print(f"✓ Saved: {colonies_csv}")
        
        # Also save combined for backwards compatibility
        if not colonies_df.empty:
            # Use colonies_df as the primary output
            bee_data_csv = output_dir / "bee_data.csv"
            colonies_df.to_csv(bee_data_csv, index=False)
            print(f"✓ Saved: {bee_data_csv} (primary output)")
        
        # Generate summaries
        summary = {
            "varroa_data": {
                "total_rows": len(varroa_df),
                "total_columns": len(varroa_df.columns),
                "columns": list(varroa_df.columns),
                "date_range": {
                    "earliest": str(varroa_df['date'].min()) if not varroa_df.empty else None,
                    "latest": str(varroa_df['date'].max()) if not varroa_df.empty else None
                },
                "states": sorted(varroa_df['State'].unique().tolist()) if not varroa_df.empty else []
            },
            "colonies_data": {
                "total_rows": len(colonies_df),
                "total_columns": len(colonies_df.columns),
                "columns": list(colonies_df.columns),
                "date_range": {
                    "earliest": str(colonies_df['date'].min()) if not colonies_df.empty else None,
                    "latest": str(colonies_df['date'].max()) if not colonies_df.empty else None
                },
                "states": sorted(colonies_df['State'].unique().tolist()) if not colonies_df.empty else []
            }
        }
        
        summary_file = output_dir / "data_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Saved: {summary_file}")
        
    except Exception as e:
        print(f"\n✗ Error saving files: {e}")
        return None
    
    print()
    print("=" * 60)
    print("✓ PROCESSING COMPLETE!")
    print("=" * 60)
    print()
    
    return {"varroa_df": varroa_df, "colonies_df": colonies_df}


def main(raw_data_dir=None, output_dir=None):
    """Run the processing pipeline
    
    Args:
        raw_data_dir: Directory containing raw CSV files (default: data/raw)
        output_dir: Directory to write processed files (default: data/processed)
    """
    # Use provided paths or defaults
    if raw_data_dir is None:
        raw_data_dir = Path(__file__).parent.parent / "data" / "raw"
    
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data" / "processed"
    
    result = process_usda_data(raw_data_dir, output_dir)
    
    if result:
        return 0
    else:
        print("✗ Processing failed!")
        return 1


if __name__ == "__main__":
    import sys
    
    # Get directories from command line or use defaults
    raw_data_dir = sys.argv[1] if len(sys.argv) > 1 else None
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    sys.exit(main(raw_data_dir=raw_data_dir, output_dir=output_dir))
