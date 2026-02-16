"""
Pipeline functionality tests.

Tests the data processing scripts and functions.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add pipeline to path
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from process_usda_data import (
    apply_special_value_replacements,
    convert_specific_columns,
    clean_column_names,
    remove_unwanted_columns
)


class TestUSDADataProcessing:
    """Test USDA data processing functions."""
    
    def test_special_value_replacements(self):
        """Test that special USDA values are replaced correctly."""
        df = pd.DataFrame({
            'A': ['(Z)', '(X)', '(NA)', '-', '100'],
            'B': [1, 2, 3, 4, 5]
        })
        
        result = apply_special_value_replacements(df)
        
        # (Z) should become 0.25
        assert result.loc[0, 'A'] == 0.25
        # (X) and (NA) should become NaN
        assert pd.isna(result.loc[1, 'A'])
        assert pd.isna(result.loc[2, 'A'])
        # - should become 0
        assert result.loc[3, 'A'] == 0
        # Regular values unchanged
        assert result.loc[4, 'A'] == '100'
    
    def test_column_name_cleaning(self):
        """Test that column names are cleaned properly."""
        df = pd.DataFrame({
            'Column Name': [1, 2],
            'Another Column': [3, 4],
            'No_Change': [5, 6]
        })
        
        result = clean_column_names(df)
        
        assert 'Column_Name' in result.columns
        assert 'Another_Column' in result.columns
        assert 'No_Change' in result.columns
        assert 'Column Name' not in result.columns
    
    def test_numeric_conversion(self):
        """Test that columns are converted to numeric correctly."""
        df = pd.DataFrame({
            'State': ['California', 'Texas', 'Idaho'],
            'Colonies': ['1000', '2000', '3000'],
            'Percent': ['10.5', '20.3', '15.0']
        })
        
        result = convert_specific_columns(df, exclude_columns=['State'])
        
        # State should remain string
        assert result['State'].dtype == 'object'
        # Numeric columns should be numeric
        assert pd.api.types.is_numeric_dtype(result['Colonies'])
        assert pd.api.types.is_numeric_dtype(result['Percent'])
        # Values should be correct
        assert result.loc[0, 'Colonies'] == 1000
        assert result.loc[1, 'Percent'] == 20.3
    
    def test_column_removal(self):
        """Test that unwanted columns are removed."""
        df = pd.DataFrame({
            'Keep1': [1, 2],
            'Keep2': [3, 4],
            'Remove1': [5, 6],
            'Remove2': [7, 8]
        })
        
        result = remove_unwanted_columns(df, ['Remove1', 'Remove2'])
        
        assert 'Keep1' in result.columns
        assert 'Keep2' in result.columns
        assert 'Remove1' not in result.columns
        assert 'Remove2' not in result.columns
    
    def test_handle_invalid_numeric_conversion(self):
        """Test that invalid values are handled during numeric conversion."""
        df = pd.DataFrame({
            'State': ['CA', 'TX'],
            'Value': ['invalid', '123']
        })
        
        result = convert_specific_columns(df, exclude_columns=['State'])
        
        # Invalid value should become NaN
        assert pd.isna(result.loc[0, 'Value'])
        # Valid value should be converted
        assert result.loc[1, 'Value'] == 123


class TestDataConsistency:
    """Test data consistency across pipeline stages."""
    
    def test_raw_data_exists(self):
        """Test that raw data directory exists."""
        raw_dir = Path(__file__).parent.parent / "data" / "raw"
        assert raw_dir.exists(), "Raw data directory does not exist"
    
    def test_processed_data_directory_exists(self):
        """Test that processed data directory exists."""
        processed_dir = Path(__file__).parent.parent / "data" / "processed"
        assert processed_dir.exists(), "Processed data directory does not exist"
    
    @pytest.mark.skipif(
        not (Path(__file__).parent.parent / "data" / "processed" / "bee_data.csv").exists(),
        reason="Processed data not available"
    )
    def test_processed_data_is_valid_csv(self):
        """Test that processed CSV can be loaded."""
        data_path = Path(__file__).parent.parent / "data" / "processed" / "bee_data.csv"
        
        # Should be able to load without error
        df = pd.read_csv(data_path)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty dataframes."""
        df = pd.DataFrame()
        
        # Should not crash
        result = clean_column_names(df)
        assert len(result) == 0
    
    def test_all_null_column(self):
        """Test handling of columns with all null values."""
        df = pd.DataFrame({
            'A': [None, None, None],
            'B': [1, 2, 3]
        })
        
        result = convert_specific_columns(df, exclude_columns=[])
        
        # Should handle gracefully
        assert 'A' in result.columns
        assert 'B' in result.columns
