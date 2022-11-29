import backtrader as bt
import pandas as pd
import datetime


class DualThrust(bt.Strategy):
    def __init__(self):
        # 不plot小时级数据
        self.data1.plotinfo.plot = False

    def next(self):
        pass


cerebro = bt.Cerebro()

# 读取数据的方法1
df = pd.read_csv('data/rbfi_min.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index('datetime', inplace=True)
df['openinterest'] = 0

brf_min_bar = bt.feeds.PandasData(
    dataname=df,
    fromdate=datetime.datetime(2018, 5, 22),
    todate=datetime.datetime(2018, 6, 22),
    timeframe=bt.TimeFrame.Minutes
)

cerebro.adddata(brf_min_bar)
# 分钟线resample成日线
cerebro.resampledata(brf_min_bar, timeframe=bt.TimeFrame.Days)

cerebro.addstrategy(DualThrust)

cerebro.run()

cerebro.plot()
