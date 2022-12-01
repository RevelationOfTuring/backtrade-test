import backtrader as bt
import pandas as pd
import datetime


class ThreeBars(bt.Indicator):
    # 本指标中有两个lines，上下轨，在此声明
    lines = ('up', 'down')

    def __init__(self):
        # 设定指标最小的周期，即第四个bar上才会有指标数值
        self.addminperiod(4)
        # 指标作图的时候是跟着哪个data走的（即本指标中的up和down将跟主图呈现在一起）
        # self.plotinfo.plotmaster = self.data

    def next(self):
        # 其实就是self.up[0]
        # .get(ago=-1, size=3)中，size表示取出3天的价格，ago表示从哪天开始取（-1表示从昨天开始），那么总的就是从昨天开始向前取3天的数据
        self.lines[0][0] = max(max(self.data.close.get(ago=-1, size=3)), max(self.data.open.get(ago=-1, size=3)))
        self.down[0] = min(min(self.data.close.get(ago=-1, size=3)), min(self.data.open.get(ago=-1, size=3)))


class MyStrategy(bt.Strategy):
    def __init__(self):
        self.up_down = ThreeBars(self.data)
        # 指标线与主图显示在一起
        self.up_down.plotinfo.plotmaster = self.data

        self.buy_signal = bt.indicators.CrossOver(self.data.close, self.up_down.up)
        self.sell_signal = bt.indicators.CrossDown(self.data.close, self.up_down.down)
        # 不在图中显示buy_signal和sell_signal的值
        self.buy_signal.plotinfo.plot = False
        self.sell_signal.plotinfo.plot = False

    def next(self):
        # 如果此时没有仓位并且出现买入信号
        if not self.position and self.buy_signal[0] == 1:
            self.order = self.buy()
        # 如果此时持空仓并且出现买入信号
        if self.getposition().size < 0 and self.buy_signal[0] == 1:
            self.order = self.close()  # 清掉仓位
            self.order = self.buy()

        # 如果此时没仓位并且出现卖出信号
        if not self.position and self.sell_signal[0] == 1:
            self.order = self.sell()

        # 如果此时持多仓并且出现卖出信号
        if self.getposition().size > 0 and self.sell_signal[0] == 1:
            self.order = self.close()  # 清掉仓位
            self.order = self.sell()


cerebro = bt.Cerebro()

# 添加一个observer
cerebro.addobserver(bt.observers.TimeReturn)

# 读取数据的方法1
df = pd.read_csv('data/rbfi_day.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index('datetime', inplace=True)
df['openinterest'] = 0
# 注 能用pandas的地方尽量用pandas
# 将pandas的dateframe转换成cerebro能识别的数据形式
brf_daily = bt.feeds.PandasData(
    dataname=df,
    fromdate=datetime.datetime(2015, 5, 13),
    todate=datetime.datetime(2017, 6, 20)
)

# 添加datafeed时指定name
cerebro.adddata(brf_daily, name='brf')

cerebro.addstrategy(MyStrategy)

cerebro.run()

# 查看仓位信息
pos = cerebro.broker.getposition(brf_daily)

print(f'持仓大小: {pos.size}')
print(f'持仓均价: {pos.price}')
print(f'资产净值: {cerebro.broker.get_value()}')
print(f'可用现金: {cerebro.broker.get_cash()}')

# 曲线为蜡烛图
# cerebro.plot(style='candle')
