-- TimescaleDB Schema for Trading Data
-- Requires TimescaleDB extension

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Main OHLC data table
CREATE TABLE IF NOT EXISTS ohlc_data (
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
    data_source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (time, symbol, timeframe)
);

-- Convert to hypertable (must be done after table creation)
SELECT create_hypertable('ohlc_data', 'time', if_not_exists => TRUE);

-- Add compression policy
ALTER TABLE ohlc_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol,timeframe',
    timescaledb.compress_orderby = 'time DESC'
);

-- Compress data older than 7 days
SELECT add_compression_policy('ohlc_data', INTERVAL '7 days', if_not_exists => TRUE);

-- Retention policy: Drop data older than 10 years
SELECT add_retention_policy('ohlc_data', INTERVAL '10 years', if_not_exists => TRUE);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_ohlc_symbol ON ohlc_data (symbol, time DESC);
CREATE INDEX IF NOT EXISTS idx_ohlc_timeframe ON ohlc_data (timeframe, time DESC);
CREATE INDEX IF NOT EXISTS idx_ohlc_symbol_timeframe ON ohlc_data (symbol, timeframe, time DESC);

-- Symbols metadata table
CREATE TABLE IF NOT EXISTS symbols (
    symbol VARCHAR(20) PRIMARY KEY,
    name VARCHAR(200),
    exchange VARCHAR(50),
    asset_type VARCHAR(20), -- stock, etf, crypto, forex, option, future
    sector VARCHAR(100),
    industry VARCHAR(100),
    currency VARCHAR(10) DEFAULT 'USD',
    active BOOLEAN DEFAULT TRUE,
    listed_date DATE,
    delisted_date DATE,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_symbols_exchange ON symbols (exchange);
CREATE INDEX IF NOT EXISTS idx_symbols_type ON symbols (asset_type);
CREATE INDEX IF NOT EXISTS idx_symbols_sector ON symbols (sector);

-- Data quality tracking
CREATE TABLE IF NOT EXISTS data_quality (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    check_date DATE NOT NULL,
    total_records BIGINT,
    missing_records INTEGER,
    duplicate_records INTEGER,
    outliers_detected INTEGER,
    quality_score DECIMAL(5,2),
    issues JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(symbol, timeframe, check_date)
);

CREATE INDEX IF NOT EXISTS idx_quality_symbol ON data_quality (symbol, check_date);

-- Ingestion logs
CREATE TABLE IF NOT EXISTS ingestion_logs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL,
    symbol VARCHAR(20),
    timeframe VARCHAR(10),
    provider VARCHAR(50),
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    records_inserted INTEGER,
    records_updated INTEGER,
    status VARCHAR(20), -- success, failed, partial
    error_message TEXT,
    duration_seconds INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ingestion_job ON ingestion_logs (job_id);
CREATE INDEX IF NOT EXISTS idx_ingestion_symbol ON ingestion_logs (symbol, created_at DESC);

-- Continuous aggregate: Daily OHLC from minute data
CREATE MATERIALIZED VIEW IF NOT EXISTS ohlc_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS day,
    symbol,
    first(open, time) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, time) AS close,
    sum(volume) AS volume,
    sum(trades) AS trades,
    avg(vwap) AS vwap
FROM ohlc_data
WHERE timeframe = '1min'
GROUP BY day, symbol
WITH NO DATA;

-- Refresh policy for continuous aggregate
SELECT add_continuous_aggregate_policy('ohlc_daily',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- Continuous aggregate: Hourly OHLC from minute data
CREATE MATERIALIZED VIEW IF NOT EXISTS ohlc_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS hour,
    symbol,
    first(open, time) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, time) AS close,
    sum(volume) AS volume,
    sum(trades) AS trades,
    avg(vwap) AS vwap
FROM ohlc_data
WHERE timeframe = '1min'
GROUP BY hour, symbol
WITH NO DATA;

-- Refresh policy for hourly aggregate
SELECT add_continuous_aggregate_policy('ohlc_hourly',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes',
    if_not_exists => TRUE
);

-- Technical indicators cache (optional, for frequently accessed indicators)
CREATE TABLE IF NOT EXISTS indicator_cache (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    indicator_name VARCHAR(50) NOT NULL,
    value DECIMAL(18,8),
    metadata JSONB,
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (time, symbol, timeframe, indicator_name)
);

SELECT create_hypertable('indicator_cache', 'time', if_not_exists => TRUE);

-- Add compression for indicator cache
ALTER TABLE indicator_cache SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol,timeframe,indicator_name'
);

SELECT add_compression_policy('indicator_cache', INTERVAL '30 days', if_not_exists => TRUE);

-- Portfolio tracking
CREATE TABLE IF NOT EXISTS portfolios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    initial_capital DECIMAL(18,2),
    currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS portfolio_positions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id),
    symbol VARCHAR(20) NOT NULL,
    quantity DECIMAL(18,8) NOT NULL,
    avg_entry_price DECIMAL(18,8),
    current_price DECIMAL(18,8),
    unrealized_pnl DECIMAL(18,2),
    realized_pnl DECIMAL(18,2),
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_positions_portfolio ON portfolio_positions (portfolio_id);

-- Trading signals (for strategy output)
CREATE TABLE IF NOT EXISTS trading_signals (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    strategy_name VARCHAR(100) NOT NULL,
    signal_type VARCHAR(20), -- buy, sell, hold
    strength DECIMAL(5,2), -- 0-100
    price_target DECIMAL(18,8),
    stop_loss DECIMAL(18,8),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (time, symbol, strategy_name)
);

SELECT create_hypertable('trading_signals', 'time', if_not_exists => TRUE);

-- Market calendar (trading hours, holidays)
CREATE TABLE IF NOT EXISTS market_calendar (
    id SERIAL PRIMARY KEY,
    exchange VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    is_trading_day BOOLEAN DEFAULT TRUE,
    open_time TIME,
    close_time TIME,
    holiday_name VARCHAR(100),
    UNIQUE(exchange, date)
);

CREATE INDEX IF NOT EXISTS idx_calendar_exchange ON market_calendar (exchange, date);

-- Splits and dividends
CREATE TABLE IF NOT EXISTS corporate_actions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    action_type VARCHAR(20), -- split, dividend, merger, etc.
    ex_date DATE NOT NULL,
    record_date DATE,
    pay_date DATE,
    ratio DECIMAL(18,8), -- for splits
    amount DECIMAL(18,8), -- for dividends
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_corporate_symbol ON corporate_actions (symbol, ex_date);

-- Functions for data quality checks
CREATE OR REPLACE FUNCTION check_data_gaps(
    p_symbol VARCHAR(20),
    p_timeframe VARCHAR(10),
    p_start_date TIMESTAMPTZ,
    p_end_date TIMESTAMPTZ
)
RETURNS TABLE (
    gap_start TIMESTAMPTZ,
    gap_end TIMESTAMPTZ,
    gap_duration INTERVAL
) AS $$
BEGIN
    RETURN QUERY
    WITH time_diffs AS (
        SELECT
            time,
            symbol,
            LAG(time) OVER (PARTITION BY symbol ORDER BY time) AS prev_time,
            time - LAG(time) OVER (PARTITION BY symbol ORDER BY time) AS time_diff
        FROM ohlc_data
        WHERE symbol = p_symbol
            AND timeframe = p_timeframe
            AND time BETWEEN p_start_date AND p_end_date
    )
    SELECT
        prev_time AS gap_start,
        time AS gap_end,
        time_diff AS gap_duration
    FROM time_diffs
    WHERE time_diff > INTERVAL '1 day' -- Adjust based on timeframe
        AND prev_time IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

-- Function to get latest price for a symbol
CREATE OR REPLACE FUNCTION get_latest_price(p_symbol VARCHAR(20), p_timeframe VARCHAR(10) DEFAULT '1d')
RETURNS DECIMAL(18,8) AS $$
DECLARE
    v_price DECIMAL(18,8);
BEGIN
    SELECT close INTO v_price
    FROM ohlc_data
    WHERE symbol = p_symbol
        AND timeframe = p_timeframe
    ORDER BY time DESC
    LIMIT 1;
    
    RETURN v_price;
END;
$$ LANGUAGE plpgsql;

-- Create read-only user for query access
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'trading_reader') THEN
        CREATE ROLE trading_reader WITH LOGIN PASSWORD 'change_me_in_production';
    END IF;
END
$$;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO trading_reader;
GRANT USAGE ON SCHEMA public TO trading_reader;

-- Create read-write user for data ingestion
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'trading_writer') THEN
        CREATE ROLE trading_writer WITH LOGIN PASSWORD 'change_me_in_production';
    END IF;
END
$$;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO trading_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO trading_writer;
GRANT USAGE ON SCHEMA public TO trading_writer;

-- Comments for documentation
COMMENT ON TABLE ohlc_data IS 'Main time-series table for OHLCV data across all symbols and timeframes';
COMMENT ON TABLE symbols IS 'Metadata about traded symbols (stocks, crypto, forex, etc.)';
COMMENT ON TABLE data_quality IS 'Data quality metrics and issue tracking';
COMMENT ON TABLE ingestion_logs IS 'Audit log for all data ingestion jobs';
COMMENT ON MATERIALIZED VIEW ohlc_daily IS 'Pre-aggregated daily OHLC data from minute bars';
COMMENT ON MATERIALIZED VIEW ohlc_hourly IS 'Pre-aggregated hourly OHLC data from minute bars';




