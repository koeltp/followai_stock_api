"""
威科夫分析模块
用于分析股票的威科夫操盘法模式
"""

from typing import List, Dict, Any
from fastapi import HTTPException
from app.services.qwen_analyzer import analyze_with_qwen
from app.db import save_wyckoff_analysis_to_db, get_stock_name_from_db, get_db_connection, get_stock_history_from_db


def get_stock_market_type(code: str) -> str:
    """获取股票的市场类型"""
    try:
        # 首先根据代码格式判断市场类型
        if code.endswith('.US'):
            return 'US'
        elif code.endswith('.HK'):
            return 'HK'
        elif code.startswith('sh.') or code.startswith('sz.'):
            return 'A'
        elif code.isdigit() and len(code) == 6:
            return 'A'
        
        # 如果无法从代码格式判断，查询数据库
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT market_type FROM stocks WHERE code = %s", (code,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    # 默认为美股
                    return 'US'
        finally:
            conn.close()
    except Exception as e:
        print(f"获取股票市场类型失败: {str(e)}")
        # 默认为美股
        return 'US'


class StockDataItem:
    """股票数据项类，用于统一数据访问方式"""
    def __init__(self, date, code, open, high, low, close, volume, amount):
        self.date = date
        self.code = code
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.amount = amount


def normalize_stock_data(stock_data):
    """统一处理股票数据格式，确保返回对象列表"""
    normalized_data = []
    for item in stock_data:
        if hasattr(item, 'date'):
            # 如果已经是对象，直接使用
            normalized_data.append(item)
        elif isinstance(item, dict):
            # 如果是字典，转换为对象
            normalized_item = StockDataItem(
                date=item.get('date', ''),
                code=item.get('code', ''),
                open=item.get('open', 0),
                high=item.get('high', 0),
                low=item.get('low', 0),
                close=item.get('close', 0),
                volume=item.get('volume', 0),
                amount=item.get('amount', 0)
            )
            normalized_data.append(normalized_item)
    return normalized_data


def batch_wyckoff_analysis(stocks: List[Dict[str, str]], start_date: str, end_date: str, min_confidence: float) -> Dict[str, Any]:
    """批量威科夫分析"""
    total_analyzed = 0
    qualified_stocks = []
    analysis_summary = {
        "total_analyzed": 0,
        "qualified_count": 0,
        "confidence_distribution": {}
    }
    
    for stock in stocks:
        try:
            result = single_stock_analysis(stock['code'], start_date, end_date)
            total_analyzed += 1
            
            if result.confidence >= min_confidence:
                qualified_stocks.append(result)
                
                # 更新分析摘要
                confidence_level = f"{int(result.confidence * 10) * 10}%"
                if confidence_level not in analysis_summary["confidence_distribution"]:
                    analysis_summary["confidence_distribution"][confidence_level] = 0
                analysis_summary["confidence_distribution"][confidence_level] += 1
        except Exception as e:
            print(f"分析股票 {stock['code']} 失败: {str(e)}")
    
    # 更新分析摘要
    analysis_summary["total_analyzed"] = total_analyzed
    analysis_summary["qualified_count"] = len(qualified_stocks)
    
    return {
        "total_analyzed": total_analyzed,
        "qualified_stocks": qualified_stocks,
        "analysis_summary": analysis_summary
    }


def single_stock_analysis(code: str, start_date: str, end_date: str) -> Any:
    """单只股票威科夫分析"""
    # 获取股票市场类型
    market_type = get_stock_market_type(code)
    print(f"股票 {code} 的市场类型: {market_type}")
    
    # 从数据库获取股票历史数据
    stock_data = get_stock_history_from_db(code, start_date, end_date)
    
    if not stock_data:
        raise HTTPException(status_code=404, detail=f"无法获取股票 {code} 的历史数据，请先同步数据")
    
    # 获取股票名称
    stock_name = get_stock_name_from_db(code)
    if not stock_name:
        raise HTTPException(status_code=404, detail=f"股票代码 {code} 不存在或未在数据库中")
    
    # 统一处理股票数据格式
    normalized_stock_data = normalize_stock_data(stock_data)
    
    # 准备分析数据
    analysis_data = {
        "code": code,
        "name": stock_name,
        "start_date": start_date,
        "end_date": end_date,
        "data": [
            {
                "date": item.date,
                "open": item.open,
                "high": item.high,
                "low": item.low,
                "close": item.close,
                "volume": item.volume
            }
            for item in normalized_stock_data
        ]
    }
    
    # 使用Qwen进行分析
    analysis_result = analyze_with_qwen(analysis_data)
    
    # 保存分析结果到数据库
    chat_completion_id = analysis_result.get('chat_completion_id', '')
    save_wyckoff_analysis_to_db(analysis_result, chat_completion_id)
    
    # 转换为Pydantic模型
    from app.schemas import WyckoffAnalysis
    return WyckoffAnalysis(
        code=analysis_result['code'],
        name=analysis_result['name'],
        analysis_date=analysis_result['end_date'],
        trend=analysis_result['trend'],
        volume_pattern=analysis_result['volume_pattern'],
        support_level=analysis_result.get('support_level'),
        resistance_level=analysis_result.get('resistance_level'),
        signal=analysis_result['signal'],
        confidence=analysis_result['confidence'],
        analysis_details=analysis_result['analysis_details']
    )