# Pine Script Indicators and Strategies

This directory contains Pine Script (v5) code for TradingView indicators, strategies, and utilities.

## Structure

- **basic/**: Simple built-in like indicators (e.g., MACD, RSI with customizations)
- **advanced/**: Complex multi-timeframe or machine learning inspired indicators
- **strategies/**: Entry/exit logic for backtesting strategies
- **utilities/**: Reusable functions and libraries (e.g., for alerts, plotting)

## Development

### Getting Started

1. Open TradingView.com and log in.
2. Go to a chart, click the Pine Editor at the bottom.
3. Copy the code from a `.pine` file here.
4. Paste into the editor, click "Add to Chart".
5. Save the script for future use.

### Creating New Indicators

Use the template below as a starting point:

```pinescript
//@version=5
indicator("My Custom Indicator", shorttitle="MCI", overlay=true)

// Inputs
length = input.int(14, title="Length", minval=1)

// Calculations
src = close
ma = ta.sma(src, length)

// Plotting
plot(ma, color=color.blue, title="MA")

// Alerts
alertcondition(ta.crossover(close, ma), title="Bullish Crossover", message="Price crossed above MA")
```

### Best Practices

- Use `//@version=5` for latest features.
- Define inputs for user customization.
- Use `ta.*` library for technical analysis functions.
- For strategies, use `strategy()` instead of `indicator()`, and `strategy.entry()`/`strategy.exit()`.
- Test on historical data before live use.
- Avoid repainting by using `barstate.isconfirmed`.

### Examples

- **MACD**: See `basic/macd-indicator.pine` for a customized MACD with histogram.
- **RSI**: `basic/rsi-indicator.pine` with overbought/oversold levels.
- **Strategy Example**: Add to `strategies/` a simple MA crossover strategy.

## Testing

- Use TradingView's Strategy Tester for backtesting.
- Replay bars to simulate real-time.
- Check for errors in the Pine Editor console.

## Resources

- [Pine Script v5 User Manual](https://www.tradingview.com/pine-script-docs/en/v5/)
- [TradingView Community Scripts](https://www.tradingview.com/scripts/)

Contribute new indicators by adding `.pine` files and updating this README.
