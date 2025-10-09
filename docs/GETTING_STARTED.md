# Getting Started with Trading-Repo

This guide will help you set up and start using the Trading Development Platform.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Your First Backtest](#your-first-backtest)
5. [Data Management](#data-management)
6. [Platform-Specific Setup](#platform-specific-setup)
7. [Next Steps](#next-steps)

## Prerequisites

### Required Software

- **Python 3.8+** (3.11 recommended)
- **Docker & Docker Compose** (for database and services)
- **Git** (for version control)

### Optional Software (for platform development)

- **Visual Studio 2019+** (for NinjaTrader C# development)
- **GCC/Clang** (for Sierra Chart C++ development)
- **Java JDK 8+** (for MotiveWave Java development)
- **TradingView Account** (for Pine Script)

### System Requirements

- **RAM**: 8GB minimum, 16GB+ recommended
- **Disk**: 50GB free space (for data storage)
- **CPU**: Multi-core processor recommended for backtesting

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/NickSloggett/Trading-Repo.git
cd Trading-Repo
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

### 4. Install TA-Lib (Optional but Recommended)

TA-Lib provides advanced technical indicators.

**macOS:**
```bash
brew install ta-lib
pip install ta-lib
```

**Ubuntu/Debian:**
```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install ta-lib
```

**Windows:**
```bash
# Download pre-built wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip install TA_Lib‑0.4.XX‑cpXX‑cpXX‑win_amd64.whl
```

### 5. Start Data Infrastructure

```bash
cd data-management/database
docker-compose up -d

# Verify containers are running
docker ps

# You should see: timescaledb, redis, grafana, prometheus
```

### 6. Initialize Database

```bash
# Return to repo root
cd ../..

# Initialize database schema
python -c "
from data_management.storage.timescale_handler import TimescaleHandler
handler = TimescaleHandler(
    host='localhost',
    database='trading_data',
    user='trading_admin',
    password='change_me_in_production'
)
print('Database initialized successfully!')
"
```

### 7. Configure Environment

Create a `.env` file in the project root:

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=trading_data
POSTGRES_USER=trading_admin
POSTGRES_PASSWORD=change_me_in_production

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Data Provider API Keys (Optional)
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
POLYGON_API_KEY=your_polygon_key
```

## Quick Start

### 1. Download Sample Data

Let's download some historical data to get started:

```bash
python -m data_management.ingestion.pipeline \
    --symbols AAPL GOOGL MSFT TSLA AMZN \
    --start 2020-01-01 \
    --timeframe 1d \
    --provider yfinance
```

This downloads daily data for 5 stocks since 2020.

### 2. Verify Data

```python
from data_management.query import DataAPI

api = DataAPI()

# Get AAPL data
df = api.get_ohlc('AAPL', start='2020-01-01', end='2023-12-31')
print(f"Downloaded {len(df)} bars")
print(df.head())
```

### 3. Access Dashboards

Open in your browser:

- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **PgAdmin**: http://localhost:5050 (admin@trading.local/admin123)

## Your First Backtest

### Simple Moving Average Crossover

Create `my_first_strategy.py`:

```python
"""
Simple MA Crossover Strategy
Buy when fast MA crosses above slow MA
Sell when fast MA crosses below slow MA
"""

import pandas as pd
from data_management.query import DataAPI
from python_algorithms.backtesting.vectorbt_engine import (
    VectorbtBacktester, BacktestConfig
)

# 1. Get data
api = DataAPI()
data = api.get_ohlc('AAPL', start='2020-01-01', end='2023-12-31')

# 2. Calculate indicators
fast_ma = data['close'].rolling(10).mean()
slow_ma = data['close'].rolling(30).mean()

# 3. Generate signals
entries = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
exits = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))

# 4. Run backtest
config = BacktestConfig(
    initial_capital=10000,
    commission=0.001,  # 0.1%
    stop_loss=0.02     # 2% stop loss
)

backtester = VectorbtBacktester(config)
results = backtester.backtest_signals(data, entries, exits)

# 5. Print results
print(results)

# 6. Plot equity curve (if matplotlib is available)
try:
    import matplotlib.pyplot as plt
    results.equity_curve.plot(title='Equity Curve')
    plt.show()
except ImportError:
    print("Install matplotlib to visualize results: pip install matplotlib")
```

Run it:
```bash
python my_first_strategy.py
```

### Expected Output

```
Backtest Results
================
Total Return: 45.32%
Annual Return: 12.15%
Sharpe Ratio: 1.85
Sortino Ratio: 2.34
Max Drawdown: -15.23%

Total Trades: 12
Win Rate: 58.33%
Profit Factor: 1.92
Avg Win: 425.50
Avg Loss: -221.30
```

## Data Management

### Ingesting Data from Multiple Sources

```python
from data_management.ingestion.pipeline import DataPipeline
from data_management.ingestion.providers.yfinance_provider import YFinanceProvider

# Initialize pipeline
pipeline = DataPipeline(provider=YFinanceProvider())

# Ingest single symbol
pipeline.ingest_symbol(
    symbol='AAPL',
    start_date='2020-01-01',
    timeframe='1d'
)

# Ingest multiple symbols
symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
pipeline.ingest_batch(
    symbols=symbols,
    start_date='2020-01-01',
    timeframe='1d'
)

# Check data quality
quality_report = pipeline.check_data_quality('AAPL')
print(quality_report)
```

### Querying Data

```python
from data_management.query import DataAPI

api = DataAPI()

# Single symbol
df = api.get_ohlc('AAPL', start='2023-01-01', timeframe='1d')

# Multiple symbols
df_multi = api.get_multi_symbol(
    ['AAPL', 'GOOGL', 'MSFT'],
    start='2023-01-01'
)

# With pre-computed indicators
df_with_indicators = api.get_ohlc_with_indicators(
    'AAPL',
    indicators=['SMA_20', 'RSI_14', 'MACD']
)

# Latest bars
latest = api.get_latest('AAPL', bars=10)
```

## Platform-Specific Setup

### TradingView (Pine Script)

1. Go to [TradingView.com](https://www.tradingview.com)
2. Open Pine Editor
3. Copy code from `pine-script-indicators/basic/`
4. Click "Add to Chart"

See [Pine Script Guide](../pine-script-indicators/README.md)

### MotiveWave (Java)

1. Install MotiveWave from [motivewave.com](https://www.motivewave.com)
2. Copy Java files from `motivewave-indicators/studies/`
3. Compile with MotiveWave SDK
4. Add study to chart

See [MotiveWave Guide](../motivewave-indicators/README.md)

### Sierra Chart (C++)

1. Install Sierra Chart from [sierrachart.com](https://www.sierrachart.com)
2. Compile C++ files from `sierra-chart-indicators/`
3. Copy DLL/SO to Sierra Chart data folder
4. Add study in Sierra Chart

See [Sierra Chart Guide](../sierra-chart-indicators/README.md)

### NinjaTrader (C#)

1. Install NinjaTrader 8 from [ninjatrader.com](https://www.ninjatrader.com)
2. Copy C# files to `Documents\NinjaTrader 8\bin\Custom\Indicators\`
3. Compile in NinjaTrader
4. Add indicator to chart

See [NinjaTrader Guide](../ninjatrader-indicators/README.md)

## Next Steps

### Learn More

- **[Python Trading Guide](./PYTHON_TRADING.md)** - Advanced Python strategies
- **[Data Management Guide](./DATA_MANAGEMENT.md)** - Deep dive into data system
- **[API Reference](./API_REFERENCE.md)** - Complete API documentation

### Example Projects

Explore example projects in:
- `python-algorithms/strategies/` - Ready-to-use strategies
- `examples/notebooks/` - Jupyter notebook tutorials
- `docs/examples/` - Code examples and use cases

### Community and Support

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions and share strategies
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

## Troubleshooting

### Database Connection Issues

```bash
# Check if containers are running
docker ps

# View logs
docker logs trading-timescaledb
docker logs trading-redis

# Restart containers
cd data-management/database
docker-compose restart
```

### Import Errors

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python version
python --version  # Should be 3.8+

# Verify installation
python -c "import pandas, numpy, yfinance; print('OK')"
```

### Data Provider Issues

If yfinance fails:
- Check internet connection
- Verify symbol is correct (e.g., 'AAPL' not 'Apple')
- Try alternative provider (Alpaca, Polygon)
- Some symbols may require exchange suffix (e.g., 'BTC-USD')

### Performance Issues

```bash
# Optimize database
docker exec trading-timescaledb psql -U trading_admin -d trading_data -c "VACUUM ANALYZE;"

# Clear Redis cache
docker exec trading-redis redis-cli FLUSHDB

# Check disk space
df -h
```

## Support

For help:
1. Check documentation in `/docs`
2. Search GitHub Issues
3. Create new issue with details
4. Contact: [@NickSloggett](https://github.com/NickSloggett)

---

**Ready to start trading!** 🚀

Now that you're set up, explore the strategies in `python-algorithms/strategies/` or create your own!




