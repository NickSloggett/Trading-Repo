# Library References

## Python Libraries

### Backtrader
- **Purpose**: Backtesting framework.
- **Docs**: [Backtrader Documentation](https://www.backtrader.com/docu/)
- **Key Classes**: `Cerebro`, `Strategy`, `DataFeed`
- **Example**: See `python-algorithms/backtesting/example_ma_crossover.py`

### TA (Technical Analysis Library)
- **Purpose**: Compute 200+ indicators.
- **Docs**: [TA Docs](https://technical-analysis-library-in-python.readthedocs.io/en/latest/)
- **Usage**: `ta.momentum.RSIIndicator(close=series).rsi()`

### yfinance
- **Purpose**: Download financial data from Yahoo Finance.
- **Docs**: [yfinance PyPI](https://pypi.org/project/yfinance/)
- **Usage**: `yf.download('AAPL', start='2020-01-01')`

### Plotly
- **Purpose**: Interactive visualizations.
- **Docs**: [Plotly Python](https://plotly.com/python/)
- **Example**: Candlestick charts in notebooks.

## Pine Script References

- [Pine Script v5 Reference](https://www.tradingview.com/pine-script-reference/v5/)

## MotiveWave SDK

- [Study Development](https://www.motivewave.com/support/study_development.htm)
- Key: `Study` class, `DataContext`, settings.
