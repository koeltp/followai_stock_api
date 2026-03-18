#!/usr/bin/env python3
"""
数据库辅助函数模块
"""


def parse_price_value(value):
    """解析价格值"""
    if value is None:
        return 0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0
