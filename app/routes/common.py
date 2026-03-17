"""
通用路由模块
包含根路径和端点信息路由
"""

from fastapi import APIRouter
from app.config import APP_CONFIG

# 创建路由器
router = APIRouter()


@router.get("/", response_model=dict)
def read_root():
    """根路径，返回API信息"""
    return {
        "message": APP_CONFIG["description"],
        "version": APP_CONFIG["version"],
        "endpoints": {
            "获取沪深300成分股": "/stocks/hs300",
            "威科夫筛选": "/stocks/wyckoff/screening",
            "单股分析": "/stocks/wyckoff/analysis",
            "筛选历史": "/stocks/wyckoff/history",
            "健康检查": "/health",
            "API文档": "/docs"
        }
    }


