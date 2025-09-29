import backtrader as bt
import yfinance as yf
from datetime import datetime

class MACrossover(bt.Strategy):
    params = (
        ('fast_period', 10),
        ('slow_period', 30),
        ('printlog', False),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        self.crossunder = bt.indicators.CrossUnder(self.fast_ma, self.slow_ma)

    def next(self):
        if self.crossover[0] > 0:
            if not self.position:
                self.buy()
                if self.params.printlog:
                    print(f'Buy at {self.data.close[0]:.2f}')
        elif self.crossunder[0] > 0:
            if self.position:
                self.sell()
                if self.params.printlog:
                    print(f'Sell at {self.data.close[0]:.2f}')

def run_backtest():
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MACrossover, printlog=True)

    # Download data
    symbol = 'AAPL'
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 1, 1)
    data_df = yf.download(symbol, start=start_date, end=end_date)
    data = bt.feeds.PandasData(dataname=data_df)
    cerebro.adddata(data)

    # Set initial cash and commission
    cerebro.broker.setcash(10000.0)
    cerebro.broker.setcommission(commission=0.001)  # 0.1%

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot
    cerebro.plot(style='candlestick')

if __name__ == '__main__':
    run_backtest()

