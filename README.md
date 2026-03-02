# U.S. Bee Colony Health Explorer

![CI](https://github.com/pineappleboy23/bee_data_site/actions/workflows/ci.yml/badge.svg)
![Deploy](https://github.com/pineappleboy23/bee_data_site/actions/workflows/pages.yml/badge.svg)

**Live site:** https://pineappleboy23.github.io/bee_data_site/

An end-to-end data project built by Trent Hansen (Data Science, graduating May 2026). Raw USDA survey files are fetched from an API, cleaned, merged, and validated through a Python ETL pipeline, then served as an interactive D3.js dashboard on GitHub Pages. The pipeline runs on a quarterly schedule so the site stays current without manual intervention.

---

## What it does

The dashboard lets you explore honey bee colony health across all 50 U.S. states from 2015 to the present. Select a metric from the dropdown — colony counts, loss rates, or stressor percentages like Varroa mite impact — and the choropleth map updates immediately. Click any state to add its time-series to the chart on the right; click more states to compare them side by side. Hover the chart to read exact values at any point in time.

---

## ETL Pipeline

The bulk of the engineering work is in the data pipeline. USDA publishes bee colony surveys as ZIP archives containing multiple CSV tables per release, with each annual or semi-annual release using slightly different column layouts and special notation.

**Fetching** (`pipeline/fetch_usda_api.py`)  
Calls the USDA ESMIS REST API to discover all available releases, downloads each ZIP, and extracts the relevant CSVs into `data/raw/`. New releases are detected automatically — only files not yet present are downloaded.

**Processing and cleaning** (`pipeline/process_usda_data.py`)  
This is where the heaviest lifting happens:

- Merges raw CSVs from multiple release directories across years into a single unified dataset, handling the fact that column names and table layouts shift between releases.
- Translates USDA special notation into usable values:
  - `(Z)` → `0.25` (reported as "less than half the unit")
  - `(X)` → `NaN` (not applicable for that state/period)
  - `(NA)` → `NaN` (data not available)
  - `-` → `0` (explicit zero)
- Normalizes column names to consistent snake_case across all years.
- Produces two clean output files: `bee_data.csv` (colony counts and losses) and `varroa_df.csv` (stressor percentages), which the frontend loads and joins client-side.

**Validation** (`tests/test_data_validation.py`)  
Automated checks run after every pipeline execution:
- All required columns are present and correctly typed
- Percentages fall within 0–100
- Colony counts are non-negative
- Max colonies >= starting colonies for each row
- Data covers expected date range

---

## Automation

Two GitHub Actions workflows keep everything running without manual work:

`deploy.yml` — runs on the 15th of January, April, July, and October. Fetches new USDA data, processes it, runs validation tests, commits the updated CSVs, and pushes to `main`. Can also be triggered manually from the Actions tab.

`pages.yml` — deploys the site to GitHub Pages on every push to `main`. Because the data pipeline commits to `main`, a quarterly data update automatically triggers a fresh deploy.

`ci.yml` — runs the full test suite across Python 3.9, 3.10, and 3.11 on every push and pull request.

---

## Project structure

```
bee_data_site/
├── pipeline/
│   ├── fetch_usda_api.py     # USDA API fetcher
│   ├── process_usda_data.py  # Cleaning, merging, notation handling
│   ├── clean_data.py         # Shared cleaning utilities
│   ├── run_pipeline.py       # Entry point
│   └── requirements.txt
├── data/
│   ├── raw/                  # Downloaded source files (gitignored)
│   └── processed/            # Clean output CSVs committed for the site
├── tests/
│   ├── test_data_validation.py
│   ├── test_pipeline.py
│   └── conftest.py
├── .github/workflows/
│   ├── ci.yml
│   ├── deploy.yml            # Quarterly data pipeline
│   └── pages.yml             # Site deployment
├── js/
│   ├── script.js             # App state and data loading
│   ├── map.js                # Choropleth map
│   ├── line-chart.js         # Time-series chart
│   └── data/us-states.json
├── index.html
└── styles.css
```

---

## Running locally

```bash
# Clone
git clone https://github.com/pineappleboy23/bee_data_site.git
cd bee_data_site

# Install pipeline dependencies
pip install -r pipeline/requirements.txt

# Fetch and process data
python pipeline/run_pipeline.py --api

# Run tests
pytest tests/ -v

# Serve the site
python -m http.server 8000
# Open http://localhost:8000
```

---

## Data source

USDA NASS Honey Bee Colonies survey — published quarterly.  
https://usda.library.cornell.edu/concern/publications/rn301137d  
API endpoint: https://esmis.nal.usda.gov/api/v1/release/findByPubId/1585
