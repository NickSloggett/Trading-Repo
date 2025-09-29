"""
Yahoo Finance Data Provider
Free historical data provider using yfinance library
"""

import yfinance as yf
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
import logging

from .base_provider import (
    BaseDataProvider, TimeFrame, AssetType, ProviderCapabilities
)

logger = logging.getLogger(__name__)


class YFinanceProvider(BaseDataProvider):
    """Yahoo Finance data provider - free historical data"""
    
    TIMEFRAME_MAP = {
        TimeFrame.MIN_1: "1m",
        TimeFrame.MIN_5: "5m",
        TimeFrame.MIN_15: "15m",
        TimeFrame.MIN_30: "30m",
        TimeFrame.HOUR_1: "1h",
        TimeFrame.DAY_1: "1d",
        TimeFrame.WEEK_1: "1wk",
        TimeFrame.MONTH_1: "1mo",
    }
    
    @property
    def name(self) -> str:
        return "Yahoo Finance"
    
    def _get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supported_timeframes=[
                TimeFrame.MIN_1, TimeFrame.MIN_5, TimeFrame.MIN_15,
                TimeFrame.MIN_30, TimeFrame.HOUR_1, TimeFrame.DAY_1,
                TimeFrame.WEEK_1, TimeFrame.MONTH_1
            ],
            supported_asset_types=[
                AssetType.STOCK, AssetType.ETF, AssetType.CRYPTO,
                AssetType.FOREX, AssetType.FUTURES, AssetType.INDEX
            ],
            has_real_time=False,
            has_historical=True,
            max_bars_per_request=10000,
            rate_limit_per_minute=200,
            requires_auth=False,
            cost="free"
        )
    
    def fetch_historical(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: TimeFrame = TimeFrame.DAY_1,
        **kwargs
    ) -> pd.DataFrame:
        """Fetch historical data from Yahoo Finance"""
        try:
            # Map timeframe
            interval = self.TIMEFRAME_MAP.get(timeframe)
            if not interval:
                raise ValueError(f"Unsupported timeframe: {timeframe}")
            
            # Adjust symbol for crypto (add -USD suffix if not present)
            if '-USD' not in symbol and 'USDT' not in symbol and kwargs.get('asset_type') == AssetType.CRYPTO:
                symbol = f"{symbol}-USD"
            
            # Download data
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval,
                auto_adjust=kwargs.get('auto_adjust', True),
                actions=False
            )
            
            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return pd.DataFrame()
            
            # Standardize format
            df.reset_index(inplace=True)
            df.rename(columns={
                'Date': 'timestamp',
                'Datetime': 'timestamp',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }, inplace=True)
            
            # Select required columns
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            df = df[required_cols]
            
            # Standardize
            df = self.standardize_dataframe(df)
            
            logger.info(f"Fetched {len(df)} bars for {symbol} from Yahoo Finance")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data from Yahoo Finance for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get symbol information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', '')),
                'exchange': info.get('exchange', ''),
                'asset_type': self._determine_asset_type(info),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'currency': info.get('currency', 'USD'),
                'country': info.get('country'),
                'market_cap': info.get('marketCap'),
                'description': info.get('longBusinessSummary', ''),
                'website': info.get('website', ''),
            }
        except Exception as e:
            logger.error(f"Error getting info for {symbol}: {e}")
            return None
    
    def search_symbols(self, query: str, asset_type: Optional[AssetType] = None) -> List[str]:
        """
        Search for symbols
        Note: Yahoo Finance doesn't have a direct search API, so this is limited
        """
        # This is a basic implementation - for production, use a dedicated search API
        results = []
        
        try:
            # Try common variations
            variations = [
                query.upper(),
                f"{query.upper()}.US",
                f"{query.upper()}-USD",  # Crypto
            ]
            
            for symbol in variations:
                if self.validate_symbol(symbol):
                    results.append(symbol)
            
        except Exception as e:
            logger.error(f"Error searching for {query}: {e}")
        
        return results
    
    def fetch_multiple_symbols(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        timeframe: TimeFrame = TimeFrame.DAY_1
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple symbols efficiently
        
        Returns dict of {symbol: dataframe}
        """
        interval = self.TIMEFRAME_MAP.get(timeframe, "1d")
        
        try:
            # Download all at once (more efficient)
            data = yf.download(
                symbols,
                start=start_date,
                end=end_date,
                interval=interval,
                group_by='ticker',
                auto_adjust=True,
                threads=True
            )
            
            result = {}
            
            if len(symbols) == 1:
                # Single symbol returns different structure
                symbol = symbols[0]
                df = data.reset_index()
                df = self._format_dataframe(df)
                result[symbol] = df
            else:
                # Multiple symbols
                for symbol in symbols:
                    try:
                        df = data[symbol].reset_index()
                        df = self._format_dataframe(df)
                        if not df.empty:
                            result[symbol] = df
                    except Exception as e:
                        logger.error(f"Error processing {symbol}: {e}")
                        continue
            
            logger.info(f"Fetched data for {len(result)} symbols")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching multiple symbols: {e}")
            return {}
    
    def _format_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Format DataFrame from yfinance output"""
        if df.empty:
            return df
        
        df.rename(columns={
            'Date': 'timestamp',
            'Datetime': 'timestamp',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)
        
        required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        available_cols = [col for col in required_cols if col in df.columns]
        df = df[available_cols]
        
        return self.standardize_dataframe(df)
    
    @staticmethod
    def _determine_asset_type(info: Dict) -> str:
        """Determine asset type from ticker info"""
        quote_type = info.get('quoteType', '').lower()
        
        type_mapping = {
            'equity': 'stock',
            'etf': 'etf',
            'cryptocurrency': 'crypto',
            'currency': 'forex',
            'future': 'futures',
            'index': 'index',
        }
        
        return type_mapping.get(quote_type, 'stock')
    
    def get_market_status(self, symbol: str) -> Dict[str, Any]:
        """Get current market status for symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'market_state': info.get('marketState', 'UNKNOWN'),
                'pre_market_price': info.get('preMarketPrice'),
                'regular_market_price': info.get('regularMarketPrice'),
                'post_market_price': info.get('postMarketPrice'),
                'last_update': datetime.now(),
            }
        except Exception as e:
            logger.error(f"Error getting market status for {symbol}: {e}")
            return {}
