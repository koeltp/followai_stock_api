"""
Baostock客户端模块
处理与Baostock API的交互
"""

import baostock as bs
import time
from typing import List, Dict
from models import StockBase, StockData
from config import BAOSTOCK_CONFIG
from database import save_stock_to_db


def init_baostock():
    """初始化baostock连接"""
    lg = bs.login()
    if lg.error_code != '0':
        raise Exception(f"登录失败: {lg.error_msg}")
    return lg


def close_baostock():
    """关闭baostock连接"""
    bs.logout()


def get_hs300_stocks() -> List[StockBase]:
    """获取沪深300成分股"""
    try:
        init_baostock()
        
        rs = bs.query_hs300_stocks()
        if rs.error_code != '0':
            raise Exception(f"获取沪深300成分股失败: {rs.error_msg}")
        
        stocks = []
        while (rs.error_code == '0') & rs.next():
            stock = rs.get_row_data()
            # Baostock返回格式: [updateDate, code, code_name]
            stock_data = StockBase(
                code=stock[1],
                name=stock[2]
            )
            stocks.append(stock_data)
            
            # 保存到数据库
            try:
                save_stock_to_db({
                    "code": stock[1],
                    "name": stock[2],
                    "is_hs300": 1
                })
            except Exception as db_error:
                print(f"数据库保存失败: {str(db_error)}")
            
            # 避免请求过于频繁
            time.sleep(0.1)
        
        close_baostock()
        return stocks
    except Exception as e:
        close_baostock()
        raise Exception(f"获取沪深300成分股失败: {str(e)}")


def get_stock_history(code: str, start_date: str, end_date: str) -> List[StockData]:
    """获取股票历史数据"""
    try:
        init_baostock()
        
        rs = bs.query_history_k_data_plus(
            code, 
            "date,code,open,high,low,close,volume,amount",
            start_date=start_date,
            end_date=end_date,
            frequency=BAOSTOCK_CONFIG["frequency"],
            adjustflag=BAOSTOCK_CONFIG["adjustflag"]
        )
        
        if rs.error_code != '0':
            raise Exception(f"获取股票历史数据失败: {rs.error_msg}")
        
        data = []
        while (rs.error_code == '0') & rs.next():
            row = rs.get_row_data()
            stock_data = StockData(
                date=row[0],
                code=row[1],
                open=float(row[2]) if row[2] else 0.0,
                high=float(row[3]) if row[3] else 0.0,
                low=float(row[4]) if row[4] else 0.0,
                close=float(row[5]) if row[5] else 0.0,
                volume=int(row[6]) if row[6] else 0,
                amount=float(row[7]) if row[7] else 0.0
            )
            data.append(stock_data)
        
        close_baostock()
        return data
    except Exception as e:
        close_baostock()
        raise Exception(f"获取股票历史数据失败: {str(e)}")


def get_stock_name(code: str) -> str:
    """根据股票代码获取股票名称"""
    try:
        init_baostock()
        
        rs = bs.query_hs300_stocks()
        stock_name = None
        while (rs.error_code == '0') & rs.next():
            stock = rs.get_row_data()
            if stock[0] == code:
                stock_name = stock[1]
                break
        
        close_baostock()
        return stock_name
    except Exception as e:
        close_baostock()
        raise Exception(f"获取股票名称失败: {str(e)}")