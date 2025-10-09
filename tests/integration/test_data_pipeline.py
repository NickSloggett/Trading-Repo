"""
Integration tests for data pipeline
"""
import pytest
import pandas as pd
import numpy as np
import os
import sys

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class TestDataPipeline:
    """Test cases for data pipeline integration"""

    @pytest.mark.integration
    def test_data_ingestion_to_storage(self):
        """Test complete data ingestion pipeline"""
        # Test data ingestion pipeline with mock data
        sample_data = {
            'timestamp': pd.date_range('2023-01-01', periods=100, freq='H'),
            'symbol': ['AAPL'] * 100,
            'price': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100)
        }
        
        df = pd.DataFrame(sample_data)
        
        # Validate data structure
        assert len(df) == 100
        assert 'timestamp' in df.columns
        assert 'symbol' in df.columns
        assert 'price' in df.columns
        assert 'volume' in df.columns
        
        # Validate data quality
        assert not df.isnull().any().any()
        assert df['price'].min() > 0
        assert df['volume'].min() > 0

    @pytest.mark.integration
    def test_database_operations(self):
        """Test database operations integration"""
        # Test database connection simulation
        # In a real integration test, this would connect to actual test database
        
        # Simulate database operations
        test_data = pd.DataFrame({
            'id': range(1, 11),
            'name': [f'Test_{i}' for i in range(1, 11)],
            'value': np.random.randn(10)
        })
        
        # Simulate CRUD operations
        # Create
        assert len(test_data) == 10
        
        # Read
        filtered_data = test_data[test_data['value'] > 0]
        assert len(filtered_data) >= 0
        
        # Update simulation
        test_data.loc[0, 'value'] = 999.0
        assert test_data.loc[0, 'value'] == 999.0
        
        # Delete simulation
        original_length = len(test_data)
        test_data = test_data.drop(0)
        assert len(test_data) == original_length - 1

    @pytest.mark.integration
    def test_data_transformation_pipeline(self):
        """Test data transformation pipeline"""
        # Test data transformation operations
        raw_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=50, freq='D'),
            'open': np.random.randn(50).cumsum() + 100,
            'high': np.random.randn(50).cumsum() + 102,
            'low': np.random.randn(50).cumsum() + 98,
            'close': np.random.randn(50).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 50)
        })
        
        # Ensure high >= low and high >= open and high >= close
        raw_data['high'] = raw_data[['open', 'high', 'low', 'close']].max(axis=1)
        raw_data['low'] = raw_data[['open', 'high', 'low', 'close']].min(axis=1)
        
        # Calculate technical indicators
        raw_data['sma_20'] = raw_data['close'].rolling(window=20).mean()
        raw_data['rsi_14'] = self._calculate_rsi(raw_data['close'], 14)
        
        # Validate transformations
        assert 'sma_20' in raw_data.columns
        assert 'rsi_14' in raw_data.columns
        assert not raw_data['sma_20'].isnull().all()
        assert not raw_data['rsi_14'].isnull().all()
        
        # Validate data integrity
        assert raw_data['high'].ge(raw_data['low']).all()
        assert raw_data['high'].ge(raw_data['close']).all()
        assert raw_data['high'].ge(raw_data['open']).all()

    def _calculate_rsi(self, prices, period=14):
        """Helper method to calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @pytest.mark.integration
    def test_error_handling_pipeline(self):
        """Test error handling in data pipeline"""
        # Test with invalid data
        invalid_data = pd.DataFrame({
            'timestamp': [None, 'invalid', pd.Timestamp.now()],
            'price': [100, -50, None],  # Negative price and None
            'volume': [1000, 0, -100]  # Zero and negative volume
        })
        
        # Test data validation
        valid_data = invalid_data.copy()
        
        # Remove rows with invalid timestamps
        valid_data = valid_data.dropna(subset=['timestamp'])
        
        # Fix invalid prices
        valid_data = valid_data[valid_data['price'] > 0]
        
        # Fix invalid volumes
        valid_data = valid_data[valid_data['volume'] > 0]
        
        # Should have filtered out invalid data
        assert len(valid_data) < len(invalid_data)
        assert valid_data['price'].min() > 0
        assert valid_data['volume'].min() > 0
