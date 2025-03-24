import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import math
import glob
import os
import yfinance as yf


def get_apple_stock_data():
    # 创建数据目录
    data_dir = 'stock_data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    try:
        # 获取Apple股票数据
        aapl = yf.Ticker("AAPL")
        # 获取足够多的历史数据以确保至少有3681条记录
        df = aapl.history(period="max")

        # 确保按时间升序排序并重置索引
        df = df.sort_index(ascending=True)
        df = df.tail(3681).copy()  # 只取最近的3681条记录

        # 创建结果DataFrame
        result = pd.DataFrame(index=df.index)

        # 基本数据
        result['ts_code'] = 'AAPL.US'
        result['trade_date'] = df.index.strftime('%Y%m%d')
        result['open'] = df['Open'].round(2)
        result['high'] = df['High'].round(2)
        result['low'] = df['Low'].round(2)
        result['close'] = df['Close'].round(2)
        result['pre_close'] = df['Close'].shift(1).round(2)
        result['change'] = (df['Close'] - df['Close'].shift(1)).round(2)
        result['pct_chg'] = ((df['Close'] - df['Close'].shift(1)) / df['Close'].shift(1) * 100).round(2)

        # 成交量和成交额
        result['vol'] = (df['Volume'] / 100).round(2)  # 转换成手
        result['amount'] = (df['Close'] * df['Volume']).round(2)

        # 估算其他指标
        total_shares = 16500000000  # 苹果总股本（截至2024年约165亿股）
        float_shares = 16000000000  # 流通股本
        free_shares = float_shares  # 自由流通股本

        # 计算换手率和量比
        result['turnover_rate'] = (df['Volume'] / float_shares * 100).round(4)
        # 计算5日平均成交量，处理开始的几天没有足够数据的情况
        volume_ma5 = df['Volume'].rolling(window=5, min_periods=1).mean()
        result['volume_ratio'] = (df['Volume'] / volume_ma5).round(2)

        # 估算市盈率、市净率、市销率
        result['pe'] = 30.0  # 估算的市盈率
        result['pb'] = 7.5  # 估算的市净率
        result['ps'] = 7.2  # 估算的市销率

        # 股本数据
        result['total_share'] = total_shares
        result['float_share'] = float_shares
        result['free_share'] = free_shares

        # 市值数据（单位：亿元）
        result['total_mv'] = (df['Close'] * total_shares).round(2)
        result['circ_mv'] = (df['Close'] * float_shares).round(2)

        # 处理第一行的pre_close, change和pct_chg为0而不是NaN
        result.loc[result.index[0], 'pre_close'] = result.loc[result.index[0], 'close']
        result.loc[result.index[0], 'change'] = 0
        result.loc[result.index[0], 'pct_chg'] = 0

        # 重置索引并确保所有列都有值
        result = result.reset_index(drop=True)

        # 填充任何剩余的NaN值
        result = result.fillna(0)

        # 保存为CSV文件
        result.to_csv('apple_stock_data.csv', index=False, float_format='%.4f')
        print(f"成功保存了 {len(result)} 条记录到 apple_stock_data.csv")

        # 显示前几行数据用于验证
        print("\n数据预览:")
        print(result.head().to_string())

    except Exception as e:
        print(f"获取数据时发生错误: {str(e)}")
        print("请稍后重试")


if __name__ == "__main__":
    get_apple_stock_data()