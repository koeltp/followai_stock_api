"""
威科夫操盘法股票筛选系统 - 主应用入口
基于Python + FastAPI + Qwen3.5-Plus + MySQL
"""

import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.config import APP_CONFIG, CORS_CONFIG
from app.tasks import setup_scheduler, run_scheduler

# 创建FastAPI应用实例
app = FastAPI(
    title=APP_CONFIG["title"],
    description=APP_CONFIG["description"],
    version=APP_CONFIG["version"]
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_CONFIG["allow_origins"],
    allow_credentials=CORS_CONFIG["allow_credentials"],
    allow_methods=CORS_CONFIG["allow_methods"],
    allow_headers=CORS_CONFIG["allow_headers"],
)

# 注册API路由
app.include_router(router, tags=["API"])

# 启动定时任务
def start_scheduler():
    setup_scheduler()
    run_scheduler()

# 在后台线程中运行定时任务
scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
scheduler_thread.start()

# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=APP_CONFIG["host"], 
        port=APP_CONFIG["port"]
    )