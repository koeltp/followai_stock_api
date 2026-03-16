"""
API路由模块
包含所有API端点
"""

from fastapi import APIRouter, HTTPException
from typing import List
from models import (
    StockBase, WyckoffAnalysis, ScreeningRequest, 
    ScreeningResult, HealthResponse, APIEndpoint
)
from baostock_client import get_hs300_stocks
from wyckoff_analysis import batch_wyckoff_analysis, single_stock_analysis
from database import get_screening_history
from config import APP_CONFIG


# 创建API路由器
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


@router.get("/health", response_model=HealthResponse)
def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        message="系统运行正常"
    )


@router.get("/stocks/hs300")
def get_hs300_stocks_endpoint(page: int = 1, page_size: int = 10, search: str = None):
    """获取沪深300成分股（支持分页和搜索）"""
    try:
        # 去除搜索参数的前后空格
        if search:
            search = search.strip()
        # 从数据库获取
        from database import get_hs300_stocks_from_db
        result = get_hs300_stocks_from_db(page, page_size, search)
        
        if result["items"]:
            # 直接返回字典格式
            return {
                "total": result["total"],
                "page": result["page"],
                "page_size": result["page_size"],
                "items": [{"code": stock['code'], "name": stock['name']} for stock in result["items"]]
            }
        else:
            # 数据库中没有数据，返回空数据
            return {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "items": []
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取沪深300成分股失败: {str(e)}")


@router.post("/stocks/wyckoff/screening", response_model=ScreeningResult)
def wyckoff_screening(request: ScreeningRequest):
    """威科夫操盘法股票筛选"""
    try:
        # 获取沪深300成分股
        stocks = get_hs300_stocks()
        
        # 转换为字典格式
        stock_dicts = [
            {"code": stock.code, "name": stock.name}
            for stock in stocks
        ]
        
        # 执行批量威科夫分析
        result = batch_wyckoff_analysis(
            stock_dicts,
            request.start_date,
            request.end_date,
            request.min_confidence
        )
        
        return ScreeningResult(
            total_analyzed=result["total_analyzed"],
            qualified_stocks=result["qualified_stocks"],
            analysis_summary=result["analysis_summary"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"威科夫筛选失败: {str(e)}")


@router.get("/stocks/wyckoff/analysis", response_model=WyckoffAnalysis)
def single_stock_analysis_endpoint(code: str, start_date: str, end_date: str):
    """单只股票威科夫分析"""
    try:
        return single_stock_analysis(code, start_date, end_date)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/stocks/wyckoff/history")
def get_screening_history_endpoint(limit: int = 50):
    """获取筛选历史记录"""
    try:
        return get_screening_history(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取筛选历史失败: {str(e)}")


@router.get("/stocks/wyckoff/analysis-history")
def get_analysis_history_endpoint(code: str = None, page: int = 1, page_size: int = 10, search: str = None, start_date: str = None, end_date: str = None):
    """获取分析历史记录（支持搜索和日期范围）"""
    try:
        # 去除搜索参数的前后空格
        if search:
            search = search.strip()
        from database import get_analysis_history
        return get_analysis_history(code, page, page_size, search, start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分析历史失败: {str(e)}")


@router.get("/stocks/history")
def get_stock_history_endpoint(code: str, start_date: str = None, end_date: str = None):
    """获取股票历史数据（用于K线图展示）"""
    try:
        from baostock_client import get_stock_history
        stock_data = get_stock_history(code, start_date, end_date)
        return {
            "code": code,
            "data": [
                {
                    "date": item.date,
                    "open": item.open,
                    "high": item.high,
                    "low": item.low,
                    "close": item.close,
                    "volume": item.volume
                }
                for item in stock_data
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票历史数据失败: {str(e)}")


@router.get("/config")
def get_config_endpoint():
    """获取所有系统配置"""
    try:
        from database import get_all_configs
        configs = get_all_configs()
        return {"configs": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.post("/config")
def update_config_endpoint(config: dict):
    """更新系统配置"""
    try:
        from database import update_config_value
        config_key = config.get('config_key')
        config_value = config.get('config_value')
        description = config.get('description')
        
        if not config_key or config_value is None:
            raise HTTPException(status_code=400, detail="配置键和值不能为空")
        
        success = update_config_value(config_key, config_value, description)
        if success:
            return {"message": "配置更新成功"}
        else:
            raise HTTPException(status_code=500, detail="配置更新失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


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