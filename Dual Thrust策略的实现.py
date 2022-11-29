import backtrader as bt
import pandas as pd
import datetime


class DualThrust(bt.Indicator):
    lines = ('up', 'down')
    params = (
        ('period', 2),
        ('k_up', 0.7),
        ('k_down', 0.7)
    )

    def __init__(self):
        self.addminperiod(self.p.period + 1)

    def next(self):
        HH = max(self.data.high.get(-1, size=self.p.period))
        LC = min(self.data.close.get(-1, size=self.p.period))
        HC = max(self.data.close.get(-1, size=self.p.period))
        LL = min(self.data.low.get(-1, size=self.p.period))
        R = max(HH - LC, HC - LL)
        # 上轨
        self.lines.up[0] = self.data.open[0] + self.p.k_up * R
        # 下轨
        self.lines.down[0] = self.data.open[0] - self.p.k_down * R


class MyStrategy(bt.Strategy):
    def __init__(self):
        # 使用resample后的日级数据
        self.dt = DualThrust(self.data1)
        # tips：self.dt是日级数据，通过调用自己同名的方法，backtrader将自动将其转化成同main data
        # 相同的颗粒度——即：日级数据1个，扩充为24*60个相同的数据（与data0升级到同维）
        self.dt = self.dt()
        # 不单独绘制dl图
        # self.dt.plotinfo.plot = False
        # 在分钟级数据
        self.dt.plotinfo.plotmaster = self.data

        self.buy_signal = bt.indicators.CrossUp(self.data.close, self.dt.up)
        self.sell_signal = bt.indicators.CrossDown(self.data.close, self.dt.down)

    def next(self):
        # 每日9:03~22:55之间才开始做单（定义日内交易）
        if self.data.datetime.time() > datetime.time(9, 3) and self.data.datetime.time() < datetime.time(22, 55):
            if not self.position and self.buy_signal[0] == 1:
                self.order = self.buy()
            if not self.position and self.sell_signal[0] == 1:
                self.order = self.sell()

            if self.getposition().size < 0 and self.buy_signal[0] == 1:
                self.order = self.close()
                self.order = self.buy()

            if self.getposition().size > 0 and self.sell_signal[0] == 1:
                self.order = self.close()
                self.order = self.sell()

        # 如果到了22：55及其之后（尾盘），并且有持仓。那么平仓
        if self.data.datetime.time() >= datetime.time(22, 55) and self.position:
            self.order = self.close()


cerebro = bt.Cerebro()

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

cerebro.addstrategy(MyStrategy)

cerebro.run()

cerebro.plot(style='candle')
