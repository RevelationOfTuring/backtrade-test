import backtrader as bt
import pandas as pd
import datetime


class HalfHalfBalance(bt.Strategy):
    def __init__(self):
        pass

    def next(self):
        today = self.data.datetime.date()
        year, month = today.year, today.month
        # 月末balance，统计当月有几天
        if month == 12:
            this_month_length = (datetime.datetime(year + 1, 1, 1) - datetime.datetime(year, month, 1)).days
        else:
            # 当月共有几天
            this_month_length = (datetime.datetime(year, month + 1, 1) - datetime.datetime(year, month, 1)).days
        # 月末调仓
        if today.day == this_month_length:
            # 将目标datafeed买入到你希望的占比
            # 将美股买入总资金的30%
            self.order_target_percent(target=0.3, data='nsdk')
            # 日经
            self.order_target_percent(target=0.1, data='rjzs')
            # 上证（a股）
            self.order_target_percent(target=0.25, data='szzs')
            # 债券
            self.order_target_percent(target=0.25, data='zzqz')
            # 为什么总体百分比之和不是100%? 因为可能资金量不够。
            # 在实盘中不可能将资金全部打满，要预留一部分针对流动性问题的出现


# 关闭默认添加的observers
cerebro = bt.Cerebro(stdstats=False)
cerebro.addobserver(bt.observers.Trades)
cerebro.addobserver(bt.observers.BuySell)
cerebro.addobserver(bt.observers.Value)

# 读取预处理好的数据
total_df = pd.read_hdf('processed_data.h5', key='data')

# col_name为每种基金的名称
for col_name in total_df:
    # 不加copy()会出现warning
    df = total_df[[col_name]].copy()
    for col in ['open', 'high', 'low', 'close']:
        # 将ohlc都设置成当天该基金的净值
        df[col] = df[col_name]
        df['volume'] = 1000000000
        datafeed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(datafeed, name=col_name)

cerebro.addstrategy(HalfHalfBalance)
cerebro.run()
print('value: ', cerebro.broker.get_value())
# 绘图不显示volume
cerebro.plot(style='candle', volume=False)
