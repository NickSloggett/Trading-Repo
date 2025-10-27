"""
Simple performance analysis utilities for trading data.

Provides basic risk and return metrics calculations.
"""

import logging
from typing import Dict, Any
from datetime import datetime

import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def compute_metrics(data: pd.DataFrame, risk_free_rate: float = 0.02) -> Dict[str, float]:
    """
    Compute basic performance metrics for a price series.

    Args:
        data: DataFrame with 'Close' column containing price data
        risk_free_rate: Annual risk-free rate (default: 2%)

    Returns:
        Dictionary containing performance metrics
    """
    if data.empty or 'Close' not in data.columns:
        logger.error("Invalid data: DataFrame is empty or missing 'Close' column")
        return {}

    try:
        # Create a copy to avoid modifying original data
        df = data.copy()

        # Calculate daily returns (avoid modifying in-place)
        returns = df['Close'].pct_change().dropna()

        if len(returns) == 0:
            logger.warning("Insufficient data for metrics calculation")
            return {}

        # Core metrics
        total_return = (df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1
        annualized_return = (1 + total_return) ** (252 / len(df)) - 1
        volatility = returns.std() * np.sqrt(252)  # Annualized volatility

        # Sharpe ratio with error handling
        if volatility > 0:
            sharpe_ratio = (annualized_return - risk_free_rate) / volatility
        else:
            sharpe_ratio = 0.0

        # Additional metrics
        max_drawdown = compute_max_drawdown(df['Close'])
        sortino_ratio = compute_sortino_ratio(returns, risk_free_rate)

        metrics = {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'sortino_ratio': sortino_ratio,
            'data_points': len(df),
            'start_date': df.index[0].strftime('%Y-%m-%d') if isinstance(df.index[0], pd.Timestamp) else str(df.index[0]),
            'end_date': df.index[-1].strftime('%Y-%m-%d') if isinstance(df.index[-1], pd.Timestamp) else str(df.index[-1])
        }

        return metrics

    except Exception as e:
        logger.error(f"Error computing metrics: {e}")
        return {}


def compute_max_drawdown(prices: pd.Series) -> float:
    """
    Calculate maximum drawdown from peak to trough.

    Args:
        prices: Series of prices

    Returns:
        Maximum drawdown as a decimal
    """
    try:
        cumulative = (1 + prices.pct_change().fillna(0)).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return abs(drawdown.min())
    except Exception:
        return 0.0


def compute_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sortino ratio (downside deviation instead of total volatility).

    Args:
        returns: Series of daily returns
        risk_free_rate: Annual risk-free rate

    Returns:
        Sortino ratio
    """
    try:
        # Annualize risk-free rate to daily
        daily_risk_free = risk_free_rate / 252

        # Calculate downside deviation (only negative returns)
        excess_returns = returns - daily_risk_free
        downside_returns = excess_returns[excess_returns < 0]

        if len(downside_returns) == 0:
            return 0.0

        downside_deviation = downside_returns.std() * np.sqrt(252)  # Annualize

        # Average excess return
        avg_excess_return = excess_returns.mean() * 252  # Annualize

        if downside_deviation > 0:
            return avg_excess_return / downside_deviation
        else:
            return 0.0

    except Exception:
        return 0.0


def analyze_symbol(symbol: str, start_date: str = '2020-01-01', end_date: str = None) -> Dict[str, Any]:
    """
    Download data and compute comprehensive analysis for a symbol.

    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        start_date: Start date string
        end_date: End date string (defaults to today)

    Returns:
        Dictionary with data and analysis results
    """
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')

    try:
        logger.info(f"Analyzing {symbol} from {start_date} to {end_date}")

        # Download data with proper error handling
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)

        if data.empty:
            logger.warning(f"No data found for {symbol}")
            return {'symbol': symbol, 'error': 'No data available'}

        # Handle MultiIndex columns from newer yfinance versions
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Ensure we have Close column
        if 'Close' not in data.columns:
            logger.error(f"No Close column in data for {symbol}")
            return {'symbol': symbol, 'error': 'Missing Close data'}

        # Compute metrics
        metrics = compute_metrics(data[['Close']])

        return {
            'symbol': symbol,
            'data': data,
            'metrics': metrics,
            'analysis_date': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        return {'symbol': symbol, 'error': str(e)}


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Example usage
    symbol = 'AAPL'
    result = analyze_symbol(symbol)

    if 'error' in result:
        print(f"Error analyzing {symbol}: {result['error']}")
    else:
        print(f"\nAnalysis for {symbol}:")
        print("=" * 50)
        for key, value in result['metrics'].items():
            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")

