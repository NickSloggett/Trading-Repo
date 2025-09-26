# Trading Tools

This directory provides modular Python tools for trading-related tasks: fetching data, performing analysis, and creating visualizations.

## Structure

- **analysis/**: Scripts for technical/fundamental analysis (e.g., compute returns, volatility, correlations using Pandas/TA)
- **data-fetchers/**: Advanced data retrieval (yfinance, Alpha Vantage, Quandl; handle multiple symbols, intervals)
- **visualization/**: Plotting functions (candlestick charts with Plotly, heatmaps for correlations, performance charts with Matplotlib)
- **config/**: Shared configs (if needed, e.g., API endpoints)

Uses the same `requirements.txt` from `python-algorithms/`.

## Usage

Import and use functions directly.

Example: Visualize candles
```python
from visualization.plot_candles import plot_candlesticks
import yfinance as yf

data = yf.download('AAPL', '2023-01-01', '2023-12-31')
plot_candlesticks(data)
```

## Examples

- **Data Fetching**: `data-fetchers/multi_symbol_fetcher.py` - Download data for a list of symbols.
- **Analysis**: `analysis/volatility_calculator.py` - Compute rolling volatility.
- **Visualization**: `visualization/performance_summary.py` - Plot strategy returns.

## Integration

These tools can be imported into `python-algorithms/strategies/` for end-to-end workflows.

Contribute by adding new tools or improving existing ones!
