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
            # 买10手
            self.order = self.buy(size=10)


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
    fromdate=datetime.datetime(2015, 5, 13),
    todate=datetime.datetime(2017, 6, 20)
)

# 添加datafeed时指定name
cerebro.adddata(brf_daily, name='brf')

cerebro.addstrategy(MyStrategy)

# 设置起始现金2w元
cerebro.broker.setcash(20000.0)
# 设置期货模式的手续费
# cerebro.broker.setcommission(commission=2.0, margin=2000.0, name='brf')

# 设置股票模式的手续费
cerebro.broker.setcommission(commission=0.0003, name='brf')
# 固定滑点
# cerebro.broker.set_slippage_fixed(fixed=5)
# 万5的滑点
cerebro.broker.set_slippage_perc(perc=0.0005)

# 设置filler
# cerebro.broker.set_filler(bt.broker.fillers.FixedBarPerc(perc=0.1))
# 固定size的filler，每根bar最多只能买1手
cerebro.broker.set_filler(bt.broker.fillers.FixedSize(size=1))

cerebro.run()

# 曲线为蜡烛图
cerebro.plot(style='candle')
