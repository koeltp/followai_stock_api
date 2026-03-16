"""
更新沪深300成分股模块
"""

from app.services import get_hs300_stocks


def update_hs300_stocks():
    """更新沪深300成分股"""
    print("开始更新沪深300成分股...")
    stocks = get_hs300_stocks()
    print(f"成功更新 {len(stocks)} 只沪深300成分股")