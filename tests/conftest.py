"""
Pytest configuration and shared fixtures.
"""

import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def data_dir(project_root):
    """Get the data directory."""
    return project_root / "data"


@pytest.fixture(scope="session")
def raw_data_dir(data_dir):
    """Get the raw data directory."""
    return data_dir / "raw"


@pytest.fixture(scope="session")
def processed_data_dir(data_dir):
    """Get the processed data directory."""
    return data_dir / "processed"
