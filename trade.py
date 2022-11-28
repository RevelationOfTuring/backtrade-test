import backtrader as bt
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import tushare as ts


def get_data(code='600519', start='2017-01-01', end='2020-01-01'):
    # df = ts.get_k_data(code, start, end)
    # df.to_csv('data/600519.csv')
    df = pd.read_csv('data/600519.csv')
    df.index = pd.to_datetime(df.date)
    # 增添open interest这一列（backtrader要求数据必须有该列）
    df['openinterest'] = 0
    # 按照backtrader对数据的要求，整合列(顺序必须是下面的顺序ohlcvo)
    df = df[['open', 'high', 'low', 'close', 'volume', 'openinterest']]
    return df


if __name__ == '__main__':
    stock_df = get_data()

    # 1.加载data
    # 注：fromdate和todate必须是date格式
    fromdate = datetime(2017, 1, 1)
    todate = datetime(2020, 1, 1)
    data = bt.feeds.PandasData(dataname=stock_df, fromdate=fromdate, todate=todate)


    # 2.构建策略
    # 上穿20日线买入，跌穿20日线卖出
    class MyStrategy(bt.Strategy):
        params = (
            ('maperiod', 20),
        )

        def __init__(self):
            self.order = None
            # 计算sma
            self.ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)

        # 策略主要写在这里，每个bar执行一次，回测的每个日期都会执行一次
        def next(self):
            # 如果当前有交易指令在进行，返回
            if self.order:
                return

            # 如果当前无持仓（只考虑买不买）
            if not self.position:
                # 通过self.datas可以访问我们加载的所有数据源
                if self.datas[0].close[0] > self.ma[0]:
                    # 买入200股
                    self.order = self.buy(size=200)
            # 如果不是空仓（只考虑卖不卖）
            else:
                if self.datas[0].close[0] < self.ma[0]:
                    self.order = self.sell(size=200)


    # 3. 策略设置
    cerebro = bt.Cerebro()  # 创建大脑
    # 将数据加入回测系统。可以添加多个数据(可以理解为一支股票的数据可以作为一个data)，那么添加的第一个数据就可以在MyStrategy中用self.datas[0]来访问。
    # 添加的第二个数据，用datas[1]来访问
    cerebro.adddata(data)
    # 加入自己的策略
    cerebro.addstrategy(MyStrategy)

    # 加入经纪人
    startcash = 100000
    cerebro.broker.setcash(startcash)  # 设置初始资金
    cerebro.broker.setcommission(0.0002)  # 设置手续费(万分之2)
    # 设置滑点(万分之一)
    cerebro.broker.set_slippage_perc(perc=0.01)

    # 4. 执行回测
    s = fromdate.strftime('%Y-%m-%d')
    t = todate.strftime('%Y-%m-%d')
    print(f'初始资金:{startcash}\n回测时间:{s}-{t}')
    cerebro.run()
    portval = cerebro.broker.getvalue()
    print(f'剩余总资金:{portval}')
