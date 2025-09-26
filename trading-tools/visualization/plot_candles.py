import plotly.graph_objects as go
import pandas as pd

def plot_candlesticks(data: pd.DataFrame, title: str = 'Candlestick Chart'):
    """
    Plot candlestick chart from OHLC data.
    
    :param data: DataFrame with 'Open', 'High', 'Low', 'Close', index as dates
    :param title: Chart title
    """
    fig = go.Figure(data=go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Candles'
    ))
    
    fig.update_layout(
        title=title,
        yaxis_title='Price',
        xaxis_title='Date',
        xaxis_rangeslider_visible=False
    )
    
    fig.show()

if __name__ == '__main__':
    import yfinance as yf
    from datetime import datetime
    
    symbol = 'AAPL'
    start = '2023-01-01'
    end = datetime.now().strftime('%Y-%m-%d')
    data = yf.download(symbol, start=start, end=end)
    plot_candlesticks(data, f'{symbol} Candlestick Chart')
