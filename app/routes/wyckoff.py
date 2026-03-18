"""
威科夫分析路由模块
包含威科夫分析相关路由
"""

from fastapi import APIRouter, HTTPException
from app.schemas import WyckoffAnalysis, ScreeningRequest, ScreeningResult
from app.services import get_hs300_stocks, batch_wyckoff_analysis, single_stock_analysis
from app.db import get_screening_history, get_analysis_history, get_analysis_logs, get_analysis_log_by_id, save_wyckoff_analysis_to_db

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
def get_analysis_history_endpoint(code: str = None, page: int = 1, page_size: int = 10, search: str = None, start_date: str = None, end_date: str = None, market: str = None):
    """获取分析历史记录（支持搜索和日期范围）"""
    try:
        # 去除搜索参数的前后空格
        if search:
            search = search.strip()
        return get_analysis_history(code, page, page_size, search, start_date, end_date, market)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分析历史失败: {str(e)}")


@router.get("/analysis-logs")
def get_analysis_logs_endpoint(code: str = None, page: int = 1, page_size: int = 10, search: str = None, start_date: str = None, end_date: str = None):
    """获取分析日志记录（支持搜索和日期范围）"""
    try:
        # 去除搜索参数的前后空格
        if search:
            search = search.strip()
        return get_analysis_logs(code, page, page_size, search, start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分析日志失败: {str(e)}")


@router.post("/reparse/{log_id}")
def reparse_analysis_log(log_id: int):
    """重新解析分析日志到威科夫分析表"""
    try:
        # 获取分析日志
        log_data = get_analysis_log_by_id(log_id)
        if not log_data:
            raise HTTPException(status_code=404, detail=f"分析日志不存在: {log_id}")
        
        # 提取响应中的JSON部分
        import re
        import json
        response = log_data.get('response', '')
        json_match = re.search(r'\{[\s\S]*\}', response)
        if not json_match:
            raise HTTPException(status_code=400, detail="无法从日志响应中提取JSON")
        
        # 解析分析结果
        analysis_result = json.loads(json_match.group(0))
        
        # 确保必要字段存在
        required_fields = ['code', 'name', 'start_date', 'end_date', 'trend', 'volume_pattern', 'signal', 'confidence', 'analysis_details']
        for field in required_fields:
            if field not in analysis_result:
                if field == 'confidence':
                    analysis_result[field] = 0.5
                elif field == 'analysis_details':
                    analysis_result[field] = {"error": "缺少详细分析"}
                else:
                    analysis_result[field] = "未知"
        
        # 确保confidence是浮点数
        if not isinstance(analysis_result['confidence'], (int, float)):
            try:
                analysis_result['confidence'] = float(analysis_result['confidence'])
            except:
                analysis_result['confidence'] = 0.5
        
        # 确保analysis_details是字典
        if not isinstance(analysis_result['analysis_details'], dict):
            analysis_result['analysis_details'] = {"analysis": str(analysis_result['analysis_details'])}
        
        # 确保support_level和resistance_level存在
        if 'support_level' not in analysis_result:
            analysis_result['support_level'] = None
        if 'resistance_level' not in analysis_result:
            analysis_result['resistance_level'] = None
        
        # 从日志中获取chat_completion_id
        chat_completion_id = log_data.get('chat_completion_id', '')
        
        # 保存到威科夫分析表
        save_wyckoff_analysis_to_db(analysis_result, chat_completion_id)
        
        return {"message": "重新解析成功", "log_id": log_id, "chat_completion_id": chat_completion_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新解析失败: {str(e)}")