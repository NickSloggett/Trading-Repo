"""
TimescaleDB Handler for OHLC Data Storage
Provides high-performance time-series data operations
"""

import os
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.pool import ThreadedConnectionPool
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class TimescaleHandler:
    """Handler for TimescaleDB operations"""
    
    def __init__(
        self,
        host: str = None,
        port: int = 5432,
        database: str = "trading_data",
        user: str = "trading_writer",
        password: str = None,
        min_connections: int = 1,
        max_connections: int = 10
    ):
        """Initialize TimescaleDB connection pool"""
        self.host = host or os.getenv('TIMESCALE_HOST', 'localhost')
        self.port = port
        self.database = database
        self.user = user
        self.password = password or os.getenv('TIMESCALE_PASSWORD', '')
        
        # Create connection pool
        self.pool = ThreadedConnectionPool(
            min_connections,
            max_connections,
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )
        
        logger.info(f"TimescaleDB connection pool initialized: {self.host}:{self.port}/{self.database}")
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool (context manager)"""
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)
    
    def insert_ohlc_data(
        self,
        data: pd.DataFrame,
        symbol: str,
        timeframe: str,
        data_source: str = None,
        batch_size: int = 1000
    ) -> int:
        """
        Insert OHLC data into TimescaleDB
        
        Args:
            data: DataFrame with columns [timestamp, open, high, low, close, volume]
            symbol: Trading symbol
            timeframe: Timeframe (1min, 5min, 1h, 1d, etc.)
            data_source: Data provider name
            batch_size: Number of records to insert per batch
            
        Returns:
            Number of records inserted
        """
        if data.empty:
            return 0
        
        # Prepare data
        data = data.copy()
        if 'timestamp' in data.columns:
            data['time'] = pd.to_datetime(data['timestamp'])
        elif 'time' not in data.columns:
            data['time'] = data.index
        
        required_cols = ['time', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_cols):
            raise ValueError(f"Data must contain columns: {required_cols}")
        
        # Add metadata
        data['symbol'] = symbol
        data['timeframe'] = timeframe
        if data_source:
            data['data_source'] = data_source
        
        # Optional columns
        optional_cols = ['trades', 'vwap']
        
        # Build column list
        cols = ['time', 'symbol', 'timeframe', 'open', 'high', 'low', 'close', 'volume']
        for col in optional_cols:
            if col in data.columns:
                cols.append(col)
        if data_source:
            cols.append('data_source')
        
        # Prepare values
        values = [tuple(row) for row in data[cols].values]
        
        # SQL query with ON CONFLICT for upserts
        placeholders = ', '.join(['%s'] * len(cols))
        cols_str = ', '.join(cols)
        update_cols = ', '.join([f"{col} = EXCLUDED.{col}" for col in cols if col not in ['time', 'symbol', 'timeframe']])
        
        query = f"""
        INSERT INTO ohlc_data ({cols_str})
        VALUES %s
        ON CONFLICT (time, symbol, timeframe)
        DO UPDATE SET {update_cols}
        """
        
        total_inserted = 0
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    # Insert in batches
                    for i in range(0, len(values), batch_size):
                        batch = values[i:i + batch_size]
                        execute_values(cur, query, batch)
                        total_inserted += len(batch)
                    
                    conn.commit()
                    logger.info(f"Inserted {total_inserted} records for {symbol} ({timeframe})")
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error inserting data: {e}")
                    raise
        
        return total_inserted
    
    def query_ohlc_data(
        self,
        symbol: str,
        timeframe: str,
        start_time: datetime = None,
        end_time: datetime = None,
        limit: int = None
    ) -> pd.DataFrame:
        """
        Query OHLC data from TimescaleDB
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            start_time: Start datetime
            end_time: End datetime
            limit: Max number of records
            
        Returns:
            DataFrame with OHLC data
        """
        conditions = ["symbol = %s", "timeframe = %s"]
        params = [symbol, timeframe]
        
        if start_time:
            conditions.append("time >= %s")
            params.append(start_time)
        
        if end_time:
            conditions.append("time <= %s")
            params.append(end_time)
        
        where_clause = " AND ".join(conditions)
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"""
        SELECT time, open, high, low, close, volume, trades, vwap
        FROM ohlc_data
        WHERE {where_clause}
        ORDER BY time ASC
        {limit_clause}
        """
        
        with self.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
        
        if not df.empty:
            df['time'] = pd.to_datetime(df['time'])
            df.set_index('time', inplace=True)
        
        return df
    
    def query_multi_symbol(
        self,
        symbols: List[str],
        timeframe: str,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> pd.DataFrame:
        """
        Query OHLC data for multiple symbols
        
        Returns DataFrame with multi-index (time, symbol)
        """
        conditions = ["symbol = ANY(%s)", "timeframe = %s"]
        params = [symbols, timeframe]
        
        if start_time:
            conditions.append("time >= %s")
            params.append(start_time)
        
        if end_time:
            conditions.append("time <= %s")
            params.append(end_time)
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
        SELECT time, symbol, open, high, low, close, volume
        FROM ohlc_data
        WHERE {where_clause}
        ORDER BY time ASC, symbol ASC
        """
        
        with self.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
        
        if not df.empty:
            df['time'] = pd.to_datetime(df['time'])
            df = df.pivot_table(
                index='time',
                columns='symbol',
                values=['open', 'high', 'low', 'close', 'volume']
            )
        
        return df
    
    def get_latest_timestamp(self, symbol: str, timeframe: str) -> Optional[datetime]:
        """Get the latest timestamp for a symbol/timeframe"""
        query = """
        SELECT MAX(time) as latest
        FROM ohlc_data
        WHERE symbol = %s AND timeframe = %s
        """
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (symbol, timeframe))
                result = cur.fetchone()
                return result[0] if result and result[0] else None
    
    def detect_gaps(
        self,
        symbol: str,
        timeframe: str,
        start_time: datetime,
        end_time: datetime,
        expected_interval: timedelta = None
    ) -> List[Tuple[datetime, datetime]]:
        """
        Detect gaps in time-series data
        
        Returns list of (gap_start, gap_end) tuples
        """
        if not expected_interval:
            # Default intervals based on timeframe
            interval_map = {
                '1min': timedelta(minutes=1),
                '5min': timedelta(minutes=5),
                '15min': timedelta(minutes=15),
                '1h': timedelta(hours=1),
                '4h': timedelta(hours=4),
                '1d': timedelta(days=1),
            }
            expected_interval = interval_map.get(timeframe, timedelta(days=1))
        
        query = """
        SELECT gap_start, gap_end, gap_duration
        FROM check_data_gaps(%s, %s, %s, %s)
        """
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (symbol, timeframe, start_time, end_time))
                gaps = [(row[0], row[1]) for row in cur.fetchall()]
        
        return gaps
    
    def get_data_quality_score(self, symbol: str, timeframe: str, days: int = 30) -> Dict[str, Any]:
        """
        Calculate data quality metrics
        
        Returns dict with metrics: completeness, gaps, outliers, etc.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get data
        df = self.query_ohlc_data(symbol, timeframe, start_date, end_date)
        
        if df.empty:
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'quality_score': 0.0,
                'total_records': 0,
                'issues': ['No data available']
            }
        
        issues = []
        total_records = len(df)
        
        # Check for missing values
        missing = df.isnull().sum().sum()
        if missing > 0:
            issues.append(f"{missing} missing values")
        
        # Check for zero volume
        zero_volume = (df['volume'] == 0).sum()
        if zero_volume > 0:
            issues.append(f"{zero_volume} bars with zero volume")
        
        # Check for outliers (price changes > 50%)
        price_changes = df['close'].pct_change().abs()
        outliers = (price_changes > 0.5).sum()
        if outliers > 0:
            issues.append(f"{outliers} potential outliers (>50% price change)")
        
        # Calculate completeness score
        completeness = 1.0 - (missing / (total_records * len(df.columns)))
        
        # Calculate overall quality score (0-100)
        quality_score = max(0, min(100, completeness * 100 - len(issues) * 5))
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'quality_score': round(quality_score, 2),
            'total_records': total_records,
            'missing_values': missing,
            'zero_volume_bars': zero_volume,
            'outliers': outliers,
            'issues': issues
        }
    
    def add_symbol_metadata(self, symbol: str, metadata: Dict[str, Any]) -> None:
        """Add or update symbol metadata"""
        query = """
        INSERT INTO symbols (symbol, name, exchange, asset_type, sector, industry, currency, active, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (symbol)
        DO UPDATE SET
            name = EXCLUDED.name,
            exchange = EXCLUDED.exchange,
            asset_type = EXCLUDED.asset_type,
            sector = EXCLUDED.sector,
            industry = EXCLUDED.industry,
            currency = EXCLUDED.currency,
            active = EXCLUDED.active,
            metadata = EXCLUDED.metadata,
            updated_at = NOW()
        """
        
        import json
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    symbol,
                    metadata.get('name'),
                    metadata.get('exchange'),
                    metadata.get('asset_type'),
                    metadata.get('sector'),
                    metadata.get('industry'),
                    metadata.get('currency', 'USD'),
                    metadata.get('active', True),
                    json.dumps(metadata.get('extra', {}))
                ))
                conn.commit()
        
        logger.info(f"Added/updated metadata for {symbol}")
    
    def log_ingestion(
        self,
        job_id: str,
        symbol: str,
        timeframe: str,
        provider: str,
        records_inserted: int,
        status: str = 'success',
        error_message: str = None,
        duration_seconds: int = None
    ) -> None:
        """Log data ingestion job"""
        query = """
        INSERT INTO ingestion_logs 
        (job_id, symbol, timeframe, provider, records_inserted, status, error_message, duration_seconds)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    job_id, symbol, timeframe, provider,
                    records_inserted, status, error_message, duration_seconds
                ))
                conn.commit()
    
    def get_symbols_list(
        self,
        asset_type: str = None,
        exchange: str = None,
        active_only: bool = True
    ) -> List[str]:
        """Get list of symbols from metadata"""
        conditions = []
        params = []
        
        if asset_type:
            conditions.append("asset_type = %s")
            params.append(asset_type)
        
        if exchange:
            conditions.append("exchange = %s")
            params.append(exchange)
        
        if active_only:
            conditions.append("active = TRUE")
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        query = f"""
        SELECT symbol
        FROM symbols
        {where_clause}
        ORDER BY symbol
        """
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return [row[0] for row in cur.fetchall()]
    
    def close(self):
        """Close connection pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("TimescaleDB connection pool closed")


# Singleton instance
_handler = None

def get_timescale_handler(**kwargs) -> TimescaleHandler:
    """Get singleton TimescaleHandler instance"""
    global _handler
    if _handler is None:
        _handler = TimescaleHandler(**kwargs)
    return _handler
