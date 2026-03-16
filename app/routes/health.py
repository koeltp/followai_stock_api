"""
健康检查路由模块
包含健康检查相关路由
"""

from fastapi import APIRouter
from app.schemas import HealthResponse

# 创建路由器
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        message="系统运行正常"
    )