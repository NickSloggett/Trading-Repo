"""
Base Provider Interface for Data Ingestion
All data providers must implement this interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
from dataclasses import dataclass
from enum import Enum


class TimeFrame(Enum):
    """Supported timeframes"""
    TICK = "tick"
    MIN_1 = "1min"
    MIN_5 = "5min"
    MIN_15 = "15min"
    MIN_30 = "30min"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    DAY_1 = "1d"
    WEEK_1 = "1w"
    MONTH_1 = "1mo"


class AssetType(Enum):
    """Asset types"""
    STOCK = "stock"
    ETF = "etf"
    CRYPTO = "crypto"
    FOREX = "forex"
    FUTURES = "futures"
    OPTIONS = "options"
    INDEX = "index"


@dataclass
class ProviderCapabilities:
    """Describes what a provider can do"""
    supported_timeframes: List[TimeFrame]
    supported_asset_types: List[AssetType]
    has_real_time: bool = False
    has_historical: bool = True
    max_bars_per_request: int = 5000
    rate_limit_per_minute: int = 60
    requires_auth: bool = False
    cost: str = "free"  # free, paid, freemium


@dataclass
class OHLCData:
    """Standardized OHLC data structure"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    trades: Optional[int] = None
    vwap: Optional[float] = None


class BaseDataProvider(ABC):
    """
    Base class for all data providers
    Provides a consistent interface for different data sources
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize provider
        
        Args:
            api_key: API key if required
            **kwargs: Provider-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs
        self._capabilities = self._get_capabilities()
    
    @abstractmethod
    def _get_capabilities(self) -> ProviderCapabilities:
        """Return provider capabilities"""
        pass
    
    @property
    def capabilities(self) -> ProviderCapabilities:
        """Get provider capabilities"""
        return self._capabilities
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name"""
        pass
    
    @abstractmethod
    def fetch_historical(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: TimeFrame = TimeFrame.DAY_1,
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data
        
        Args:
            symbol: Trading symbol
            start_date: Start datetime
            end_date: End datetime
            timeframe: Data timeframe
            **kwargs: Provider-specific options
            
        Returns:
            DataFrame with columns: [timestamp, open, high, low, close, volume]
        """
        pass
    
    def fetch_latest(
        self,
        symbol: str,
        timeframe: TimeFrame = TimeFrame.DAY_1,
        bars: int = 1
    ) -> pd.DataFrame:
        """
        Fetch latest bars
        
        Args:
            symbol: Trading symbol
            timeframe: Data timeframe
            bars: Number of bars to fetch
            
        Returns:
            DataFrame with latest bars
        """
        end_date = datetime.now()
        start_date = self._calculate_start_date(end_date, timeframe, bars)
        return self.fetch_historical(symbol, start_date, end_date, timeframe)
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if symbol exists and is tradable
        
        Args:
            symbol: Trading symbol
            
        Returns:
            True if valid, False otherwise
        """
        try:
            data = self.fetch_latest(symbol, bars=1)
            return not data.empty
        except Exception:
            return False
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get symbol metadata
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dict with symbol information (name, exchange, asset_type, etc.)
        """
        return None
    
    def search_symbols(self, query: str, asset_type: Optional[AssetType] = None) -> List[str]:
        """
        Search for symbols
        
        Args:
            query: Search query
            asset_type: Filter by asset type
            
        Returns:
            List of matching symbols
        """
        return []
    
    @staticmethod
    def _calculate_start_date(end_date: datetime, timeframe: TimeFrame, bars: int) -> datetime:
        """Calculate start date based on number of bars needed"""
        from datetime import timedelta
        
        timeframe_deltas = {
            TimeFrame.MIN_1: timedelta(minutes=1),
            TimeFrame.MIN_5: timedelta(minutes=5),
            TimeFrame.MIN_15: timedelta(minutes=15),
            TimeFrame.MIN_30: timedelta(minutes=30),
            TimeFrame.HOUR_1: timedelta(hours=1),
            TimeFrame.HOUR_4: timedelta(hours=4),
            TimeFrame.DAY_1: timedelta(days=1),
            TimeFrame.WEEK_1: timedelta(weeks=1),
            TimeFrame.MONTH_1: timedelta(days=30),
        }
        
        delta = timeframe_deltas.get(timeframe, timedelta(days=1))
        
        # Add buffer for weekends/holidays
        buffer_multiplier = 1.5 if timeframe in [TimeFrame.DAY_1, TimeFrame.WEEK_1] else 1.2
        
        return end_date - (delta * bars * buffer_multiplier)
    
    @staticmethod
    def standardize_dataframe(df: pd.DataFrame, required_cols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Standardize DataFrame format
        
        Ensures consistent column names and data types
        """
        if df.empty:
            return df
        
        # Standardize column names (lowercase)
        df.columns = df.columns.str.lower()
        
        # Map common variations
        column_mapping = {
            'datetime': 'timestamp',
            'date': 'timestamp',
            'time': 'timestamp',
            'o': 'open',
            'h': 'high',
            'l': 'low',
            'c': 'close',
            'v': 'volume',
            'vol': 'volume',
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        elif df.index.name in ['datetime', 'date', 'time'] or isinstance(df.index, pd.DatetimeIndex):
            df['timestamp'] = pd.to_datetime(df.index)
            df.reset_index(drop=True, inplace=True)
        
        # Ensure numeric types
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Required columns check
        if required_cols is None:
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Sort by timestamp
        df.sort_values('timestamp', inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        # Remove duplicates
        df.drop_duplicates(subset=['timestamp'], keep='last', inplace=True)
        
        return df
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"




