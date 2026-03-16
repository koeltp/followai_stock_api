"""
手动更新沪深300成分股
"""

from baostock_client import get_hs300_stocks

def update_hs300_stocks():
    try:
        print("开始获取沪深300成分股...")
        stocks = get_hs300_stocks()
        print(f"成功获取 {len(stocks)} 只沪深300成分股")
        print("前10只股票:")
        for stock in stocks[:10]:
            print(f"{stock.code}: {stock.name}")
    except Exception as e:
        print(f"获取失败: {str(e)}")

if __name__ == "__main__":
    update_hs300_stocks()