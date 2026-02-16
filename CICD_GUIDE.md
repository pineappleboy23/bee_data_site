# CI/CD Quick Reference Guide

Quick commands and tips for using the CI/CD infrastructure.

## 🚀 Quick Commands

### Setup
```bash
# Install all dependencies
pip install -r pipeline/requirements.txt -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=pipeline

# Generate HTML coverage report
pytest tests/ -v --cov=pipeline --cov-report=html
# Open htmlcov/index.html

# Run specific test file
pytest tests/test_pipeline.py -v

# Run tests matching pattern
pytest tests/ -k "validation" -v
```

### Code Quality
```bash
# Format code
black pipeline/ tests/
isort pipeline/ tests/

# Check formatting (without changes)
black pipeline/ tests/ --check
isort pipeline/ tests/ --check

# Lint code
flake8 pipeline/ tests/

# Type check
mypy pipeline/

# Run all quality checks at once
pre-commit run --all-files
```

### Data Pipeline
```bash
# Recommended: Fetch via API (fast & reliable)
python pipeline/run_pipeline.py --api

# Fetch latest 3 releases
python pipeline/run_pipeline.py --api -n 3

# Or run steps individually:
# Step 1: Fetch USDA data via API
python pipeline/fetch_usda_api.py

# Step 2: Process data
python pipeline/process_usda_data.py

# Step 3: Run data validation
pytest tests/test_data_validation.py -v
```

## 🔧 Pre-commit Hooks

Pre-commit hooks run automatically before each `git commit`.

### What Gets Checked
- ✓ Trailing whitespace removal
- ✓ End-of-file fixing
- ✓ YAML syntax validation
- ✓ Large file prevention
- ✓ Black formatting
- ✓ isort import sorting
- ✓ flake8 linting
- ✓ Bandit security checks

### Manual Execution
```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Skip hooks for a commit (not recommended)
git commit --no-verify -m "message"
```

### Update Hooks
```bash
# Update to latest versions
pre-commit autoupdate
```

## 🔄 GitHub Actions Workflows

### CI Pipeline (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

**What It Does:**
1. Tests on Python 3.9, 3.10, 3.11
2. Runs linting (flake8)
3. Checks formatting (black, isort)
4. Runs test suite with coverage
5. Uploads coverage to Codecov

**Viewing Results:**
- Go to repository → Actions tab
- Click on latest workflow run
- View logs for each Python version

### CD Pipeline (`.github/workflows/deploy.yml`)

**Triggers:**
- Quarterly schedule: Jan 15, Apr 15, Jul 15, Oct 15 at 2 AM UTC
- Manual trigger via workflow dispatch

**What It Does:**
1. Fetches latest USDA data
2. Processes and validates data
3. Commits processed data to repo
4. Deploys to GitHub Pages

**Manual Trigger:**
1. Go to repository → Actions
2. Select "Deploy to GitHub Pages"
3. Click "Run workflow"
4. Select branch and click "Run workflow"

**Viewing Deployed Site:**
- https://YOUR_USERNAME.github.io/bee_data_site/

## 📊 Coverage Reports

### Local Coverage
```bash
# Generate coverage report
pytest tests/ -v --cov=pipeline --cov-report=html

# Open in browser
# Windows
start htmlcov/index.html
# Mac
open htmlcov/index.html
# Linux
xdg-open htmlcov/index.html
```

### Codecov Integration
- Coverage automatically uploaded from CI pipeline
- View at: https://codecov.io/gh/YOUR_USERNAME/bee_data_site
- Badge in README shows current coverage

## 🐛 Troubleshooting

### Tests Failing

**Check test output:**
```bash
# Verbose output
pytest tests/ -vv

# Show local variables on failure
pytest tests/ -vv --showlocals

# Stop at first failure
pytest tests/ -x
```

**Common Issues:**
- Missing data files → Run `python pipeline/fetch_usda_api.py`
- Import errors → Check Python path: `echo $PYTHONPATH`
- Dependency issues → Reinstall: `pip install -r requirements-dev.txt --force-reinstall`

### Pre-commit Hooks Failing

**Fix formatting:**
```bash
# Auto-fix with black
black pipeline/ tests/

# Auto-fix with isort
isort pipeline/ tests/

# Re-run hooks
pre-commit run --all-files
```

**Linting errors:**
```bash
# See detailed flake8 errors
flake8 pipeline/ tests/ --show-source

# Fix common issues
# - Remove unused imports
# - Fix indentation
# - Add blank lines per PEP 8
```

### CI Pipeline Failing

**Check logs:**
1. Go to Actions tab
2. Click failing workflow
3. Expand failed step
4. Read error message

**Common CI failures:**
- Linting: Fix locally with `flake8 pipeline/ tests/`
- Formatting: Fix with `black pipeline/ tests/` and `isort pipeline/ tests/`
- Tests: Debug with `pytest tests/ -vv`
- Coverage: Some tests not running or coverage threshold not met

**Fix and push:**
```bash
# Fix issues locally
black pipeline/ tests/
isort pipeline/ tests/
pytest tests/ -v --cov

# Commit and push
git add .
git commit -m "fix: resolve CI failures"
git push
```

### CD Pipeline Issues

**Data fetching fails:**
- Check USDA API availability
- Verify API endpoint in `fetch_usda_api.py`
- Check workflow logs for detailed errors

**Deployment fails:**
- Ensure GitHub Pages is enabled (Settings → Pages)
- Check repository permissions
- Verify deploy branch is correct

## 📦 Dependencies

### Adding New Dependencies

**Production dependency:**
```bash
# Add to pipeline/requirements.txt
echo "new-package>=1.0.0" >> pipeline/requirements.txt

# Install
pip install -r pipeline/requirements.txt
```

**Development dependency:**
```bash
# Add to requirements-dev.txt
echo "new-dev-package>=2.0.0" >> requirements-dev.txt

# Install
pip install -r requirements-dev.txt
```

**Update CI:**
- Dependencies are cached in CI
- Cache refreshes when requirements files change

## 🎯 Best Practices

### Before Committing
1. ✓ Run tests: `pytest tests/ -v`
2. ✓ Check formatting: `black pipeline/ tests/ --check`
3. ✓ Check imports: `isort pipeline/ tests/ --check`
4. ✓ Run linter: `flake8 pipeline/ tests/`
5. ✓ Pre-commit runs automatically

### Before Creating PR
1. ✓ All tests pass
2. ✓ Coverage maintained (check HTML report)
3. ✓ No linting errors
4. ✓ Documentation updated
5. ✓ Meaningful commit messages

### Code Review Checklist
- [ ] Tests added for new features
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] Error handling included
- [ ] Type hints added (when practical)

## 📚 Additional Resources

- **pytest docs**: https://docs.pytest.org/
- **Black docs**: https://black.readthedocs.io/
- **flake8 docs**: https://flake8.pycqa.org/
- **GitHub Actions docs**: https://docs.github.com/en/actions
- **Pre-commit docs**: https://pre-commit.com/

## 🆘 Getting Help

If you encounter issues:
1. Check this guide
2. Read full CONTRIBUTING.md
3. Check existing GitHub issues
4. Create new issue with details:
   - Error message
   - Steps to reproduce
   - Environment (OS, Python version)
   - Relevant logs

---

**Quick tip**: Bookmark this file for fast reference! 🔖
