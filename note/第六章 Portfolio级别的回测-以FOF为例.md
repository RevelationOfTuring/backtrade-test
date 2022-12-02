## 第六章 Portfolio级别的回测-以FOF为例

<img src="assets/image-20221202173955859.png" alt="image-20221202173955859" style="zoom:50%;" />

FOF就是投资基金的基金。

<img src="assets/image-20221202174356574.png" alt="image-20221202174356574" style="zoom:50%;" />

这里是用四个数据：

- nsdk.csv：纳斯达克指数，这里可以理解为一个严格跟踪纳斯达克的基金（数据见下图）；

  <img src="assets/image-20221202175146644.png" alt="image-20221202175146644" style="zoom:50%;" />

- rjzs.csv：日经指数

- szzs.csv：上证指数

- zzqz.csv：中证全债（债券指数），可以将其看做一堆债券，不会怎么亏。

既然使用不同的指数，那么就面临一个新问题：交易日不同。

思路：假设四个数据中某一个指数当天有数据，那么即使其他三个都停市，那么这三个市场的数据都使用之前一天的数据进行填充。

所以要进行数据预处理（在jupyter-notebook中）：

```python
%matplotlib inline
import pandas as pd

nsdk_df=pd.read_csv('data/nsdk.csv')
rjzs_df=pd.read_csv('data/rjzs.csv')
szzs_df=pd.read_csv('data/szzs.csv')
zzqz_df=pd.read_csv('data/zzqz.csv')

# outer合并四个数据
summary_df = pd.merge(nsdk_df, rjzs_df, on=['datetime'], how='outer').merge(
    szzs_df, on=['datetime'], how='outer').merge(zzqz_df, on=['datetime'], how='outer')

# datetime转时间格式
summary_df.datetime = pd.to_datetime(summary_df.datetime)

# 按照datetime排序
summary_df = summary_df.sort_values('datetime')
summary_df
```

<img src="assets/image-20221202193230755.png" alt="image-20221202193230755" style="zoom:50%;" />

```python
# 用前一天的value填充，如果是na的话。最后的2008-01-02~2008-01-03的na用1.0填充
summary_df = summary_df.fillna(method='ffill').fillna(1.0)
```

<img src="assets/image-20221202193256717.png" alt="image-20221202193256717" style="zoom:50%;" />

```python
summary_df.set_index('datetime', inplace=True)
summary_df
```

<img src="assets/image-20221202193411702.png" alt="image-20221202193411702" style="zoom:50%;" />

```python
summary_df.plot(figsize=(16,9))
```

<img src="assets/image-20221202193411702.png" alt="image-20221202193411702" style="zoom:50%;" />

```python
summary_df.plot(figsize=(16,9))
# 数据持久化
summary_df.to_hdf('processed_data.h5',key='data')
```

<img src="assets/1.png" alt="image-20221202193411702" style="zoom:50%;" />