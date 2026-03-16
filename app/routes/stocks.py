"""
股票路由模块
包含股票相关路由
"""

from fastapi import APIRouter, HTTPException
from app.db import get_hs300_stocks_from_db
from app.services import get_stock_history

# 创建路由器
router = APIRouter(prefix="/stocks")


@router.get("/hs300")
def get_hs300_stocks_endpoint(page: int = 1, page_size: int = 10, search: str = None):
    """获取沪深300成分股（支持分页和搜索）"""
    try:
        # 去除搜索参数的前后空格
        if search:
            search = search.strip()
        # 从数据库获取
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


@router.get("/history")
def get_stock_history_endpoint(code: str, start_date: str = None, end_date: str = None):
    """获取股票历史数据（用于K线图展示）"""
    try:
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