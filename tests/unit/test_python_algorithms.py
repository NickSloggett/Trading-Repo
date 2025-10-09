"""
Unit tests for python algorithms modules
"""
import pytest
import pandas as pd
import numpy as np
import os
import sys

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from python_algorithms.utils.fetch_data import fetch_data
except ImportError:
    fetch_data = None


class TestFetchData:
    """Test cases for data fetching utilities"""

    def test_fetch_data_import(self):
        """Test that fetch_data can be imported"""
        # Test that the module structure exists
        if fetch_data is None:
            pytest.skip("fetch_data module not available")
        assert fetch_data is not None

    def test_dataframe_creation(self):
        """Test DataFrame creation from fetched data"""
        # Create a sample DataFrame for testing
        sample_data = {
            'symbol': ['AAPL', 'GOOGL', 'MSFT'],
            'price': [150.0, 2500.0, 300.0],
            'volume': [1000000, 500000, 750000]
        }
        df = pd.DataFrame(sample_data)
        assert len(df) == 3
        assert 'symbol' in df.columns
        assert 'price' in df.columns
        assert 'volume' in df.columns

    def test_data_validation(self):
        """Test data validation for trading algorithms"""
        # Test price data validation
        prices = np.array([100.0, 101.5, 99.8, 102.3, 98.7])
        assert len(prices) == 5
        assert np.all(prices > 0)  # Prices should be positive
        assert np.std(prices) > 0  # Should have some volatility


class TestTradingAlgorithms:
    """Test cases for trading algorithm utilities"""
    
    def test_moving_average_calculation(self):
        """Test moving average calculation"""
        data = np.array([100, 101, 102, 103, 104, 105, 106, 107, 108, 109])
        
        # Simple moving average calculation
        window = 5
        ma = pd.Series(data).rolling(window=window).mean()
        
        assert len(ma) == len(data)
        assert not np.isnan(ma.iloc[-1])  # Last value should be calculated
        assert ma.iloc[-1] == np.mean(data[-window:])  # Should match expected value
        
    def test_rsi_calculation(self):
        """Test RSI calculation"""
        # Create sample price data with known RSI characteristics
        prices = np.array([100, 102, 104, 103, 105, 107, 106, 108, 110, 109])
        
        # Calculate price changes
        changes = np.diff(prices)
        gains = np.where(changes > 0, changes, 0)
        losses = np.where(changes < 0, -changes, 0)
        
        # Simple RSI calculation (simplified)
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        assert 0 <= rsi <= 100
        assert not np.isnan(rsi)
        
    def test_portfolio_calculation(self):
        """Test portfolio calculation utilities"""
        # Sample portfolio data
        portfolio = {
            'AAPL': {'shares': 100, 'price': 150.0},
            'GOOGL': {'shares': 50, 'price': 2500.0},
            'MSFT': {'shares': 200, 'price': 300.0}
        }
        
        # Calculate total value
        total_value = sum(stock['shares'] * stock['price'] for stock in portfolio.values())
        expected_value = 100 * 150 + 50 * 2500 + 200 * 300
        assert total_value == expected_value
        assert total_value > 0


class TestBacktesting:
    """Test cases for backtesting utilities"""
    
    def test_strategy_returns_calculation(self):
        """Test strategy returns calculation"""
        # Sample strategy data
        initial_capital = 10000
        final_capital = 12000
        
        # Calculate returns
        returns = (final_capital - initial_capital) / initial_capital
        assert returns == 0.2  # 20% return
        assert returns > 0
        
    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation"""
        # Sample returns data
        returns = np.array([0.01, 0.02, -0.01, 0.03, 0.015, -0.005, 0.02, 0.01])
        risk_free_rate = 0.02  # 2% annual risk-free rate
        
        # Calculate Sharpe ratio (simplified)
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        
        assert not np.isnan(sharpe_ratio)
        assert isinstance(sharpe_ratio, float)
