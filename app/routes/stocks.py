"""
股票路由模块
包含股票相关路由
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.db import get_hs300_stocks_from_db, save_stock_to_db
from app.services.baostock_client import get_stock_history as get_a_stock_history
from app.services.longport_client import sync_stock_data

router = APIRouter(prefix="/stocks")


class AddStockRequest(BaseModel):
    """添加股票请求"""
    code: str
    name: str
    market_type: str = "A"


class SyncStockRequest(BaseModel):
    """同步股票请求"""
    code: str
    market_type: str = "A"
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@router.get("/hs300")
def get_hs300_stocks_endpoint(page: int = 1, page_size: int = 10, search: str = None):
    """获取沪深300成分股（支持分页和搜索）"""
    try:
        if search:
            search = search.strip()
        result = get_hs300_stocks_from_db(page, page_size, search)
        
        if result["items"]:
            return {
                "total": result["total"],
                "page": result["page"],
                "page_size": result["page_size"],
                "items": [{"id": stock['id'], "code": stock['code'], "name": stock['name']} for stock in result["items"]]
            }
        else:
            return {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "items": []
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取沪深300成分股失败: {str(e)}")


@router.get("/list")
def get_stock_list(page: int = 1, page_size: int = 10, search: str = None, market: str = None):
    """获取所有股票列表（支持分页和搜索）"""
    try:
        from app.db.stock import get_all_stocks_from_db
        if search:
            search = search.strip()
        result = get_all_stocks_from_db(page, page_size, search, market)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票列表失败: {str(e)}")


@router.post("/add")
def add_stock(request: AddStockRequest):
    """添加股票"""
    try:
        code = request.code
        market_type = request.market_type
        
        # 根据市场类型转换代码格式
        if market_type == 'US':
            if not code.endswith('.US'):
                code = f"{code}.US"
        elif market_type == 'HK':
            if not code.endswith('.HK'):
                code = f"{code}.HK"
        elif market_type == 'A':
            # 自动判断并添加 sh. 或 sz. 前缀
            if not (code.startswith('sh.') or code.startswith('sz.')):
                # 移除可能的空格
                code = code.strip()
                # 判断股票代码类型
                if code.startswith('6'):
                    # 上海股票
                    code = f"sh.{code}"
                elif code.startswith('0') or code.startswith('3'):
                    # 深圳股票
                    code = f"sz.{code}"
                else:
                    # 无法判断，返回错误
                    return {
                        'success': False,
                        'message': '无法判断A股股票代码类型，请使用 sh. 或 sz. 前缀'
                    }
        
        stock_data = {
            'code': code,
            'name': request.name,
            'market_type': market_type,
            'is_hs300': 0
        }
        save_stock_to_db(stock_data)
        
        return {
            'success': True,
            'message': '股票添加成功',
            'data': stock_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加股票失败: {str(e)}")


@router.post("/sync")
def sync_stock(request: SyncStockRequest):
    """同步股票历史数据"""
    try:
        if request.market_type == 'A':
            # 验证 A 股股票代码格式
            code = request.code
            if not (code.startswith('sh.') or code.startswith('sz.')):
                return {
                    'success': False,
                    'message': 'A股股票代码格式错误，请使用 sh. 或 sz. 前缀'
                }
            
            # 检查代码长度
            code_part = code.split('.')[1]
            if len(code_part) != 6:
                return {
                    'success': False,
                    'message': '股票代码应为9位，请检查。格式示例：sh.600000'
                }
            
            history = get_a_stock_history(code, request.start_date, request.end_date)
            if history:
                return {
                    'success': True,
                    'message': f'成功同步 {len(history)} 条历史数据',
                    'count': len(history)
                }
            else:
                return {
                    'success': False,
                    'message': '未能获取到历史数据'
                }
        else:
            result = sync_stock_data(request.code, request.market_type, request.start_date, request.end_date)
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步股票数据失败: {str(e)}")
