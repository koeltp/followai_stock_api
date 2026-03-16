"""
威科夫分析路由模块
包含威科夫分析相关路由
"""

from fastapi import APIRouter, HTTPException
from app.schemas import WyckoffAnalysis, ScreeningRequest, ScreeningResult
from app.services import get_hs300_stocks, batch_wyckoff_analysis, single_stock_analysis
from app.db import get_screening_history, get_analysis_history

# 创建路由器
router = APIRouter(prefix="/stocks/wyckoff")


@router.post("/screening", response_model=ScreeningResult)
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


@router.get("/analysis", response_model=WyckoffAnalysis)
def single_stock_analysis_endpoint(code: str, start_date: str, end_date: str):
    """单只股票威科夫分析"""
    try:
        return single_stock_analysis(code, start_date, end_date)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/history")
def get_screening_history_endpoint(limit: int = 50):
    """获取筛选历史记录"""
    try:
        return get_screening_history(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取筛选历史失败: {str(e)}")


@router.get("/analysis-history")
def get_analysis_history_endpoint(code: str = None, page: int = 1, page_size: int = 10, search: str = None, start_date: str = None, end_date: str = None):
    """获取分析历史记录（支持搜索和日期范围）"""
    try:
        # 去除搜索参数的前后空格
        if search:
            search = search.strip()
        return get_analysis_history(code, page, page_size, search, start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分析历史失败: {str(e)}")