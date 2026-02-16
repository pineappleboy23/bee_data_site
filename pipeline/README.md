# Bee Data Pipeline

This pipeline fetches and processes USDA bee colony data for the visualization website.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Recommended: Automated API Fetch (Fastest & Most Reliable)

Use the USDA ESMIS API to automatically download the latest data:

```bash
# Fetch latest data via API and process
python pipeline/run_pipeline.py --api

# Fetch multiple releases (e.g., last 3 reports)
python pipeline/run_pipeline.py --api -n 3
```

This method:
- ✓ Uses official USDA API
- ✓ Fast and reliable
- ✓ No manual downloads needed
- ✓ Direct ZIP file URLs
- ✓ Handles extraction automatically

### Alternative: Process From Existing Data (Default)

### Alternative: Process From Existing Data (Default)

If you already have CSV files in `data/raw/` (from manual download):

```bash
python pipeline/run_pipeline.py
```

This processes all CSV files in `data/raw/` and outputs to `data/processed/bee_data.csv`.

## Usage Options

### `run_pipeline.py` - Unified Pipeline Runner

The main pipeline runner with flexible modes:

```bash
# Recommended: Fetch via API, then process
python pipeline/run_pipeline.py --api

# Fetch multiple releases (e.g., last 3)
python pipeline/run_pipeline.py --api -n 3

# Default: Process from existing CSV files in data/raw/
python pipeline/run_pipeline.py

# Fetch from GitHub URL, then process
python pipeline/run_pipeline.py --fetch

# Full pipeline with API fetch
python pipeline/run_pipeline.py --full
```

**Arguments:**
- No args (default): Processes existing CSVs in `data/raw/`
- `--api`: Fetches via USDA API, then processes (recommended)
- `-n, --num-releases N`: Number of releases to fetch via API (default: 1)
- `--fetch`: Fetches from GitHub URL, then uses basic transform
- `--full`: Full pipeline with API fetch (alias for `--api`)

### Individual Scripts

You can also run pipeline steps independently:

**1. Fetch Raw Data**

```bash
# Option A: Fetch via API (Recommended)
python pipeline/fetch_usda_api.py           # Latest release
python pipeline/fetch_usda_api.py -n 3      # Last 3 releases
python pipeline/fetch_usda_api.py --all     # All available releases

# Option B: Download from GitHub URL
python pipeline/fetch.py
```

**2. Process Data**

```bash
# Option A: Basic transform (for GitHub data)
python pipeline/transform.py

# Option B: Advanced USDA processing (for USDA data)
python pipeline/process_usda_data.py
```

### Option 2: USDA Data Processing (From Colab Workflow)

If you have raw USDA CSV files (from https://usda.library.cornell.edu/concern/publications/rn301137d):

1. Place your raw CSV files in `data/raw/`
2. Run the USDA processing script:

```bash
python pipeline/process_usda_data.py
```

This script handles:
- Multiple CSV file loading
- USDA special notation: (Z), (X), (NA), (-)
- Column name standardization
- Numeric type conversion
- DataFrame merging
- Data validation

### Run Complete Pipeline

```bash
python pipeline/run_pipeline.py
```

## Data Flow

### Simple Flow
```
External Source (GitHub) 
    ↓ fetch.py
data/raw/bee_data_latest.csv
    ↓ transform.py
data/processed/bee_data.csv
data/processed/bee_data.json
    ↓
Frontend (js/script.js)
```

### USDA Data Flow
```
USDA CSV Files (manual download)
    ↓
data/raw/*.csv
    ↓ process_usda_data.py
data/processed/bee_data.csv
data/processed/bee_data.json
    ↓
Frontend (js/script.js)
```

## Scripts

- **`fetch.py`** - Download data from external GitHub source
- **`transform.py`** - Basic data cleaning and processing
- **`process_usda_data.py`** - Advanced USDA data processing (based on your Colab notebook)
- **`run_pipeline.py`** - Execute full pipeline automatically

## Future Enhancements

- Add scheduling (cron job or GitHub Actions) for automatic updates
- Connect to USDA API for official data source
- Add data validation and quality checks
- Implement versioning for data snapshots
- Add more data sources (weather, pesticide use, etc.)
- Create data quality reports
- Add automated testing
