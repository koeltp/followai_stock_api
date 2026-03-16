"""
定时任务调度器模块
"""

import schedule
import time
import threading
from app.tasks.update_hs300 import update_hs300_stocks


def setup_scheduler():
    """设置定时任务"""
    # 每天早上9点更新沪深300成分股
    schedule.every().day.at("09:00").do(update_hs300_stocks)
    
    # 每周一到周五下午3点执行威科夫分析
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
        getattr(schedule.every(), day).at("15:00").do(run_daily_analysis)


def run_daily_analysis():
    """执行每日分析"""
    print("执行每日威科夫分析...")
    # 这里可以添加每日分析逻辑


def run_scheduler():
    """运行调度器"""
    print("启动定时任务调度器...")
    while True:
        schedule.run_pending()
        time.sleep(60)