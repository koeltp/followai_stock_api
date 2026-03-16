"""
定时任务模块
用于每天19点从Baostock获取最新的股票数据并保存到数据库
"""

import schedule
import time
import datetime
from baostock_client import get_hs300_stocks
from database import save_stock_to_db
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def update_hs300_stocks():
    """更新沪深300成分股数据"""
    logger.info("开始更新沪深300成分股数据")
    try:
        # 获取沪深300成分股
        stocks = get_hs300_stocks()
        logger.info(f"成功获取{len(stocks)}只沪深300成分股")
        
        # 保存到数据库
        for stock in stocks:
            try:
                save_stock_to_db({
                    "code": stock.code,
                    "name": stock.name
                })
            except Exception as e:
                logger.error(f"保存股票{stock.code}失败: {str(e)}")
        
        logger.info("沪深300成分股数据更新完成")
    except Exception as e:
        logger.error(f"更新沪深300成分股数据失败: {str(e)}")


def setup_scheduler():
    """设置定时任务"""
    # 每天19点执行
    schedule.every().day.at("19:00").do(update_hs300_stocks)
    logger.info("定时任务设置完成，每天19点更新沪深300成分股数据")
    
    # 不再立即执行，只在定时任务时间执行
    # 如果需要首次运行时有数据，请手动调用一次update_hs300_stocks()


def run_scheduler():
    """运行定时任务"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次


if __name__ == "__main__":
    setup_scheduler()
    run_scheduler()
