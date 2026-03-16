"""
路由模块
包含所有API路由
"""

from fastapi import APIRouter
from .common import router as common_router
from .health import router as health_router
from .stocks import router as stocks_router
from .wyckoff import router as wyckoff_router
from .config import router as config_router

# 创建主路由器
router = APIRouter()

# 包含各个子路由
router.include_router(common_router, tags=["Common"])
router.include_router(health_router, tags=["Health"])
router.include_router(stocks_router, tags=["Stocks"])
router.include_router(wyckoff_router, tags=["Wyckoff"])
router.include_router(config_router, tags=["Config"])

__all__ = ['router']