"""
Candlestick chart visualization utilities.

Provides interactive candlestick charts using Plotly.
"""

import logging
from typing import Optional, Union
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

logger = logging.getLogger(__name__)


def plot_candlesticks(
    data: pd.DataFrame,
    title: Optional[str] = None,
    show_volume: bool = False,
    height: int = 600
) -> go.Figure:
    """
    Plot interactive candlestick chart from OHLC data.

    Args:
        data: DataFrame with OHLC columns and datetime index
        title: Chart title (auto-generated if None)
        show_volume: Whether to show volume subplot
        height: Chart height in pixels

    Returns:
        Plotly Figure object
    """
    if data.empty:
        logger.warning("Empty data provided to plot_candlesticks")
        return go.Figure()

    # Validate required columns
    required_cols = ['Open', 'High', 'Low', 'Close']
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        logger.error(f"Missing required columns: {missing_cols}")
        return go.Figure()

    # Create subplots if volume is requested
    if show_volume and 'Volume' in data.columns:
        from plotly.subplots import make_subplots
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=('Price', 'Volume'),
            row_width=[0.7, 0.3]
        )

        # Add candlestick
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='OHLC'
            ),
            row=1, col=1
        )

        # Add volume bar chart
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color='rgba(0, 100, 255, 0.5)'
            ),
            row=2, col=1
        )

        # Update layout for subplots
        fig.update_layout(
            title=title or 'Candlestick Chart with Volume',
            yaxis_title='Price',
            yaxis2_title='Volume',
            xaxis_rangeslider_visible=False,
            height=height
        )

        # Update x-axis for both subplots
        fig.update_xaxes(rangeslider_visible=False, row=1, col=1)
        fig.update_xaxes(title_text='Date', row=2, col=1)

    else:
        # Single plot without volume
        fig = go.Figure(data=go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='OHLC'
        ))

        fig.update_layout(
            title=title or 'Candlestick Chart',
            yaxis_title='Price',
            xaxis_title='Date',
            xaxis_rangeslider_visible=False,
            height=height
        )

    # Common layout updates
    fig.update_layout(
        template='plotly_white',
        hovermode='x unified',
        showlegend=False
    )

    return fig


def plot_symbol_candles(
    symbol: str,
    start_date: str = '2023-01-01',
    end_date: Optional[str] = None,
    interval: str = '1d',
    show_volume: bool = True
) -> go.Figure:
    """
    Download data and create candlestick chart for a symbol.

    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        start_date: Start date string
        end_date: End date string (defaults to today)
        interval: Data interval ('1d', '1h', '1m', etc.)
        show_volume: Whether to show volume subplot

    Returns:
        Plotly Figure object
    """
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')

    try:
        logger.info(f"Downloading data for {symbol} to create candlestick chart")

        # Download data
        data = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False,
            auto_adjust=True
        )

        if data.empty:
            logger.warning(f"No data found for {symbol}")
            return go.Figure()

        # Handle MultiIndex columns from newer yfinance versions
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Create chart
        title = f"{symbol} Candlestick Chart ({start_date} to {end_date})"
        fig = plot_candlesticks(data, title=title, show_volume=show_volume)

        return fig

    except Exception as e:
        logger.error(f"Error creating candlestick chart for {symbol}: {e}")
        return go.Figure()


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Example usage
    symbol = 'AAPL'
    fig = plot_symbol_candles(symbol, show_volume=True)

    # Show the chart
    fig.show()

