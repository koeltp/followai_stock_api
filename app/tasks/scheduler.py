"""
定时任务调度器模块
"""

import schedule
import time
import threading
from app.config.config import SCHEDULER_CONFIG
from app.tasks.update_hs300 import update_hs300_stocks


def setup_scheduler():
    """设置定时任务"""
    # 检查定时任务是否启用
    if not SCHEDULER_CONFIG.get('enabled', True):
        print("定时任务已禁用")
        return
    
    # 获取任务配置
    tasks_config = SCHEDULER_CONFIG.get('tasks', {})
    
    # 更新沪深300成分股任务
    update_hs300_config = tasks_config.get('update_hs300', {})
    if update_hs300_config.get('enabled', True):
        cron_time = update_hs300_config.get('cron', '09:00')
        schedule.every().day.at(cron_time).do(update_hs300_stocks)
        print(f"已设置更新沪深300成分股任务: 每天 {cron_time}")
    
    # 每日分析任务
    daily_analysis_config = tasks_config.get('daily_analysis', {})
    if daily_analysis_config.get('enabled', True):
        cron_time = daily_analysis_config.get('cron', '15:00')
        days = daily_analysis_config.get('days', ["monday", "tuesday", "wednesday", "thursday", "friday"])
        for day in days:
            getattr(schedule.every(), day).at(cron_time).do(run_daily_analysis)
        print(f"已设置每日威科夫分析任务: {', '.join(days)} {cron_time}")


def run_daily_analysis():
    """执行每日分析"""
    print("执行每日威科夫分析...")
    # 这里可以添加每日分析逻辑


def run_scheduler():
    """运行调度器"""
    # 检查定时任务是否启用
    if not SCHEDULER_CONFIG.get('enabled', True):
        print("定时任务已禁用，调度器未启动")
        return
    
    print("启动定时任务调度器...")
    while True:
        schedule.run_pending()
        time.sleep(60)
