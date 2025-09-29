"""
High-Performance Backtesting Engine using vectorbt
Vectorized backtesting for ultra-fast strategy testing
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Callable, List, Tuple
import logging
from dataclasses import dataclass
from datetime import datetime

try:
    import vectorbt as vbt
    VBT_AVAILABLE = True
except ImportError:
    VBT_AVAILABLE = False
    print("Warning: vectorbt not installed. Install with: pip install vectorbt")

logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """Configuration for backtesting"""
    initial_capital: float = 10000.0
    commission: float = 0.001  # 0.1%
    slippage: float = 0.0005  # 0.05%
    leverage: float = 1.0
    margin: float = 1.0
    risk_free_rate: float = 0.02  # 2% annual
    
    # Position sizing
    size_type: str = 'percent'  # 'percent', 'shares', 'value'
    size: float = 1.0  # 100% of capital
    
    # Risk management
    stop_loss: Optional[float] = None  # e.g., 0.02 for 2% stop
    take_profit: Optional[float] = None  # e.g., 0.05 for 5% profit target
    trailing_stop: Optional[float] = None  # trailing stop percentage
    
    # Constraints
    max_positions: int = 1  # Maximum concurrent positions
    allow_short: bool = True


@dataclass
class BacktestResults:
    """Results from backtest"""
    # Performance metrics
    total_return: float
    annual_return: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    
    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    
    # Risk metrics
    volatility: float
    var_95: float  # Value at Risk 95%
    cvar_95: float  # Conditional VaR 95%
    
    # Time series
    equity_curve: pd.Series
    returns: pd.Series
    positions: pd.Series
    trades: pd.DataFrame
    
    # Raw portfolio object (for advanced analysis)
    portfolio: Any = None
    
    def __str__(self) -> str:
        return f"""
Backtest Results
================
Total Return: {self.total_return:.2%}
Annual Return: {self.annual_return:.2%}
Sharpe Ratio: {self.sharpe_ratio:.2f}
Sortino Ratio: {self.sortino_ratio:.2f}
Max Drawdown: {self.max_drawdown:.2%}

Total Trades: {self.total_trades}
Win Rate: {self.win_rate:.2%}
Profit Factor: {self.profit_factor:.2f}
Avg Win: {self.avg_win:.2f}
Avg Loss: {self.avg_loss:.2f}
        """


class VectorbtBacktester:
    """
    High-performance backtesting engine using vectorbt
    
    Vectorbt provides:
    - Ultra-fast vectorized backtesting (10-100x faster than backtrader)
    - Portfolio optimization
    - Advanced analytics
    - Interactive visualizations
    """
    
    def __init__(self, config: Optional[BacktestConfig] = None):
        """Initialize backtester"""
        if not VBT_AVAILABLE:
            raise ImportError("vectorbt is required. Install with: pip install vectorbt")
        
        self.config = config or BacktestConfig()
        logger.info("VectorbtBacktester initialized")
    
    def backtest_signals(
        self,
        data: pd.DataFrame,
        entries: pd.Series,
        exits: pd.Series,
        direction: str = 'longonly'  # 'longonly', 'shortonly', 'both'
    ) -> BacktestResults:
        """
        Backtest using entry and exit signals
        
        Args:
            data: OHLCV DataFrame
            entries: Boolean series indicating entry signals
            exits: Boolean series indicating exit signals
            direction: Trading direction
            
        Returns:
            BacktestResults object
        """
        # Create portfolio
        portfolio = vbt.Portfolio.from_signals(
            close=data['close'],
            entries=entries,
            exits=exits,
            direction=direction,
            init_cash=self.config.initial_capital,
            fees=self.config.commission,
            slippage=self.config.slippage,
            size=self.config.size,
            size_type=self.config.size_type,
            sl_stop=self.config.stop_loss,
            tp_stop=self.config.take_profit,
            allow_partial=True
        )
        
        return self._extract_results(portfolio, data)
    
    def backtest_orders(
        self,
        data: pd.DataFrame,
        size: pd.Series,
        price: Optional[pd.Series] = None
    ) -> BacktestResults:
        """
        Backtest using order sizes
        
        Args:
            data: OHLCV DataFrame
            size: Series with order sizes (positive for long, negative for short)
            price: Optional price series (default: close)
            
        Returns:
            BacktestResults object
        """
        if price is None:
            price = data['close']
        
        portfolio = vbt.Portfolio.from_orders(
            close=price,
            size=size,
            init_cash=self.config.initial_capital,
            fees=self.config.commission,
            slippage=self.config.slippage
        )
        
        return self._extract_results(portfolio, data)
    
    def optimize_parameters(
        self,
        data: pd.DataFrame,
        strategy_func: Callable,
        param_grid: Dict[str, List[Any]],
        metric: str = 'sharpe_ratio',
        maximize: bool = True
    ) -> Tuple[Dict[str, Any], BacktestResults]:
        """
        Optimize strategy parameters
        
        Args:
            data: OHLCV DataFrame
            strategy_func: Function that takes parameters and returns (entries, exits)
            param_grid: Dict of parameter names to lists of values to try
            metric: Metric to optimize ('sharpe_ratio', 'total_return', etc.)
            maximize: Whether to maximize (True) or minimize (False) metric
            
        Returns:
            Tuple of (best_params, best_results)
        """
        # Generate parameter combinations
        from itertools import product
        
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        param_combinations = list(product(*param_values))
        
        logger.info(f"Testing {len(param_combinations)} parameter combinations...")
        
        best_metric = float('-inf') if maximize else float('inf')
        best_params = None
        best_results = None
        
        for i, param_combo in enumerate(param_combinations):
            params = dict(zip(param_names, param_combo))
            
            try:
                # Generate signals with these parameters
                entries, exits = strategy_func(data, **params)
                
                # Run backtest
                results = self.backtest_signals(data, entries, exits)
                
                # Get metric value
                metric_value = getattr(results, metric)
                
                # Check if better
                is_better = (maximize and metric_value > best_metric) or \
                           (not maximize and metric_value < best_metric)
                
                if is_better:
                    best_metric = metric_value
                    best_params = params
                    best_results = results
                    logger.info(f"New best: {params} - {metric}={metric_value:.4f}")
                
            except Exception as e:
                logger.warning(f"Error testing params {params}: {e}")
                continue
            
            # Progress logging
            if (i + 1) % 10 == 0:
                logger.info(f"Tested {i + 1}/{len(param_combinations)} combinations")
        
        logger.info(f"Optimization complete. Best {metric}: {best_metric:.4f}")
        return best_params, best_results
    
    def walk_forward_analysis(
        self,
        data: pd.DataFrame,
        strategy_func: Callable,
        param_grid: Dict[str, List[Any]],
        train_period: int = 252,  # Trading days
        test_period: int = 63,
        anchored: bool = False
    ) -> List[BacktestResults]:
        """
        Walk-forward analysis for strategy validation
        
        Args:
            data: OHLCV DataFrame
            strategy_func: Strategy function
            param_grid: Parameter grid for optimization
            train_period: Days in training window
            test_period: Days in testing window
            anchored: Use anchored walk-forward (expanding window)
            
        Returns:
            List of BacktestResults for each test period
        """
        results = []
        total_periods = len(data)
        start_idx = train_period
        
        while start_idx + test_period <= total_periods:
            # Define train and test windows
            if anchored:
                train_start = 0
            else:
                train_start = start_idx - train_period
            
            train_data = data.iloc[train_start:start_idx]
            test_data = data.iloc[start_idx:start_idx + test_period]
            
            logger.info(f"Walk-forward: Train {len(train_data)} bars, Test {len(test_data)} bars")
            
            # Optimize on training data
            best_params, _ = self.optimize_parameters(
                train_data, strategy_func, param_grid
            )
            
            # Test on out-of-sample data
            entries, exits = strategy_func(test_data, **best_params)
            test_results = self.backtest_signals(test_data, entries, exits)
            
            results.append(test_results)
            
            # Move to next period
            start_idx += test_period
        
        logger.info(f"Walk-forward analysis complete: {len(results)} test periods")
        return results
    
    def monte_carlo_simulation(
        self,
        returns: pd.Series,
        n_simulations: int = 1000,
        n_periods: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Monte Carlo simulation of returns
        
        Args:
            returns: Historical returns series
            n_simulations: Number of simulations to run
            n_periods: Number of periods to simulate (default: same as returns)
            
        Returns:
            Dict with simulation results
        """
        if n_periods is None:
            n_periods = len(returns)
        
        # Calculate statistics
        mean_return = returns.mean()
        std_return = returns.std()
        
        # Run simulations
        simulations = []
        final_values = []
        
        for i in range(n_simulations):
            # Generate random returns
            sim_returns = np.random.normal(mean_return, std_return, n_periods)
            
            # Calculate cumulative returns
            cum_returns = (1 + sim_returns).cumprod()
            simulations.append(cum_returns)
            final_values.append(cum_returns[-1])
        
        simulations = np.array(simulations)
        final_values = np.array(final_values)
        
        # Calculate statistics
        return {
            'mean_final': np.mean(final_values),
            'median_final': np.median(final_values),
            'std_final': np.std(final_values),
            'percentile_5': np.percentile(final_values, 5),
            'percentile_95': np.percentile(final_values, 95),
            'probability_profit': np.mean(final_values > 1.0),
            'all_simulations': simulations,
            'final_values': final_values
        }
    
    def _extract_results(self, portfolio: Any, data: pd.DataFrame) -> BacktestResults:
        """Extract results from vectorbt portfolio"""
        # Get stats
        stats = portfolio.stats()
        
        # Calculate metrics
        total_return = portfolio.total_return()
        annual_return = portfolio.annualized_return()
        sharpe_ratio = portfolio.sharpe_ratio()
        sortino_ratio = portfolio.sortino_ratio()
        calmar_ratio = portfolio.calmar_ratio()
        max_drawdown = portfolio.max_drawdown()
        
        # Trade statistics
        trades = portfolio.trades.records_readable
        total_trades = len(trades)
        
        if total_trades > 0:
            winning_trades = len(trades[trades['PnL'] > 0])
            losing_trades = len(trades[trades['PnL'] < 0])
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            wins = trades[trades['PnL'] > 0]['PnL']
            losses = trades[trades['PnL'] < 0]['PnL']
            
            avg_win = wins.mean() if len(wins) > 0 else 0
            avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
            
            total_wins = wins.sum() if len(wins) > 0 else 0
            total_losses = abs(losses.sum()) if len(losses) > 0 else 1  # Avoid div by zero
            
            profit_factor = total_wins / total_losses if total_losses > 0 else 0
        else:
            winning_trades = losing_trades = 0
            win_rate = avg_win = avg_loss = profit_factor = 0
        
        # Get equity curve and returns
        equity_curve = portfolio.value()
        returns = portfolio.returns()
        positions = portfolio.positions.size
        
        # Risk metrics
        volatility = returns.std() * np.sqrt(252)  # Annualized
        var_95 = returns.quantile(0.05)
        cvar_95 = returns[returns <= var_95].mean()
        
        # Max drawdown duration
        drawdown = portfolio.drawdown()
        max_dd_duration = portfolio.max_dd_duration()
        
        return BacktestResults(
            total_return=total_return,
            annual_return=annual_return,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_dd_duration,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            volatility=volatility,
            var_95=var_95,
            cvar_95=cvar_95,
            equity_curve=equity_curve,
            returns=returns,
            positions=positions,
            trades=trades,
            portfolio=portfolio
        )


# Example usage
if __name__ == '__main__':
    # Example: SMA crossover strategy
    import sys
    sys.path.append('..')
    from data_management.query import DataAPI
    
    # Get data
    api = DataAPI()
    data = api.get_ohlc('AAPL', start='2020-01-01', end='2023-12-31')
    
    # Define strategy
    def sma_crossover_strategy(data, fast_period=10, slow_period=30):
        fast_ma = data['close'].rolling(fast_period).mean()
        slow_ma = data['close'].rolling(slow_period).mean()
        
        entries = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
        exits = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))
        
        return entries, exits
    
    # Run backtest
    config = BacktestConfig(
        initial_capital=10000,
        commission=0.001,
        stop_loss=0.02
    )
    
    backtester = VectorbtBacktester(config)
    
    entries, exits = sma_crossover_strategy(data, 10, 30)
    results = backtester.backtest_signals(data, entries, exits)
    
    print(results)
    
    # Optimize parameters
    param_grid = {
        'fast_period': [5, 10, 20],
        'slow_period': [20, 30, 50]
    }
    
    best_params, best_results = backtester.optimize_parameters(
        data, sma_crossover_strategy, param_grid
    )
    
    print(f"\nBest parameters: {best_params}")
    print(best_results)
