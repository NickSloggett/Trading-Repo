"""
Backtest runner for all trading strategies
"""
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import pytest


def run_all_strategies():
    """Run backtests for all available strategies"""
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    print("Running strategy backtests...")

    # Generate sample price data for backtesting
    np.random.seed(42)  # For reproducible results
    dates = pd.date_range('2023-01-01', periods=252, freq='D')  # 1 year of trading days
    
    # Generate realistic price data with trend and volatility
    returns = np.random.normal(0.0005, 0.02, 252)  # Daily returns with slight upward bias
    prices = 100 * np.exp(np.cumsum(returns))  # Starting price of $100
    
    price_data = pd.DataFrame({
        'date': dates,
        'price': prices,
        'volume': np.random.randint(1000000, 10000000, 252)
    })
    
    # Test different strategies
    strategies = {
        'Buy_Hold': test_buy_hold_strategy(price_data),
        'MA_Crossover': test_ma_crossover_strategy(price_data),
        'RSI_Strategy': test_rsi_strategy(price_data),
        'Mean_Reversion': test_mean_reversion_strategy(price_data)
    }
    
    # Compile results
    results = []
    for strategy_name, result in strategies.items():
        results.append({
            'strategy': strategy_name,
            'total_return': result['total_return'],
            'sharpe_ratio': result['sharpe_ratio'],
            'max_drawdown': result['max_drawdown'],
            'num_trades': result['num_trades'],
            'win_rate': result['win_rate']
        })
    
    # Save results
    results_df = pd.DataFrame(results)
    results_file = results_dir / "backtest_results.csv"
    results_df.to_csv(results_file, index=False)
    
    print(f"Backtest results saved to {results_file}")
    print("\nStrategy Performance Summary:")
    print(results_df.to_string(index=False))
    
    return True


def test_buy_hold_strategy(data):
    """Test buy and hold strategy"""
    initial_price = data['price'].iloc[0]
    final_price = data['price'].iloc[-1]
    total_return = (final_price - initial_price) / initial_price
    
    # Calculate Sharpe ratio
    returns = data['price'].pct_change().dropna()
    sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
    
    # Calculate max drawdown
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    
    return {
        'total_return': total_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'num_trades': 1,
        'win_rate': 1.0 if total_return > 0 else 0.0
    }


def test_ma_crossover_strategy(data):
    """Test moving average crossover strategy"""
    # Calculate moving averages
    data['ma_short'] = data['price'].rolling(window=10).mean()
    data['ma_long'] = data['price'].rolling(window=20).mean()
    
    # Generate signals
    data['signal'] = 0
    data.loc[data['ma_short'] > data['ma_long'], 'signal'] = 1
    data.loc[data['ma_short'] < data['ma_long'], 'signal'] = -1
    
    # Calculate strategy returns
    data['strategy_returns'] = data['signal'].shift(1) * data['price'].pct_change()
    strategy_returns = data['strategy_returns'].dropna()
    
    # Calculate performance metrics
    total_return = (1 + strategy_returns).prod() - 1
    sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252) if strategy_returns.std() > 0 else 0
    
    # Calculate max drawdown
    cumulative = (1 + strategy_returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    
    # Count trades
    position_changes = data['signal'].diff().abs()
    num_trades = (position_changes > 0).sum()
    
    # Calculate win rate
    winning_trades = (strategy_returns > 0).sum()
    total_trades = len(strategy_returns[strategy_returns != 0])
    win_rate = winning_trades / total_trades if total_trades > 0 else 0
    
    return {
        'total_return': total_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'num_trades': num_trades,
        'win_rate': win_rate
    }


def test_rsi_strategy(data):
    """Test RSI-based strategy"""
    # Calculate RSI
    data['rsi'] = calculate_rsi(data['price'], 14)
    
    # Generate signals (oversold/overbought)
    data['signal'] = 0
    data.loc[data['rsi'] < 30, 'signal'] = 1  # Buy when oversold
    data.loc[data['rsi'] > 70, 'signal'] = -1  # Sell when overbought
    
    # Calculate strategy returns
    data['strategy_returns'] = data['signal'].shift(1) * data['price'].pct_change()
    strategy_returns = data['strategy_returns'].dropna()
    
    # Calculate performance metrics
    total_return = (1 + strategy_returns).prod() - 1
    sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252) if strategy_returns.std() > 0 else 0
    
    # Calculate max drawdown
    cumulative = (1 + strategy_returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    
    # Count trades
    position_changes = data['signal'].diff().abs()
    num_trades = (position_changes > 0).sum()
    
    # Calculate win rate
    winning_trades = (strategy_returns > 0).sum()
    total_trades = len(strategy_returns[strategy_returns != 0])
    win_rate = winning_trades / total_trades if total_trades > 0 else 0
    
    return {
        'total_return': total_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'num_trades': num_trades,
        'win_rate': win_rate
    }


def test_mean_reversion_strategy(data):
    """Test mean reversion strategy"""
    # Calculate Bollinger Bands
    data['sma'] = data['price'].rolling(window=20).mean()
    data['std'] = data['price'].rolling(window=20).std()
    data['upper_band'] = data['sma'] + 2 * data['std']
    data['lower_band'] = data['sma'] - 2 * data['std']
    
    # Generate signals
    data['signal'] = 0
    data.loc[data['price'] < data['lower_band'], 'signal'] = 1  # Buy when below lower band
    data.loc[data['price'] > data['upper_band'], 'signal'] = -1  # Sell when above upper band
    
    # Calculate strategy returns
    data['strategy_returns'] = data['signal'].shift(1) * data['price'].pct_change()
    strategy_returns = data['strategy_returns'].dropna()
    
    # Calculate performance metrics
    total_return = (1 + strategy_returns).prod() - 1
    sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252) if strategy_returns.std() > 0 else 0
    
    # Calculate max drawdown
    cumulative = (1 + strategy_returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    
    # Count trades
    position_changes = data['signal'].diff().abs()
    num_trades = (position_changes > 0).sum()
    
    # Calculate win rate
    winning_trades = (strategy_returns > 0).sum()
    total_trades = len(strategy_returns[strategy_returns != 0])
    win_rate = winning_trades / total_trades if total_trades > 0 else 0
    
    return {
        'total_return': total_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'num_trades': num_trades,
        'win_rate': win_rate
    }


def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


if __name__ == "__main__":
    success = run_all_strategies()
    sys.exit(0 if success else 1)
