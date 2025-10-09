# Data Management System

Enterprise-grade data management for storing and querying large amounts of OHLC (Open, High, Low, Close) data from multiple tickers and timeframes.

## Overview

This system provides:
- **TimescaleDB** integration for time-series data storage
- **Parquet** file storage for historical data archives
- **Data ingestion** pipelines from multiple sources
- **Efficient querying** with indexing and compression
- **Data validation** and quality checks
- **Backup and archival** strategies

## Architecture

```
data-management/
├── database/
│   ├── schema.sql              # TimescaleDB schema with hypertables
│   ├── migrations/             # Database migrations
│   └── docker-compose.yml      # Database setup
├── ingestion/
│   ├── providers/              # Data provider integrations
│   │   ├── yfinance_provider.py
│   │   ├── alpaca_provider.py
│   │   ├── polygon_provider.py
│   │   ├── ib_provider.py      # Interactive Brokers
│   │   └── coinbase_provider.py
│   ├── pipeline.py             # Main ingestion pipeline
│   └── scheduler.py            # Automated data updates
├── storage/
│   ├── timescale_handler.py    # TimescaleDB operations
│   ├── parquet_handler.py      # Parquet file operations
│   └── cache_manager.py        # Redis caching layer
├── query/
│   ├── api.py                  # Data query API
│   └── aggregations.py         # Custom aggregations
├── validation/
│   ├── data_quality.py         # Data quality checks
│   └── integrity.py            # Data integrity validation
└── config/
    ├── providers.yaml          # Provider configurations
    └── symbols.yaml            # Symbol lists by category
```

## Features

### 1. TimescaleDB Storage
- Hypertables for efficient time-series storage
- Automatic data compression and retention policies
- Continuous aggregates for fast queries
- Support for multiple timeframes (1min, 5min, 1h, 1d, etc.)

### 2. Multiple Data Providers
- **yfinance**: Free historical data
- **Alpaca**: Real-time and historical market data
- **Polygon.io**: Professional-grade market data
- **Interactive Brokers**: Direct broker integration
- **Coinbase**: Cryptocurrency data
- Custom provider interface for extensions

### 3. Data Ingestion Pipeline
- Concurrent downloads for multiple symbols
- Automatic gap detection and filling
- Deduplication and data cleaning
- Error handling and retry logic
- Progress tracking and logging

### 4. Query Optimization
- Indexed queries for fast retrieval
- Pre-aggregated views for common queries
- Redis caching for frequently accessed data
- Vectorized operations with Pandas/NumPy

### 5. Data Quality
- Missing data detection
- Outlier detection and handling
- Split/dividend adjustments
- Corporate action handling

## Quick Start

### 1. Setup Database

```bash
cd data-management/database
docker-compose up -d
```

### 2. Initialize Schema

```bash
python -m data_management.database.init_db
```

### 3. Ingest Historical Data

```bash
# Ingest single symbol
python -m data_management.ingestion.pipeline --symbol AAPL --start 2020-01-01

# Ingest multiple symbols from list
python -m data_management.ingestion.pipeline --symbols-file config/symbols.yaml --provider alpaca

# Bulk ingest S&P 500
python -m data_management.ingestion.pipeline --preset sp500 --timeframe 1d
```

### 4. Query Data

```python
from data_management.query import DataAPI

api = DataAPI()

# Get OHLCV data
df = api.get_ohlc(
    symbol='AAPL',
    start='2023-01-01',
    end='2023-12-31',
    timeframe='1d'
)

# Get multiple symbols
df = api.get_multi_symbol(
    symbols=['AAPL', 'GOOGL', 'MSFT'],
    start='2023-01-01',
    timeframe='1h'
)

# Get with indicators pre-computed
df = api.get_ohlc_with_indicators(
    symbol='AAPL',
    indicators=['SMA_20', 'RSI_14', 'MACD']
)
```

## Database Schema

### Main OHLC Table

```sql
CREATE TABLE ohlc_data (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    open DECIMAL(18,8) NOT NULL,
    high DECIMAL(18,8) NOT NULL,
    low DECIMAL(18,8) NOT NULL,
    close DECIMAL(18,8) NOT NULL,
    volume BIGINT NOT NULL,
    trades INTEGER,
    vwap DECIMAL(18,8),
    PRIMARY KEY (time, symbol, timeframe)
);

-- Convert to hypertable
SELECT create_hypertable('ohlc_data', 'time');

-- Add compression
ALTER TABLE ohlc_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol,timeframe'
);

-- Add compression policy (compress data older than 7 days)
SELECT add_compression_policy('ohlc_data', INTERVAL '7 days');
```

## Storage Estimates

For reference, approximate storage requirements:

| Data | Symbols | Timeframe | Duration | Estimated Size |
|------|---------|-----------|----------|----------------|
| Stocks | 100 | 1 day | 10 years | ~50 MB |
| Stocks | 500 | 1 day | 10 years | ~250 MB |
| Stocks | 100 | 1 min | 1 year | ~5 GB |
| Crypto | 50 | 1 min | 2 years | ~2 GB |

With compression, expect 5-10x reduction in storage size.

## Performance

Typical query performance on modern hardware:

- Single symbol, 1 year daily data: < 10ms
- Single symbol, 1 year minute data: < 100ms
- 100 symbols, 1 year daily data: < 200ms
- Aggregations on 1M+ rows: < 500ms

## Best Practices

1. **Use appropriate timeframes**: Store base timeframe (1min) and aggregate up
2. **Implement retention policies**: Archive old data to Parquet
3. **Monitor data quality**: Run validation checks regularly
4. **Cache frequently accessed data**: Use Redis for hot data
5. **Batch operations**: Bulk insert/update for better performance
6. **Index strategically**: Balance query speed vs. write performance

## Advanced Features

### Continuous Aggregates

Pre-compute common aggregations:

```sql
CREATE MATERIALIZED VIEW ohlc_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS day,
    symbol,
    first(open, time) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, time) AS close,
    sum(volume) AS volume
FROM ohlc_1min
GROUP BY day, symbol;
```

### Real-time Data Streaming

```python
from data_management.streaming import StreamHandler

handler = StreamHandler()

@handler.on_data
def process_tick(tick):
    # Process real-time tick data
    save_to_database(tick)
    update_indicators(tick)

handler.subscribe(['AAPL', 'GOOGL', 'MSFT'])
handler.start()
```

## Monitoring

Dashboard metrics:
- Data ingestion rate
- Storage utilization
- Query performance
- Data quality scores
- Provider uptime

Access Grafana dashboard: http://localhost:3000

## Troubleshooting

Common issues and solutions:

1. **Slow queries**: Check indexes, use continuous aggregates
2. **Missing data**: Run gap detection and backfill
3. **Storage growth**: Enable compression, implement retention
4. **Data quality issues**: Run validation scripts

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines on adding new data providers or features.




