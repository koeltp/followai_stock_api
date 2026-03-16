"""
Baostock客户端模块
用于获取股票数据
"""

import baostock as bs
from typing import List, Dict, Any
from app.db import save_stock_to_db, save_stock_history_to_db
from app.config import BAOSTOCK_CONFIG


class StockBase:
    """股票基本信息基类"""
    def __init__(self, code, name):
        self.code = code
        self.name = name


class StockData:
    """股票历史数据基类"""
    def __init__(self, date, code, open, high, low, close, volume, amount):
        self.date = date
        self.code = code
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.amount = amount


def get_hs300_stocks() -> List[StockBase]:
    """获取沪深300成分股"""
    # 登录baostock
    lg = bs.login()
    if lg.error_code != '0':
        print(f"登录失败: {lg.error_msg}")
        return []
    
    # 获取沪深300成分股
    rs = bs.query_hs300_stocks()
    if rs.error_code != '0':
        print(f"获取沪深300成分股失败: {rs.error_msg}")
        bs.logout()
        return []
    
    # 处理结果
    stocks = []
    while (rs.error_code == '0') & rs.next():
        item = rs.get_row_data()
        stock = StockBase(item[1], item[2])
        stocks.append(stock)
        
        # 保存到数据库
        save_stock_to_db({
            'code': item[1],
            'name': item[2],
            'is_hs300': 1
        })
    
    # 登出baostock
    bs.logout()
    return stocks


def get_stock_history(code: str, start_date: str = None, end_date: str = None) -> List[StockData]:
    """获取股票历史数据"""
    # 登录baostock
    lg = bs.login()
    if lg.error_code != '0':
        print(f"登录失败: {lg.error_msg}")
        return []
    
    # 设置默认日期
    if not start_date:
        start_date = BAOSTOCK_CONFIG.get('default_start_date', '2020-01-01')
    if not end_date:
        end_date = BAOSTOCK_CONFIG.get('default_end_date', '2023-12-31')
    
    # 获取股票历史数据
    rs = bs.query_history_k_data_plus(
        code,
        "date,code,open,high,low,close,volume,amount",
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag="3"
    )
    
    if rs.error_code != '0':
        print(f"获取股票历史数据失败: {rs.error_msg}")
        bs.logout()
        return []
    
    # 处理结果
    stock_data = []
    history_data = []
    while (rs.error_code == '0') & rs.next():
        item = rs.get_row_data()
        data = StockData(
            date=item[0],
            code=item[1],
            open=float(item[2]) if item[2] else 0,
            high=float(item[3]) if item[3] else 0,
            low=float(item[4]) if item[4] else 0,
            close=float(item[5]) if item[5] else 0,
            volume=float(item[6]) if item[6] else 0,
            amount=float(item[7]) if item[7] else 0
        )
        stock_data.append(data)
        
        # 准备保存到数据库的数据
        history_data.append({
            'date': item[0],
            'code': item[1],
            'open': float(item[2]) if item[2] else 0,
            'high': float(item[3]) if item[3] else 0,
            'low': float(item[4]) if item[4] else 0,
            'close': float(item[5]) if item[5] else 0,
            'volume': float(item[6]) if item[6] else 0,
            'amount': float(item[7]) if item[7] else 0
        })
    
    # 保存到数据库
    if history_data:
        save_stock_history_to_db(history_data)
    
    # 登出baostock
    bs.logout()
    return stock_data