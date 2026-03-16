"""
威科夫分析模块
整合Baostock客户端和Qwen分析器，提供完整的威科夫分析功能
"""

import time
from typing import List, Dict, Any
from models import WyckoffAnalysis, StockData
from baostock_client import get_stock_history
from qwen_analyzer import analyze_with_qwen
from database import save_wyckoff_analysis_to_db, save_stock_history_to_db, get_stock_name_from_db
from config import API_PRICE_CONFIG


def perform_wyckoff_analysis(stock_code: str, stock_name: str, start_date: str, end_date: str) -> WyckoffAnalysis:
    """
    执行威科夫分析
    
    Args:
        stock_code: 股票代码
        stock_name: 股票名称
        start_date: 开始日期
        end_date: 结束日期
    
    Returns:
        威科夫分析结果
    """
    try:
        # 获取股票历史数据
        stock_data = get_stock_history(stock_code, start_date, end_date)
        
        if len(stock_data) < 10:
            raise Exception("数据不足，无法进行分析")
        
        # 保存历史数据到数据库
        try:
            save_stock_history_to_db([
                {
                    'date': item.date,
                    'code': item.code,
                    'open': item.open,
                    'high': item.high,
                    'low': item.low,
                    'close': item.close,
                    'volume': item.volume,
                    'amount': item.amount
                }
                for item in stock_data
            ])
        except Exception as db_error:
            print(f"保存股票历史数据失败: {str(db_error)}")
        
        # 使用Qwen进行威科夫分析
        qwen_result = analyze_with_qwen(stock_data, stock_name)
        
        # 从数据库获取Qwen API价格配置
        from database import get_config_value
        input_price = float(get_config_value('qwen.standard.input.price'))
        output_price = float(get_config_value('qwen.standard.output.price'))
        
        # 计算token使用量和费用
        token_usage = qwen_result.get('token_usage', 0)
        prompt_tokens = qwen_result.get('prompt_tokens', 0)
        completion_tokens = qwen_result.get('completion_tokens', 0)
        
        # 分别计算输入和输出的费用
        input_cost = (prompt_tokens / 1000) * input_price
        output_cost = (completion_tokens / 1000) * output_price
        total_cost = input_cost + output_cost
        
        # 构建分析结果
        analysis = WyckoffAnalysis(
            code=stock_code,
            name=stock_name,
            analysis_date=stock_data[-1].date,
            trend=qwen_result.get('trend', '未知'),
            volume_pattern=qwen_result.get('volume_pattern', '未知'),
            support_level=qwen_result.get('support_level'),
            resistance_level=qwen_result.get('resistance_level'),
            signal=qwen_result.get('signal', '观望'),
            confidence=float(qwen_result.get('confidence', 0.5)),
            analysis_details=qwen_result.get('analysis_details', {})
        )
        
        # 保存分析结果到数据库
        save_wyckoff_analysis_to_db({
            'code': analysis.code,
            'name': analysis.name,
            'start_date': start_date,
            'end_date': analysis.analysis_date,
            'trend': analysis.trend,
            'volume_pattern': analysis.volume_pattern,
            'support_level': analysis.support_level,
            'resistance_level': analysis.resistance_level,
            'signal': analysis.signal,
            'confidence': analysis.confidence,
            'analysis_details': analysis.analysis_details,
            'token_usage': token_usage,
            'cost': total_cost
        })
        
        return analysis
        
    except Exception as e:
        raise Exception(f"威科夫分析失败: {str(e)}")


def batch_wyckoff_analysis(stocks: List[Dict[str, str]], start_date: str, end_date: str, 
                          min_confidence: float = 0.7) -> Dict[str, Any]:
    """
    批量威科夫分析
    
    Args:
        stocks: 股票列表 [{'code': 'xxx', 'name': 'xxx'}, ...]
        start_date: 开始日期
        end_date: 结束日期
        min_confidence: 最小置信度
    
    Returns:
        分析结果字典
    """
    qualified_stocks = []
    total_analyzed = 0
    failed_stocks = []
    
    for stock in stocks:
        try:
            analysis = perform_wyckoff_analysis(
                stock['code'],
                stock['name'],
                start_date,
                end_date
            )
            
            # 筛选符合条件的股票
            if analysis.confidence >= min_confidence and analysis.signal in ['买入', '强烈买入']:
                qualified_stocks.append(analysis)
            
            total_analyzed += 1
            
            # 避免请求过于频繁
            time.sleep(1.0)
            
        except Exception as e:
            print(f"分析{stock['name']}({stock['code']})失败: {str(e)}")
            failed_stocks.append({
                'code': stock['code'],
                'name': stock['name'],
                'error': str(e)
            })
            continue
    
    # 生成分析摘要
    analysis_summary = {
        "total_stocks": len(stocks),
        "qualified_count": len(qualified_stocks),
        "failed_count": len(failed_stocks),
        "qualification_rate": len(qualified_stocks) / len(stocks) if stocks else 0,
        "average_confidence": sum(s.confidence for s in qualified_stocks) / len(qualified_stocks) if qualified_stocks else 0,
        "signal_distribution": {
            "买入": len([s for s in qualified_stocks if s.signal == '买入']),
            "强烈买入": len([s for s in qualified_stocks if s.signal == '强烈买入'])
        }
    }
    
    return {
        "total_analyzed": total_analyzed,
        "qualified_stocks": qualified_stocks,
        "failed_stocks": failed_stocks,
        "analysis_summary": analysis_summary
    }


def single_stock_analysis(code: str, start_date: str, end_date: str) -> WyckoffAnalysis:
    """
    单只股票威科夫分析
    
    Args:
        code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
    
    Returns:
        威科夫分析结果
    """
    # 从数据库获取股票名称
    stock_name = get_stock_name_from_db(code)
    
    if not stock_name:
        raise Exception("股票不在沪深300成分股中")
    
    return perform_wyckoff_analysis(code, stock_name, start_date, end_date)
