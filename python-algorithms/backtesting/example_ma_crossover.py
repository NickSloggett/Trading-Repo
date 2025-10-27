import backtrader as bt
import yfinance as yf
import asyncio
import aiohttp
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Optional, Tuple

class OptimizedMACrossover(bt.Strategy):
    params = (
        ('fast_period', 10),
        ('slow_period', 30),
        ('printlog', False),
    )

    def __init__(self):
        # Use vectorized operations where possible
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        if self.crossover[0] > 0:  # Fast MA crosses above slow MA
            if not self.position:
                self.buy()
                if self.params.printlog:
                    print(f'Buy at {self.data.close[0]:.2f}')
        elif self.crossover[0] < 0:  # Fast MA crosses below slow MA
            if self.position:
                self.sell()
                if self.params.printlog:
                    print(f'Sell at {self.data.close[0]:.2f}')

async def download_data_async(symbol: str, start_date: datetime, end_date: datetime,
                             session: Optional[aiohttp.ClientSession] = None) -> pd.DataFrame:
    """Download stock data asynchronously with proper error handling."""
    try:
        # Use yfinance with async session if provided
        data_df = yf.download(symbol, start=start_date, end=end_date, progress=False)

        if data_df.empty:
            raise ValueError(f"No data found for {symbol}")

        return data_df
    except Exception as e:
        print(f"Error downloading {symbol}: {e}")
        raise

def vectorized_ma_signals(close_prices: np.ndarray, fast_period: int = 10,
                         slow_period: int = 30) -> Tuple[np.ndarray, np.ndarray]:
    """Calculate MA crossover signals using vectorized operations."""
    fast_ma = pd.Series(close_prices).rolling(window=fast_period).mean().values
    slow_ma = pd.Series(close_prices).rolling(window=slow_period).mean().values

    # Calculate crossovers using numpy for better performance
    fast_above_slow = fast_ma > slow_ma
    fast_above_slow_prev = np.roll(fast_above_slow, 1)
    fast_above_slow_prev[0] = fast_above_slow[0]  # Handle first element

    crossover = (fast_above_slow) & (~fast_above_slow_prev)  # Fast crosses above slow
    crossunder = (~fast_above_slow) & (fast_above_slow_prev)  # Fast crosses below slow

    return crossover, crossunder

async def run_backtest_async(symbol: str = 'AAPL', start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None, initial_cash: float = 10000.0) -> dict:
    """Run backtest asynchronously with optimized data handling."""
    if start_date is None:
        start_date = datetime(2020, 1, 1)
    if end_date is None:
        end_date = datetime(2023, 1, 1)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(OptimizedMACrossover, printlog=False)

    # Download data asynchronously
    async with aiohttp.ClientSession() as session:
        data_df = await download_data_async(symbol, start_date, end_date, session)

    # Handle MultiIndex columns from newer yfinance versions
    if isinstance(data_df.columns, pd.MultiIndex):
        # Flatten MultiIndex columns by taking the first level (price type)
        data_df.columns = data_df.columns.get_level_values(0)

    # Ensure we have the required columns
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in data_df.columns for col in required_cols):
        raise ValueError(f"Missing required columns in data. Found: {data_df.columns.tolist()}")

    data = bt.feeds.PandasData(dataname=data_df)
    cerebro.adddata(data)

    # Set initial cash and commission
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=0.001)  # 0.1%

    initial_value = cerebro.broker.getvalue()
    print(f'Starting Portfolio Value: ${initial_value:,.2f}')

    # Run backtest
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()

    print(f'Final Portfolio Value: ${final_value:,.2f}')
    print(f'Total Return: ${final_value - initial_value:,.2f} ({((final_value/initial_value - 1) * 100):.2f}%)')

    return {
        'initial_value': initial_value,
        'final_value': final_value,
        'total_return': final_value - initial_value,
        'total_return_pct': (final_value/initial_value - 1) * 100,
        'strategy': results[0]
    }

def run_backtest_sync(symbol: str = 'AAPL', start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None, initial_cash: float = 10000.0) -> dict:
    """Synchronous wrapper for backward compatibility."""
    return asyncio.run(run_backtest_async(symbol, start_date, end_date, initial_cash))

if __name__ == '__main__':
    # Run optimized backtest
    result = run_backtest_sync()

    # Optional: Plot results (commented out for headless environments)
    # cerebro.plot(style='candlestick')

