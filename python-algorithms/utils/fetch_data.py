"""
Data fetching utilities for trading algorithms.

Provides functions to download and save historical market data from various sources.
"""

import logging
from pathlib import Path
from typing import Optional, Union
from datetime import datetime

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def fetch_and_save(
    symbol: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    save_path: Union[str, Path] = 'data',
    interval: str = '1d'
) -> Optional[pd.DataFrame]:
    """
    Fetch historical data for a symbol and save to CSV.

    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        start_date: Start date (str or datetime)
        end_date: End date (str or datetime)
        save_path: Directory to save CSV
        interval: Data interval ('1d', '1h', '1m', etc.)

    Returns:
        DataFrame with historical data, or None if failed
    """
    try:
        # Convert to Path and create directory
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)

        # Download data with proper error handling
        logger.info(f"Fetching data for {symbol} from {start_date} to {end_date}")
        data = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False,
            auto_adjust=True
        )

        if data.empty:
            logger.warning(f"No data found for {symbol}")
            return None

        # Handle MultiIndex columns from newer yfinance versions
        if isinstance(data.columns, pd.MultiIndex):
            # Flatten MultiIndex columns by taking the first level (price type)
            data.columns = data.columns.get_level_values(0)

        # Validate required columns exist
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return None

        # Save to CSV
        start_str = start_date if isinstance(start_date, str) else start_date.strftime('%Y%m%d')
        end_str = end_date if isinstance(end_date, str) else end_date.strftime('%Y%m%d')
        filename = f"{symbol}_{start_str}_to_{end_str}_{interval}.csv"
        filepath = save_path / filename

        data.to_csv(filepath)
        logger.info(f"Data saved to {filepath} (shape: {data.shape})")

        return data

    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return None


def fetch_multiple_symbols(
    symbols: list[str],
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    save_path: Union[str, Path] = 'data',
    interval: str = '1d'
) -> dict[str, pd.DataFrame]:
    """
    Fetch historical data for multiple symbols efficiently.

    Args:
        symbols: List of stock symbols
        start_date: Start date (str or datetime)
        end_date: End date (str or datetime)
        save_path: Directory to save CSV files
        interval: Data interval

    Returns:
        Dict mapping symbols to DataFrames
    """
    results = {}

    for symbol in symbols:
        data = fetch_and_save(symbol, start_date, end_date, save_path, interval)
        if data is not None:
            results[symbol] = data

    logger.info(f"Successfully fetched data for {len(results)}/{len(symbols)} symbols")
    return results


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Example usage
    symbol = 'AAPL'
    start = '2020-01-01'
    end = datetime.now().strftime('%Y-%m-%d')

    data = fetch_and_save(symbol, start, end)
    if data is not None:
        print(f"Successfully fetched {len(data)} records for {symbol}")
    else:
        print(f"Failed to fetch data for {symbol}")

