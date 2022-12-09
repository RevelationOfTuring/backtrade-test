import backtrader as bt
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import tushare as ts


def get_data(code='600519', start='2017-01-01', end='2020-01-01'):
    # df = ts.get_k_data(code, start, end)
    # df.to_csv(f'data/{code}.csv')
    df = pd.read_csv(f'data/{code}.csv')
    df.index = pd.to_datetime(df.date)
    # 增添open interest这一列（backtrader要求数据必须有该列）
    df['openinterest'] = 0
    # 按照backtrader对数据的要求，整合列(顺序必须是下面的顺序ohlcvo)
    df = df[['open', 'high', 'low', 'close', 'volume', 'openinterest']]
    return df


if __name__ == '__main__':
    stock_df = get_data()
    stock_df1 = get_data('600419')

    # 1.加载data
    # 注：fromdate和todate必须是date格式
    fromdate = datetime(2017, 1, 1)
    todate = datetime(2020, 1, 1)
    # 创建两支股票的数据集
    data = bt.feeds.PandasData(dataname=stock_df, fromdate=fromdate, todate=todate)
    data1 = bt.feeds.PandasData(dataname=stock_df1, fromdate=fromdate, todate=todate)


    # 2.构建策略
    # 上穿20日线买入，跌穿20日线卖出
    class MyStrategy(bt.Strategy):
        # params = (
        #     ('period_20', 20),
        #     ('period_15', 15),
        # )
        # 也可以通过字典的形式定义params
        params = dict(period_20=20, period_15=15)

        def __init__(self):
            self.order = None
            # 定义line
            self.ma20 = bt.indicators.SMA(self.datas[0], period=self.params.period_20)
            # self.p 与 self.params 相同
            self.ma15 = bt.indicators.SMA(self.datas[0], period=self.p.period_15)
            # 定义一个line，该line为15日均线与20日均线的差
            self.ma_15_20 = self.ma15 - self.ma20
            # 生成时间错位的线
            self.close_1 = self.datas[0].close(-1)

        def next(self):
            # 打印datas[0]的column names， 即 ('close', 'low', 'high', 'open', 'volume', 'openinterest', 'datetime')
            # print(self.data.lines.getlinealiases())
            # 显示每天的date time(unix秒)
            print(self.data.datetime[0])
            # backtrader中一个工具，将unix秒转成日期
            print(bt.num2date(self.data.datetime[0]))

            # 策略自身只含一条datetime线，返回 ('datetime',)
            # print(self.getlinealiases())

            # 可以访问明天的时间
            # print(self.data.datetime.datetime(1))
            # 但是不能通过self.datetime.datetime(1)访问明天的datetime，会报错
            # print(self.datetime.datetime(1))

            # 明天的收盘价
            # print(self.data.close[1])
            # 昨天的收盘价
            # print(self.data.close[-1])

            # 回测bar的总数
            print(self.datas[0].buflen())
            # 已处理bar总数
            print(len(self.datas[0]))
            # 注: 非预加载情况下，len()和buflen()是一致的。都是动态增长。
            # 如果只有一个数据对象，那么len(self)和len(self.data)是一致的
            print(len(self))

            # 取最近的5个历史close(不包含今天)
            print(self.datas[0].close.get(ago=-1, size=5))
            # 取最近的5个历史close(包含今天)
            print(self.datas[0].close.get(ago=0, size=5))

            # 打印时间错位线
            print(self.close_1[0])
            print(self.datas[0].close[-1])
            print('-' * 20)

            # 如果当前有交易指令在进行，返回
            if self.order:
                return


    # 3. 策略设置
    cerebro = bt.Cerebro()  # 创建大脑

    # 将数据加入回测系统（添加两个数据集，并给每个数据集分别定义各自的名字）
    cerebro.adddata(data, name='maotai')
    cerebro.adddata(data1, name='tianren')

    # 加入自己的策略
    cerebro.addstrategy(MyStrategy)

    # 加入经纪人
    startcash = 100000
    cerebro.broker.set_cash(startcash)  # 设置初始资金
    cerebro.broker.setcommission(0.0002)  # 设置手续费(万分之2)

    # 4. 执行回测
    s = fromdate.strftime('%Y-%m-%d')
    t = todate.strftime('%Y-%m-%d')
    print(f'初始资金:{startcash}\n回测时间:{s}-{t}')
    cerebro.run()
    portval = cerebro.broker.getvalue()
    print(f'剩余总资金:{portval}')
