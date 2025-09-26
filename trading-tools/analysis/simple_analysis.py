import pandas as pd
import numpy as np

def compute_metrics(data: pd.DataFrame, risk_free_rate: float = 0.0) -> dict:
    """
    Compute basic performance metrics.
    
    :param data: DataFrame with 'Close' column
    :param risk_free_rate: Annual risk-free rate
    :return: Dict with metrics
    """
    # Daily returns
    data['Returns'] = data['Close'].pct_change()
    
    # Metrics
    total_return = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
    annualized_return = (1 + total_return) ** (252 / len(data)) - 1
    volatility = data['Returns'].std() * np.sqrt(252)
    sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility != 0 else 0
    
    metrics = {
        'Total Return': total_return,
        'Annualized Return': annualized_return,
        'Volatility': volatility,
        'Sharpe Ratio': sharpe_ratio
    }
    
    return metrics

if __name__ == '__main__':
    import yfinance as yf
    from datetime import datetime
    
    symbol = 'AAPL'
    start = '2020-01-01'
    end = datetime.now().strftime('%Y-%m-%d')
    data = yf.download(symbol, start=start, end=end)['Close'].to_frame()
    
    metrics = compute_metrics(data)
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")
