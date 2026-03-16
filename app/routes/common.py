"""
通用路由模块
包含根路径和端点信息路由
"""

from fastapi import APIRouter
from typing import List
from app.schemas import APIEndpoint
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


@router.get("/endpoints", response_model=List[APIEndpoint])
def get_endpoints():
    """获取所有API端点信息"""
    endpoints = [
        APIEndpoint(
            name="根路径",
            path="/",
            method="GET",
            description="返回API基本信息"
        ),
        APIEndpoint(
            name="健康检查",
            path="/health",
            method="GET",
            description="检查系统运行状态"
        ),
        APIEndpoint(
            name="获取沪深300成分股",
            path="/stocks/hs300",
            method="GET",
            description="获取沪深300成分股列表"
        ),
        APIEndpoint(
            name="威科夫筛选",
            path="/stocks/wyckoff/screening",
            method="POST",
            description="基于威科夫操盘法筛选股票"
        ),
        APIEndpoint(
            name="单股分析",
            path="/stocks/wyckoff/analysis",
            method="GET",
            description="对单只股票进行威科夫分析"
        ),
        APIEndpoint(
            name="筛选历史",
            path="/stocks/wyckoff/history",
            method="GET",
            description="获取历史筛选记录"
        )
    ]
    return endpoints