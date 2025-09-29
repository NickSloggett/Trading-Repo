import yfinance as yf
import pandas as pd
from datetime import datetime
import os

def fetch_and_save(symbol, start_date, end_date, save_path='data'):
    """
    Fetch historical data for a symbol and save to CSV.
    
    :param symbol: Stock symbol (e.g., 'AAPL')
    :param start_date: Start date (str or datetime)
    :param end_date: End date (str or datetime)
    :param save_path: Directory to save CSV
    """
    # Create data dir if not exists
    os.makedirs(save_path, exist_ok=True)
    
    # Download data
    data = yf.download(symbol, start=start_date, end=end_date)
    
    if data.empty:
        print(f"No data found for {symbol}")
        return
    
    # Save to CSV
    filename = f"{symbol}_{start_date.replace('-', '')}_to_{end_date.replace('-', '')}.csv"
    filepath = os.path.join(save_path, filename)
    data.to_csv(filepath)
    print(f"Data saved to {filepath}")
    print(f"Shape: {data.shape}")
    
    return data

if __name__ == '__main__':
    symbol = 'AAPL'
    start = '2020-01-01'
    end = datetime.now().strftime('%Y-%m-%d')
    fetch_and_save(symbol, start, end)

