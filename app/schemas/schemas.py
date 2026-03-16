"""
数据模式模块
包含所有Pydantic数据模型
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any


class StockBase(BaseModel):
    """股票基本信息模型"""
    code: str
    name: str


class StockData(BaseModel):
    """股票历史数据模型"""
    date: str
    code: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float


class WyckoffAnalysis(BaseModel):
    """威科夫分析结果模型"""
    model_config = ConfigDict(from_attributes=True)
    code: str
    name: str
    analysis_date: str
    trend: str
    volume_pattern: str
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    signal: str
    confidence: float
    analysis_details: Dict[str, Any]


class ScreeningRequest(BaseModel):
    """股票筛选请求模型"""
    start_date: str
    end_date: str
    min_confidence: float = 0.7


class ScreeningResult(BaseModel):
    """股票筛选结果模型"""
    model_config = ConfigDict(from_attributes=True)
    total_analyzed: int
    qualified_stocks: List[WyckoffAnalysis]
    analysis_summary: Dict[str, Any]


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    message: str


class APIEndpoint(BaseModel):
    """API端点信息模型"""
    name: str
    path: str
    method: str
    description: str