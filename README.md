# 🐝 Bee Colony Data Visualization

![CI/CD Pipeline](https://github.com/YOUR_USERNAME/bee_data_site/workflows/CI%20Pipeline/badge.svg)
![Deploy Status](https://github.com/YOUR_USERNAME/bee_data_site/workflows/Deploy%20to%20GitHub%20Pages/badge.svg)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/bee_data_site/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/bee_data_site)

An interactive data visualization tool for tracking honey bee colony health across the United States. Features automated data pipelines, comprehensive testing, and CI/CD workflows for quarterly USDA data updates.

## 🎯 Features

### Data Visualization
- **Interactive US Map**: State-by-state choropleth visualization of bee colony metrics
- **Time Series Charts**: Track colony counts and health indicators over time
- **Dynamic Filtering**: Compare metrics across states and time periods
- **Responsive Design**: Built with D3.js v7 for smooth interactions

### Data Pipeline
- **Automated Data Fetching**: USDA API integration
- **Data Processing**: Handles USDA special notation ((Z), (X), (NA), -)
- **Data Validation**: Comprehensive quality checks for schema, ranges, and consistency
- **Quarterly Updates**: Scheduled pipeline runs for new USDA releases

### CI/CD Infrastructure
- **Automated Testing**: pytest suite with 15+ validation tests
- **Multi-Version Testing**: Python 3.9, 3.10, 3.11 compatibility
- **Code Coverage**: Integrated with Codecov for visibility
- **Code Quality**: flake8, black, isort, mypy enforcement
- **Pre-commit Hooks**: Automatic formatting and linting
- **GitHub Actions**: Automated deployment to GitHub Pages

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    QUARTERLY SCHEDULE                        │
│         (Jan 15, Apr 15, Jul 15, Oct 15 @ 2 AM UTC)        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │  Fetch USDA Data │  ← fetch_usda_api.py
              │  (API Method)    │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  Process Data    │  ← process_usda_data.py
              │  (Clean, Merge)  │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  Validate Data   │  ← tests/test_data_validation.py
              │  (Quality Tests) │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  Auto-Commit &   │  ← .github/workflows/deploy.yml
              │  Deploy to Pages │
              └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/bee_data_site.git
   cd bee_data_site
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r pipeline/requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

### Running Locally

1. **Fetch and process data**
   ```bash
   # Option 1: Use USDA API (Recommended - Fast & Reliable)
   python pipeline/run_pipeline.py --api
   
   # Option 2: Fetch latest 3 releases via API
   python pipeline/run_pipeline.py --api -n 3
   
   # Option 3: Process existing CSV files
   # (Place CSV or ZIP files in data/raw/ first)
   python pipeline/run_pipeline.py
   ```

2. **Run tests**
   ```bash
   # Run all tests with coverage
   pytest tests/ -v --cov=pipeline --cov-report=html
   
   # View coverage report
   # Open htmlcov/index.html in browser
   ```

3. **View the site**
   ```bash
   # Serve locally (requires Python http.server or similar)
   python -m http.server 8000
   # Open http://localhost:8000 in browser
   ```

## 🧪 Testing

### Test Suite Overview
- **Data Validation**: Schema checks, range validation, consistency tests
- **Pipeline Tests**: Unit tests for data processing functions
- **Edge Cases**: Special USDA notation handling, missing data, invalid inputs

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=pipeline --cov-report=term-missing

# Run specific test file
pytest tests/test_data_validation.py -v

# Run tests matching pattern
pytest tests/ -k "test_schema" -v
```

## 📊 Data Processing

### USDA Special Notation Handling
The pipeline correctly processes USDA NASS special notation:
- `(Z)` → 0.25 (less than half the reporting unit)
- `(X)` → NaN (not applicable)
- `(NA)` → NaN (not available)
- `-` → 0 (zero value)

### Data Sources
- **Primary**: USDA NASS Honey Bee Surveys (Quarterly)
- **API**: https://esmis.nal.usda.gov/api/v1/release/findByPubId/1585
- **Web**: https://usda.library.cornell.edu/concern/publications/rn301137d
- **Update Frequency**: Quarterly (January, April, July, October)
- **Format**: ZIP files containing CSV data tables

### Data Validation
Automated quality checks ensure:
- ✓ Schema compliance (required columns present)
- ✓ Range validation (percentages 0-100%, colonies ≥ 0)
- ✓ Consistency checks (max_colonies ≥ starting_colonies)
- ✓ Date recency (data not older than 2 years)
- ✓ Stressor percentage logic (sum validation)

## 🔄 CI/CD Workflows

### Continuous Integration (CI)
**Trigger**: Push/PR to `main` or `develop`

Pipeline steps:
1. **Test Matrix**: Python 3.9, 3.10, 3.11
2. **Install Dependencies**: Cached pip packages
3. **Lint**: flake8 (E9, F63, F7, F82 error codes)
4. **Format Check**: black and isort validation
5. **Test**: pytest with coverage reporting
6. **Coverage**: Upload to Codecov

### Continuous Deployment (CD)
**Trigger**: Quarterly schedule (15th of Jan/Apr/Jul/Oct @ 2 AM UTC)

Pipeline steps:
1. **Fetch Data**: Call USDA API
2. **Process Data**: Clean and validate
3. **Run Tests**: Ensure data quality
4. **Commit**: Auto-commit processed data
5. **Deploy**: Push to GitHub Pages

## 🛠️ Development

### Code Quality Tools

```bash
# Format code with black
black pipeline/ tests/

# Sort imports with isort
isort pipeline/ tests/

# Lint with flake8
flake8 pipeline/ tests/

# Type check with mypy
mypy pipeline/
```

### Pre-commit Hooks
Pre-commit hooks automatically run before each commit:
- ✓ Trailing whitespace removal
- ✓ YAML/TOML syntax validation
- ✓ black formatting
- ✓ isort import sorting
- ✓ flake8 linting
- ✓ bandit security checks

```bash
# Run hooks manually
pre-commit run --all-files
```

### Project Structure

```
bee_data_site/
├── pipeline/
│   ├── fetch.py              # Basic data fetcher
│   ├── fetch_usda_api.py     # USDA API fetcher (recommended)
│   ├── transform.py          # Basic data cleaning
│   ├── process_usda_data.py  # Advanced USDA processing
│   ├── requirements.txt      # Pipeline dependencies
│   └── README.md            # Pipeline documentation
├── data/
│   ├── raw/                 # Downloaded raw data
│   ├── processed/           # Cleaned, validated data
│   └── README.md           # Data documentation
├── tests/
│   ├── test_data_validation.py  # Data quality tests
│   ├── test_pipeline.py         # Pipeline unit tests
│   └── conftest.py              # Test fixtures
├── .github/workflows/
│   ├── ci.yml               # CI pipeline
│   └── deploy.yml           # CD pipeline
├── js/
│   ├── script.js            # Main visualization logic
│   ├── map.js              # US map component
│   ├── line-chart.js       # Time series component
│   └── data/               # Map GeoJSON data
├── index.html              # Main HTML page
├── styles.css              # Styles
├── pyproject.toml          # Python tool configuration
├── requirements-dev.txt    # Development dependencies
└── .pre-commit-config.yaml # Pre-commit hook config
```

## 📈 Key Metrics

### Visualization Metrics
- States Tracked: 50 states + DC + US aggregate
- Time Period: 2015-present
- Metrics:
  - Colony counts (starting, max, lost, added)
  - Loss percentages
  - Renovation percentages
  - Stressor impact percentages (Varroa mites, diseases, pesticides, etc.)

### Code Quality Metrics
- Test Coverage: Target 80%+
- Linting: All critical flake8 errors enforced
- Formatting: black + isort compliance
- Type Safety: mypy validation (gradual typing)

## 🤝 Contributing

### Workflow
1. Create feature branch from `develop`
2. Make changes (pre-commit hooks will run automatically)
3. Run tests: `pytest tests/ -v --cov`
4. Push and create PR to `develop`
5. CI pipeline runs automatically
6. Merge after approval

### Coding Standards
- **Style**: Black formatting (line length 100)
- **Imports**: isort with black profile
- **Linting**: flake8 compliance
- **Testing**: pytest for all new features
- **Type Hints**: Encouraged for function signatures

## 📝 License

This project is open source and available under the MIT License.

## 🔗 Links

- **Live Site**: https://YOUR_USERNAME.github.io/bee_data_site/
- **Data Source**: [USDA NASS Honey Bee Surveys](https://usda.library.cornell.edu/concern/publications/rn301137d)
- **Issues**: https://github.com/YOUR_USERNAME/bee_data_site/issues

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with** ❤️ **and** 🐝 **for better bee data accessibility**
