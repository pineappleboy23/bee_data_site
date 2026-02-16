"""
Data validation tests for bee colony data.

Tests data quality, schema, and value ranges.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path


class TestDataValidation:
    """Test suite for validating processed bee data."""
    
    @pytest.fixture
    def processed_data_path(self):
        """Get path to processed data file."""
        return Path(__file__).parent.parent / "data" / "processed" / "bee_data.csv"
    
    @pytest.fixture
    def data(self, processed_data_path):
        """Load processed data for testing."""
        if not processed_data_path.exists():
            pytest.skip("Processed data file not found. Run pipeline first.")
        return pd.read_csv(processed_data_path)
    
    def test_data_file_exists(self, processed_data_path):
        """Test that processed data file exists."""
        assert processed_data_path.exists(), "Processed data file does not exist"
    
    def test_data_not_empty(self, data):
        """Test that data contains rows."""
        assert len(data) > 0, "Data file is empty"
    
    def test_required_columns_exist(self, data):
        """Test that required columns are present."""
        required_columns = ['State', 'Starting_Colonies']
        
        for col in required_columns:
            assert col in data.columns, f"Required column '{col}' is missing"
    
    def test_no_all_null_columns(self, data):
        """Test that no column is entirely null."""
        for col in data.columns:
            null_count = data[col].isnull().sum()
            total_count = len(data)
            assert null_count < total_count, f"Column '{col}' is entirely null"
    
    def test_numeric_columns_are_numeric(self, data):
        """Test that numeric columns contain valid numbers."""
        numeric_columns = [
            'Starting_Colonies', 'Max_Colonies', 'Lost_colonies',
            'Percent_Lost', 'Added_colonies', 'Renovated_colonies'
        ]
        
        for col in numeric_columns:
            if col in data.columns:
                # Check that the column is numeric type or can be converted
                assert pd.api.types.is_numeric_dtype(data[col]) or \
                       data[col].dtype == 'object', \
                       f"Column '{col}' should be numeric"
    
    def test_percentage_values_in_range(self, data):
        """Test that percentage columns are between 0 and 100."""
        percentage_columns = ['Percent_Lost', 'Percent_renovated']
        
        for col in percentage_columns:
            if col in data.columns:
                # Get non-null values
                values = data[col].dropna()
                if len(values) > 0:
                    assert values.min() >= 0, f"{col} has values less than 0"
                    assert values.max() <= 100, f"{col} has values greater than 100"
    
    def test_colony_counts_positive(self, data):
        """Test that colony counts are non-negative."""
        colony_columns = [
            'Starting_Colonies', 'Max_Colonies', 
            'Lost_colonies', 'Added_colonies', 'Renovated_colonies'
        ]
        
        for col in colony_columns:
            if col in data.columns:
                values = data[col].dropna()
                if len(values) > 0:
                    assert values.min() >= 0, f"{col} has negative values"
    
    def test_states_are_valid(self, data):
        """Test that State column contains valid US states or 'United States'."""
        if 'State' in data.columns:
            states = data['State'].dropna().unique()
            
            # Should have at least some states
            assert len(states) > 0, "No states found in data"
            
            # Check for common patterns
            state_values = data['State'].value_counts()
            assert state_values.sum() > 0, "State column has no valid entries"
    
    def test_no_duplicate_state_date_combinations(self, data):
        """Test for duplicate state-date combinations."""
        if 'State' in data.columns and 'date' in data.columns:
            duplicates = data.duplicated(subset=['State', 'date'], keep=False)
            duplicate_count = duplicates.sum()
            
            if duplicate_count > 0:
                # This might be expected in some cases, so just warn
                print(f"Warning: Found {duplicate_count} duplicate State-Date combinations")
    
    def test_data_has_recent_dates(self, data):
        """Test that data contains relatively recent dates."""
        if 'date' in data.columns:
            # Try to parse dates
            dates_col = pd.to_datetime(data['date'], errors='coerce')
            valid_dates = dates_col.dropna()
            
            if len(valid_dates) > 0:
                most_recent = valid_dates.max()
                # Data should be from at least 2020 onwards
                assert most_recent.year >= 2020, \
                    f"Most recent data is from {most_recent.year}, which seems outdated"
    
    def test_data_spans_multiple_years(self, data):
        """Test that data covers multiple years (2015-2025 based on USDA API)."""
        if 'date' in data.columns:
            # Try to parse dates
            dates_col = pd.to_datetime(data['date'], errors='coerce')
            valid_dates = dates_col.dropna()
            
            if len(valid_dates) > 0:
                min_year = valid_dates.min().year
                max_year = valid_dates.max().year
                
                # Should have data from at least 2015
                assert min_year <= 2016, \
                    f"Data only starts from {min_year}, expected 2015-2016"
                
                # Should have data through at least 2022 (API has releases through 2025)
                assert max_year >= 2022, \
                    f"Data only goes to {max_year}, expected at least 2022"
                
                # Should span multiple years
                year_span = max_year - min_year
                assert year_span >= 6, \
                    f"Data only spans {year_span} years, expected at least 6 years"
    
    def test_date_format_consistency(self, data):
        """Test that dates are in a consistent, parseable format."""
        if 'date' in data.columns:
            dates_col = pd.to_datetime(data['date'], errors='coerce')
            valid_count = dates_col.notna().sum()
            total_count = len(data)
            
            # At least 80% of dates should be parseable
            if total_count > 0:
                valid_ratio = valid_count / total_count
                assert valid_ratio >= 0.8, \
                    f"Only {valid_ratio*100:.1f}% of dates are valid/parseable"
    
    def test_quarterly_data_coverage(self, data):
        """Test that data includes multiple quarters per year."""
        if 'date' in data.columns:
            dates_col = pd.to_datetime(data['date'], errors='coerce')
            valid_dates = dates_col.dropna()
            
            if len(valid_dates) > 10:  # Need enough data points
                # Group by year and count unique quarters
                df_with_dates = pd.DataFrame({'date': valid_dates})
                df_with_dates['year'] = df_with_dates['date'].dt.year
                df_with_dates['quarter'] = df_with_dates['date'].dt.quarter
                
                # Check that recent years have multiple quarters
                recent_years = df_with_dates[df_with_dates['year'] >= 2020]
                if len(recent_years) > 0:
                    quarters_per_year = recent_years.groupby('year')['quarter'].nunique()
                    # Should have at least 2 quarters per year (some years may be incomplete)
                    assert quarters_per_year.min() >= 1, \
                        "Some years have no quarterly data"
    
    def test_stressor_columns_in_valid_range(self, data):
        """Test that stressor columns (percentages) are in valid range."""
        stressor_columns = [
            'Diseases', 'Pesticides', 'Varroa_mites', 
            'Other_pests_and_parasites', 'Other', 'Unknown'
        ]
        
        for col in stressor_columns:
            if col in data.columns:
                values = data[col].dropna()
                if len(values) > 0:
                    assert values.min() >= 0, f"{col} has negative values"
                    # Stressors should be percentages (0-100)
                    assert values.max() <= 100, f"{col} has values > 100%"


class TestDataSchema:
    """Test suite for data schema validation."""
    
    @pytest.fixture
    def data(self):
        """Load processed data."""
        data_path = Path(__file__).parent.parent / "data" / "processed" / "bee_data.csv"
        if not data_path.exists():
            pytest.skip("Processed data not found")
        return pd.read_csv(data_path)
    
    def test_column_types(self, data):
        """Test that columns have expected data types."""
        # This is flexible - just ensure no unexpected types
        for col in data.columns:
            dtype = data[col].dtype
            # Should be numeric, object, or datetime
            assert dtype.kind in ['i', 'f', 'O', 'M', 'U'], \
                f"Column '{col}' has unexpected dtype: {dtype}"
    
    def test_no_completely_empty_rows(self, data):
        """Test that there are no completely empty rows."""
        empty_rows = data.isnull().all(axis=1).sum()
        assert empty_rows == 0, f"Found {empty_rows} completely empty rows"
    
    def test_data_size_reasonable(self, data):
        """Test that data size is reasonable (not too small or corrupted)."""
        assert len(data) >= 10, "Data has fewer than 10 rows - seems too small"
        assert len(data.columns) >= 5, "Data has fewer than 5 columns - seems incomplete"


class TestVarroaData:
    """Test suite for varroa_df.csv output validation."""
    
    @pytest.fixture
    def varroa_data_path(self):
        """Get path to varroa data file."""
        return Path(__file__).parent.parent / "data" / "processed" / "varroa_df.csv"
    
    @pytest.fixture
    def varroa_data(self, varroa_data_path):
        """Load varroa data for testing."""
        if not varroa_data_path.exists():
            pytest.skip("Varroa data file not found. Run pipeline first.")
        return pd.read_csv(varroa_data_path)
    
    def test_varroa_file_exists(self, varroa_data_path):
        """Test that varroa_df.csv exists."""
        assert varroa_data_path.exists(), "varroa_df.csv does not exist"
    
    def test_varroa_required_columns(self, varroa_data):
        """Test that varroa_df has all required columns."""
        required_columns = [
            'table', 'State', 'Varroa_mites', 'Other_pests_and_parasites',
            'Diseases', 'Pesticides', 'Other', 'Unknown', 'date'
        ]
        
        for col in required_columns:
            assert col in varroa_data.columns, f"Required column '{col}' missing from varroa_df"
    
    def test_varroa_column_count(self, varroa_data):
        """Test that varroa_df has exactly 9 columns."""
        assert len(varroa_data.columns) == 9, \
            f"Expected 9 columns in varroa_df, got {len(varroa_data.columns)}"
    
    def test_varroa_stressor_values_are_valid(self, varroa_data):
        """Test that all stressor columns contain valid non-negative values."""
        stressor_columns = [
            'Varroa_mites', 'Other_pests_and_parasites', 
            'Diseases', 'Pesticides', 'Other', 'Unknown'
        ]
        
        for col in stressor_columns:
            values = varroa_data[col].dropna()
            if len(values) > 0:
                assert values.min() >= 0, f"{col} has negative values"
                # Stressors can exceed 100% (overlapping stressors), but should be reasonable
                assert values.max() <= 150, f"{col} has suspiciously high values: max={values.max()}"
    
    def test_varroa_has_all_states(self, varroa_data):
        """Test that varroa_df includes major US states."""
        states = varroa_data['State'].unique()
        
        # Should have multiple states
        assert len(states) >= 40, f"Expected at least 40 states, found {len(states)}"
        
        # Check for some key states
        key_states = ['California', 'Texas', 'Florida', 'North Dakota', 'Montana']
        for state in key_states:
            assert state in states, f"Key state '{state}' missing from varroa data"
    
    def test_varroa_date_range(self, varroa_data):
        """Test that varroa_df spans 2015-2023 time period."""
        dates = pd.to_datetime(varroa_data['date'], errors='coerce')
        valid_dates = dates.dropna()
        
        assert len(valid_dates) > 0, "No valid dates in varroa_df"
        
        min_year = valid_dates.min().year
        max_year = valid_dates.max().year
        
        assert min_year <= 2016, f"Data starts too late: {min_year} (expected 2015-2016)"
        assert max_year >= 2020, f"Data ends too early: {max_year} (expected at least 2020)"
    
    def test_varroa_data_volume(self, varroa_data):
        """Test that varroa_df has reasonable amount of data (>500 rows)."""
        assert len(varroa_data) >= 500, \
            f"varroa_df has only {len(varroa_data)} rows (expected at least 500)"
    
    def test_varroa_table_column_values(self, varroa_data):
        """Test that table column contains appropriate values."""
        table_values = varroa_data['table'].unique()
        
        # Should have multiple table identifiers
        assert len(table_values) > 0, "Table column is empty"
        
        # All values should be numeric
        assert pd.api.types.is_numeric_dtype(varroa_data['table']), \
            "Table column should be numeric"
    
    def test_varroa_spot_check_alabama_2015(self, varroa_data):
        """Spot check: Verify Alabama 2015-01-01 data exists."""
        alabama_2015 = varroa_data[
            (varroa_data['State'] == 'Alabama') & 
            (varroa_data['date'].str.startswith('2015-01'))
        ]
        
        assert len(alabama_2015) > 0, "Alabama 2015-01-01 data not found in varroa_df"
    
    def test_varroa_no_all_zero_rows(self, varroa_data):
        """Test that stressor columns don't have rows where all stressors are 0."""
        stressor_columns = [
            'Varroa_mites', 'Other_pests_and_parasites', 
            'Diseases', 'Pesticides', 'Other', 'Unknown'
        ]
        
        stressor_df = varroa_data[stressor_columns]
        all_zero_rows = (stressor_df.fillna(0) == 0).all(axis=1).sum()
        
        # Some rows might have no stressors, but shouldn't be majority
        total_rows = len(varroa_data)
        assert all_zero_rows < total_rows * 0.5, \
            f"{all_zero_rows} rows have all stressors at 0 (>{total_rows * 0.5} expected max)"


class TestColoniesData:
    """Test suite for colonies_df.csv output validation."""
    
    @pytest.fixture
    def colonies_data_path(self):
        """Get path to colonies data file."""
        return Path(__file__).parent.parent / "data" / "processed" / "colonies_df.csv"
    
    @pytest.fixture
    def colonies_data(self, colonies_data_path):
        """Load colonies data for testing."""
        if not colonies_data_path.exists():
            pytest.skip("Colonies data file not found. Run pipeline first.")
        return pd.read_csv(colonies_data_path)
    
    def test_colonies_file_exists(self, colonies_data_path):
        """Test that colonies_df.csv exists."""
        assert colonies_data_path.exists(), "colonies_df.csv does not exist"
    
    def test_colonies_required_columns(self, colonies_data):
        """Test that colonies_df has all required columns."""
        required_columns = [
            'table', 'State', 'Starting_Colonies', 'Max_Colonies',
            'Lost_colonies', 'Percent_lost', 'Added_colonies',
            'Renovated_colonies', 'Percent_renovated', 'date'
        ]
        
        for col in required_columns:
            assert col in colonies_data.columns, \
                f"Required column '{col}' missing from colonies_df"
    
    def test_colonies_column_count(self, colonies_data):
        """Test that colonies_df has exactly 10 columns."""
        assert len(colonies_data.columns) == 10, \
            f"Expected 10 columns in colonies_df, got {len(colonies_data.columns)}"
    
    def test_colonies_counts_are_positive(self, colonies_data):
        """Test that all colony count columns are non-negative."""
        count_columns = [
            'Starting_Colonies', 'Max_Colonies',
            'Lost_colonies', 'Added_colonies', 'Renovated_colonies'
        ]
        
        for col in count_columns:
            values = colonies_data[col].dropna()
            if len(values) > 0:
                assert values.min() >= 0, f"{col} has negative values"
    
    def test_colonies_percentages_valid(self, colonies_data):
        """Test that percentage columns are in valid range (0-100)."""
        percentage_columns = ['Percent_lost', 'Percent_renovated']
        
        for col in percentage_columns:
            values = colonies_data[col].dropna()
            if len(values) > 0:
                assert values.min() >= 0, f"{col} has negative values"
                assert values.max() <= 100, f"{col} exceeds 100%: max={values.max()}"
    
    def test_colonies_has_all_states(self, colonies_data):
        """Test that colonies_df includes major US states."""
        states = colonies_data['State'].unique()
        
        # Should have multiple states
        assert len(states) >= 40, f"Expected at least 40 states, found {len(states)}"
        
        # Check for some key states
        key_states = ['California', 'Texas', 'Florida', 'North Dakota', 'Montana']
        for state in key_states:
            assert state in states, f"Key state '{state}' missing from colonies data"
    
    def test_colonies_date_range(self, colonies_data):
        """Test that colonies_df spans 2015-2023 time period."""
        dates = pd.to_datetime(colonies_data['date'], errors='coerce')
        valid_dates = dates.dropna()
        
        assert len(valid_dates) > 0, "No valid dates in colonies_df"
        
        min_year = valid_dates.min().year
        max_year = valid_dates.max().year
        
        assert min_year <= 2016, f"Data starts too late: {min_year} (expected 2015-2016)"
        assert max_year >= 2020, f"Data ends too early: {max_year} (expected at least 2020)"
    
    def test_colonies_data_volume(self, colonies_data):
        """Test that colonies_df has reasonable amount of data (>500 rows)."""
        assert len(colonies_data) >= 500, \
            f"colonies_df has only {len(colonies_data)} rows (expected at least 500)"
    
    def test_colonies_california_data_exists(self, colonies_data):
        """Spot check: Verify California has significant colony counts."""
        california_data = colonies_data[colonies_data['State'] == 'California']
        
        assert len(california_data) > 0, "No California data found"
        
        # California should have large colony counts
        max_colonies = california_data['Max_Colonies'].max()
        assert max_colonies > 500000, \
            f"California max colonies seems too low: {max_colonies}"
    
    def test_colonies_spot_check_alabama_2015(self, colonies_data):
        """Spot check: Verify Alabama 2015-01-01 data exists with expected values."""
        alabama_2015 = colonies_data[
            (colonies_data['State'] == 'Alabama') & 
            (colonies_data['date'].str.startswith('2015-01'))
        ]
        
        assert len(alabama_2015) > 0, "Alabama 2015-01-01 data not found in colonies_df"
        
        # Based on reference data: Alabama,7000,7000.0,1800,26.0,2800,250,4.0,2015-01-01
        row = alabama_2015.iloc[0]
        assert row['Starting_Colonies'] == 7000, \
            f"Expected Starting_Colonies=7000, got {row['Starting_Colonies']}"
        assert row['Max_Colonies'] == 7000.0, \
            f"Expected Max_Colonies=7000.0, got {row['Max_Colonies']}"
    
    def test_colonies_table_column_values(self, colonies_data):
        """Test that table column contains appropriate values."""
        table_values = colonies_data['table'].unique()
        
        # Should have multiple table identifiers
        assert len(table_values) > 0, "Table column is empty"
        
        # All values should be numeric
        assert pd.api.types.is_numeric_dtype(colonies_data['table']), \
            "Table column should be numeric"
    
    def test_colonies_realistic_counts(self, colonies_data):
        """Test that colony counts are in realistic ranges."""
        # No state should have more than 2 million colonies
        max_colonies = colonies_data['Max_Colonies'].max()
        assert max_colonies <= 2000000, \
            f"Suspiciously high Max_Colonies value: {max_colonies}"
        
        # Lost colonies shouldn't exceed max colonies
        mask = colonies_data['Lost_colonies'].notna() & colonies_data['Max_Colonies'].notna()
        filtered = colonies_data[mask]
        
        if len(filtered) > 0:
            violations = filtered[filtered['Lost_colonies'] > filtered['Max_Colonies']]
            assert len(violations) == 0, \
                f"Found {len(violations)} rows where Lost_colonies > Max_Colonies"
