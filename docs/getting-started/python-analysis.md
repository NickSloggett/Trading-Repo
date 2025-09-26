# Getting Started with Python Trading Analysis

## Overview

Use Python for data analysis, backtesting, and strategy development.

## Setup

1. Install Python 3.8+.
2. Navigate to `python-algorithms/`:
   ```bash
   cd python-algorithms
   pip install -r requirements.txt
   ```
3. For notebooks: `pip install jupyter` (included).

## Basic Usage

### Fetch Data
Run `utils/fetch_data.py` to download CSV data.

### Backtesting
Run `backtesting/example_ma_crossover.py` for a simple strategy test.

### Analysis
Open `notebooks/trading_data_analysis.ipynb` in Jupyter:
```bash
cd notebooks
jupyter notebook
```

## Key Libraries

- **yfinance**: Fetch market data.
- **pandas/ta**: Data manipulation and indicators.
- **backtrader**: Strategy backtesting.
- **plotly/matplotlib**: Visualizations.

## Workflow

1. Fetch data → `data/`
2. Analyze in notebook.
3. Implement strategy in `strategies/`.
4. Backtest in `backtesting/`.
5. Visualize results.

## Next Steps

- Customize strategies.
- Add more symbols from `config/symbols.json`.
- Explore `trading-tools/` for modular functions.
- Resources: [Backtrader Docs](https://www.backtrader.com/docu/)
