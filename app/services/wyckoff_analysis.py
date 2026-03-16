"""
威科夫分析模块
用于分析股票的威科夫操盘法模式
"""

from typing import List, Dict, Any
from fastapi import HTTPException
from app.services.baostock_client import get_stock_history
from app.services.qwen_analyzer import analyze_with_qwen
from app.db import save_wyckoff_analysis_to_db, get_stock_name_from_db


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
    # 获取股票历史数据
    stock_data = get_stock_history(code, start_date, end_date)
    if not stock_data:
        raise HTTPException(status_code=404, detail=f"无法获取股票 {code} 的历史数据")
    
    # 获取股票名称
    stock_name = get_stock_name_from_db(code)
    if not stock_name:
        stock_name = "未知"
    
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
            for item in stock_data
        ]
    }
    
    # 使用Qwen进行分析
    analysis_result = analyze_with_qwen(analysis_data)
    
    # 保存分析结果到数据库
    save_wyckoff_analysis_to_db(analysis_result)
    
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