# Contributing to Bee Colony Data Visualization

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [CI/CD Pipeline](#cicd-pipeline)

## Getting Started

### Prerequisites
- Python 3.9+
- Git
- Code editor (VS Code recommended)

### Initial Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/bee_data_site.git
   cd bee_data_site
   ```

2. **Install dependencies**
   ```bash
   # Production dependencies
   pip install -r pipeline/requirements.txt
   
   # Development dependencies
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```
   
   This will automatically run code formatters and linters before each commit.

4. **Verify setup**
   ```bash
   # Run tests
   pytest tests/ -v
   
   # Run formatters
   black pipeline/ tests/ --check
   isort pipeline/ tests/ --check
   
   # Run linter
   flake8 pipeline/ tests/
   ```

## Development Workflow

### Branch Strategy
- `main` - Production branch, always stable
- `develop` - Integration branch for features
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Urgent production fixes

### Creating a Feature Branch

```bash
# Start from develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name
```

### Making Changes

1. **Write code** - Make your changes
2. **Format code** - Pre-commit hooks will run automatically on commit
3. **Run tests** - Ensure all tests pass
4. **Commit changes** - Use descriptive commit messages

```bash
# Format manually (if needed)
black pipeline/ tests/
isort pipeline/ tests/

# Run tests
pytest tests/ -v --cov=pipeline

# Commit
git add .
git commit -m "feat: add new data validation check"
```

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add support for additional USDA data formats
fix: handle missing state data in choropleth map
docs: update README with deployment instructions
test: add edge case tests for special notation handling
```

## Code Standards

### Python Code Style

**Formatting**
- Use [Black](https://black.readthedocs.io/) for code formatting
- Line length: 100 characters
- Use [isort](https://pycqa.github.io/isort/) for import sorting

**Linting**
- Use [flake8](https://flake8.pycqa.org/) for linting
- Critical error codes enforced:
  - E9: Runtime errors
  - F63: Invalid syntax
  - F7: Syntax errors
  - F82: Undefined names

**Type Hints**
- Use type hints for function signatures when practical
- Use [mypy](http://mypy-lang.org/) for type checking

**Example Function**
```python
from typing import List, Dict
import pandas as pd

def process_state_data(
    df: pd.DataFrame, 
    state: str
) -> Dict[str, float]:
    """
    Process bee colony data for a specific state.
    
    Args:
        df: DataFrame containing colony data
        state: Two-letter state code
        
    Returns:
        Dictionary of aggregated metrics
    """
    state_data = df[df['State'] == state]
    return {
        'avg_colonies': state_data['starting_colonies'].mean(),
        'total_lost': state_data['lost_colonies'].sum()
    }
```

### JavaScript Code Style

**General Guidelines**
- Use ES6+ features (arrow functions, const/let, async/await)
- Use camelCase for variables and functions
- Use PascalCase for classes
- Add comments for complex logic
- Keep functions focused and small

**Example**
```javascript
/**
 * Filter data by selected state and year
 */
const filterData = (data, state, year) => {
    return data.filter(d => 
        d.state === state && 
        new Date(d.date).getFullYear() === year
    );
};
```

### Documentation

**Python Docstrings**
Use Google-style docstrings:

```python
def calculate_loss_percentage(lost: int, starting: int) -> float:
    """
    Calculate the percentage of colonies lost.
    
    Args:
        lost: Number of colonies lost
        starting: Starting number of colonies
        
    Returns:
        Loss percentage (0-100)
        
    Raises:
        ValueError: If starting is zero or negative
        
    Example:
        >>> calculate_loss_percentage(10, 100)
        10.0
    """
    if starting <= 0:
        raise ValueError("Starting colonies must be positive")
    return (lost / starting) * 100
```

**README Updates**
- Update README.md when adding major features
- Include examples for new functionality
- Update architecture diagrams if structure changes

## Testing

### Writing Tests

**Test Structure**
```python
import pytest
from pipeline.process_usda_data import apply_special_value_replacements

class TestSpecialValueHandling:
    """Tests for USDA special notation handling."""
    
    def test_z_notation_replacement(self):
        """Test (Z) notation converts to 0.25."""
        result = apply_special_value_replacements("(Z)")
        assert result == 0.25
    
    def test_dash_replacement(self):
        """Test dash converts to 0."""
        result = apply_special_value_replacements("-")
        assert result == 0
```

**Test Types**
1. **Unit Tests** - Test individual functions
2. **Integration Tests** - Test pipeline workflows
3. **Data Validation Tests** - Test data quality

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_pipeline.py -v

# Run with coverage
pytest tests/ -v --cov=pipeline --cov-report=html

# Run tests matching pattern
pytest tests/ -k "test_special" -v

# Run and stop at first failure
pytest tests/ -x
```

### Test Coverage

- Target: 80%+ coverage for pipeline code
- View coverage report: `htmlcov/index.html` after running tests with `--cov-report=html`
- CI pipeline enforces coverage reporting

### Adding Tests for New Features

When adding a new feature:
1. Write tests first (TDD approach encouraged)
2. Ensure tests cover edge cases
3. Add docstrings to test functions
4. Run full test suite before committing

## Pull Request Process

### Before Submitting

**Checklist:**
- [ ] All tests pass locally
- [ ] Code is formatted (black, isort)
- [ ] Code passes linting (flake8)
- [ ] Coverage is maintained or improved
- [ ] Documentation is updated
- [ ] Commit messages follow convention
- [ ] No sensitive data in commits

### Submitting a Pull Request

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub**
   - Base branch: `develop`
   - Compare branch: `feature/your-feature-name`
   - Fill out PR template

3. **PR Description Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Tests pass locally
   - [ ] New tests added
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No new warnings
   ```

4. **Wait for CI/CD**
   - CI pipeline runs automatically
   - Must pass before merge
   - Address any failures

5. **Code Review**
   - Respond to feedback
   - Make requested changes
   - Request re-review

6. **Merge**
   - Squash and merge (preferred)
   - Delete branch after merge

## CI/CD Pipeline

### Continuous Integration (CI)

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

**Pipeline Steps:**
1. **Setup** - Install Python 3.9, 3.10, 3.11
2. **Dependencies** - Install requirements (cached)
3. **Lint** - Run flake8
4. **Format Check** - Verify black and isort
5. **Test** - Run pytest with coverage
6. **Report** - Upload coverage to Codecov

**Viewing Results:**
- Check Actions tab in GitHub
- View coverage at codecov.io
- All checks must pass

### Continuous Deployment (CD)

**Triggers:**
- Quarterly schedule (Jan 15, Apr 15, Jul 15, Oct 15)
- Manual workflow dispatch

**Pipeline Steps:**
1. **Fetch** - Download latest USDA data
2. **Process** - Clean and validate data
3. **Test** - Run data validation tests
4. **Commit** - Auto-commit processed data
5. **Deploy** - Push to GitHub Pages

### Manual CI/CD Testing

Test locally before pushing:

```bash
# Run the full CI pipeline locally
pytest tests/ -v --cov=pipeline --cov-report=term-missing
black pipeline/ tests/ --check
isort pipeline/ tests/ --check
flake8 pipeline/ tests/
mypy pipeline/

# Test data pipeline
python pipeline/fetch_usda_api.py
python pipeline/process_usda_data.py
pytest tests/test_data_validation.py -v
```

## Questions or Issues?

- **Bug Reports**: Open an issue with `bug` label
- **Feature Requests**: Open an issue with `enhancement` label
- **Questions**: Open a discussion or issue with `question` label

Thank you for contributing! 🐝

