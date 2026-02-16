# Bee Colony Data

This directory contains bee colony data for visualization.

## Data Sources

### Primary Source
- **USDA NASS Honey Bee Surveys**
- URL: https://usda.library.cornell.edu/concern/publications/rn301137d
- Contains quarterly honey bee colony data including:
  - Starting colonies
  - Maximum colonies
  - Lost colonies  
  - Added colonies
  - Renovated colonies
  - Stressors (diseases, pesticides, varroa mites, etc.)
  - State-by-state breakdowns

### Alternative/Current Source
- **GitHub Repository** (merged_df.csv)
- URL: https://raw.githubusercontent.com/pineappleboy23/DS_data/refs/heads/main/merged_df.csv
- Pre-processed merged dataset

## Directory Structure

```
data/
├── raw/               # Raw data files (git-ignored)
│   ├── bee_data_latest.csv
│   └── *.csv          # Any manually downloaded USDA files
├── processed/         # Cleaned/processed data (tracked in git)
│   ├── bee_data.csv
│   ├── bee_data.json
│   └── data_summary.json
└── README.md          # This file
```

## Data Format

### Common Columns (after processing)
- `State` - US state name
- `date` - Date or period of observation
- `Starting_Colonies` - Number of colonies at start of period
- `Max_Colonies` - Maximum number of colonies during period
- `Lost_colonies` - Number of colonies lost
- `Percent_Lost` - Percentage of colonies lost
- `Added_colonies` - Number of colonies added
- `Renovated_colonies` - Number of colonies renovated
- `Diseases` - Percentage affected by diseases
- `Pesticides` - Percentage affected by pesticides
- `Varroa_mites` - Percentage affected by varroa mites
- `Other_pests_and_parasites` - Percentage affected by other pests

### USDA Special Notations

The USDA uses special notation in their data:
- `(Z)` - Less than half the unit shown (converted to 0.25)
- `(X)` - Not applicable (converted to NaN)
- `(NA)` - Not available (converted to NaN)
- `-` - None reported (converted to 0)

These are automatically handled by the `process_usda_data.py` script.

## Updating Data

### From GitHub (Automated)
```bash
python pipeline/fetch.py
python pipeline/transform.py
```

### From USDA (Manual Download)
1. Download CSV files from https://usda.library.cornell.edu/concern/publications/rn301137d
2. Place in `data/raw/`
3. Run: `python pipeline/process_usda_data.py`

## Notes

- Raw CSV files are excluded from git (see `.gitignore`)
- Processed data is tracked in git for easy deployment
- If processed files become too large, they can be excluded from git
- Data should be updated quarterly when USDA releases new surveys