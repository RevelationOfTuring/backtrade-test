import backtrader as bt
import pandas as pd
import datetime


class MyStrategy(bt.Strategy):
    def __init__(self):
        # 利用datas[0]数据来绘制sma曲线
        self.bt_sma = bt.indicators.MovingAverageSimple(self.data, period=24)
        # 更高级的金叉死叉的写法
        # close上穿sma返回1，下穿返回-1，不穿返回0
        self.buy_sell_signal = bt.indicators.CrossOver(self.data.close, self.bt_sma)

    def start(self):
        print('start()')

    def prenext(self):
        print('prenext()')

    def nextstart(self):
        print('nextstart()')

    def next(self):
        # 如果此时没有仓位并且close上穿sma
        if not self.position and self.buy_sell_signal[0] == 1:
            self.order = self.buy()
        # 如果此时没有仓位并且close下穿sma
        if not self.position and self.buy_sell_signal[0] == -1:
            self.order = self.sell()

        # 如果此时有仓位并且close上穿sma
        if self.position and self.buy_sell_signal[0] == 1:
            self.order = self.close()  # 清掉仓位
            self.order = self.buy()  # 转为多头
        # 如果此时有仓位并且close下穿sma
        if self.position and self.buy_sell_signal[0] == -1:
            self.order = self.close()  # 清掉仓位
            self.order = self.sell()  # 转为空头

    def stop(self):
        print('stop()')


cerebro = bt.Cerebro()

# 读取数据的方法1
df = pd.read_csv('data/rbfi_day.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index('datetime', inplace=True)
df['openinterest'] = 0
# 注 能用pandas的地方尽量用pandas
# 将pandas的dateframe转换成cerebro能识别的数据形式
brf_daily = bt.feeds.PandasData(
    dataname=df,
    fromdate=datetime.datetime(2016, 5, 13),
    todate=datetime.datetime(2017, 6, 20)
)

cerebro.adddata(brf_daily)

cerebro.addstrategy(MyStrategy)

cerebro.run()

# 绘制出的曲线为黑线
# cerebro.plot()
# 曲线为蜡烛图
cerebro.plot(style='candle')
