# Python Trading Algorithms and Data Analysis

This directory contains Python code for developing trading strategies, backtesting, and analyzing historical trading data.

## Structure

- **backtesting/**: Scripts and frameworks for strategy backtesting (e.g., using Backtrader)
- **config/**: Configuration files (API keys, symbols list, strategy params)
- **strategies/**: Implementations of trading strategies (e.g., MA crossover, RSI mean reversion)
- **utils/**: Utility functions (data loaders, technical indicators via TA library)
- **data/**: Directory for historical data (CSV/Parquet; large files ignored by .gitignore)
- **notebooks/**: Jupyter notebooks for exploratory data analysis and visualization

## Setup

1. **Install Dependencies**
   ```bash
   cd python-algorithms
   pip install -r requirements.txt
   ```
   Note: For TA-Lib binary, may need `conda install -c conda-forge ta-lib` or similar.

2. **Environment Variables**
   Create `.env` file in `config/` for API keys (e.g., ALPHA_VANTAGE_KEY=your_key)
   Use `python-dotenv` to load.

3. **Fetch Data**
   Run `utils/fetch_data.py` to download sample data via yfinance.

4. **Jupyter Notebooks**
   ```bash
   cd notebooks
   jupyter notebook
   ```

## Example Usage

### Backtesting a Strategy

See `backtesting/example_ma_crossover.py`:

```python
import backtrader as bt
import yfinance as yf

class MACrossover(bt.Strategy):
    params = (('fast', 10), ('slow', 30),)

    def __init__(self):
        self.fast_ma = bt.ind.SMA(period=self.p.fast)
        self.slow_ma = bt.ind.SMA(period=self.p.slow)
        self.crossover = bt.ind.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        if self.crossover > 0:
            self.buy()
        elif self.crossover < 0:
            self.sell()

# Run backtest
cerebro = bt.Cerebro()
data = bt.feeds.PandasData(dataname=yf.download('AAPL', '2020-01-01', '2023-01-01'))
cerebro.adddata(data)
cerebro.addstrategy(MACrossover)
cerebro.run()
cerebro.plot()
```

Run: `python backtesting/example_ma_crossover.py`

### Data Analysis Notebook

Open `notebooks/trading_data_analysis.ipynb` for loading data, computing indicators, and visualizing performance.

## Strategies

- Implement in `strategies/` as classes inheriting from backtrader.Strategy.
- Use `ta` library for indicators: e.g., `ta.momentum.RSIIndicator(close).rsi()`
- Test with historical data from yfinance or CSV.

## Best Practices

- Vectorize computations with Pandas/Numpy for speed.
- Use backtrader or vectorbt for efficient backtesting.
- Handle transaction costs and slippage in simulations.
- Version control configs but not sensitive API keys.
- Document strategies with docstrings and update README.

## Resources

- [Backtrader Documentation](https://www.backtrader.com/docu/)
- [TA Library](https://technical-analysis-library-in-python.readthedocs.io/)
- [yfinance](https://pypi.org/project/yfinance/)
- [Pandas for Finance](https://www.oreilly.com/library/view/python-for-finance/9781492024347/)

Contribute new strategies or analysis scripts!
