"""
Qwen分析器模块
处理与Qwen3.5-Plus API的交互
"""

import requests
import json
import re
from typing import List, Dict, Any
from models import StockData
from config import get_qwen_api_config, API_CONFIG


def analyze_with_qwen(stock_data: List[StockData], stock_name: str) -> Dict[str, Any]:
    """
    使用Qwen3.5-Plus进行威科夫分析
    
    Args:
        stock_data: 股票历史数据
        stock_name: 股票名称
    
    Returns:
        分析结果字典
    """
    try:
        # 准备分析数据
        recent_data = stock_data[-20:]  # 使用最近20天的数据
        data_summary = []
        for item in recent_data:
            data_summary.append({
                "date": item.date,
                "close": item.close,
                "volume": item.volume,
                "high": item.high,
                "low": item.low
            })
        
        # 构建分析提示词
        prompt = f"""
        请基于威科夫操盘法分析以下股票数据：
        股票名称：{stock_name}
        最近20天数据：{json.dumps(data_summary, ensure_ascii=False)}
        
        请分析以下方面：
        1. 趋势分析（上涨/下跌/震荡）
        2. 成交量模式（放量/缩量/异常）
        3. 支撑位和阻力位
        4. 交易信号（买入/卖出/观望）
        5. 置信度（0-1之间的小数）
        
        请以JSON格式返回结果，包含以下字段：
        {{
            "trend": "趋势",
            "volume_pattern": "成交量模式",
            "support_level": 支撑位价格,
            "resistance_level": 阻力位价格,
            "signal": "交易信号",
            "confidence": 置信度,
            "analysis_details": {{
                "trend_analysis": "趋势分析详情",
                "volume_analysis": "成交量分析详情",
                "key_levels": "关键价位分析",
                "risk_assessment": "风险评估"
            }}
        }}
        """
        
        # 获取Qwen API配置
        qwen_config = get_qwen_api_config()
        
        # 调用Qwen API
        headers = {
            "Authorization": f"Bearer {qwen_config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": qwen_config['model'],
            "messages": [
                {"role": "system", "content": "你是一个专业的股票分析师，擅长威科夫操盘法分析。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": API_CONFIG["temperature"],
            "max_tokens": API_CONFIG["max_tokens"]
        }
        
        response = requests.post(
            f"{qwen_config['base_url']}/chat/completions",
            headers=headers,
            json=payload,
            timeout=API_CONFIG["timeout"]
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # 获取token使用量
            usage = result.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', 0)
            
            # 尝试解析JSON结果
            try:
                analysis_result = json.loads(content)
                # 添加token使用量到结果中
                analysis_result['token_usage'] = total_tokens
                analysis_result['prompt_tokens'] = prompt_tokens
                analysis_result['completion_tokens'] = completion_tokens
                return analysis_result
            except json.JSONDecodeError:
                # 如果直接解析失败，尝试提取JSON部分
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    analysis_result = json.loads(json_match.group())
                    # 添加token使用量到结果中
                    analysis_result['token_usage'] = total_tokens
                    analysis_result['prompt_tokens'] = prompt_tokens
                    analysis_result['completion_tokens'] = completion_tokens
                    return analysis_result
                else:
                    # 返回默认结果
                    default_result = get_default_analysis(content)
                    default_result['token_usage'] = total_tokens
                    default_result['prompt_tokens'] = prompt_tokens
                    default_result['completion_tokens'] = completion_tokens
                    return default_result
        else:
            raise Exception(f"Qwen API调用失败: {response.status_code}, {response.text}")
            
    except Exception as e:
        print(f"Qwen分析失败: {str(e)}")
        # 返回默认分析结果
        return get_default_analysis(str(e))


def get_default_analysis(error_message: str = "分析失败") -> Dict[str, Any]:
    """
    获取默认分析结果
    
    Args:
        error_message: 错误信息
    
    Returns:
        默认分析结果字典
    """
    return {
        "trend": "未知",
        "volume_pattern": "未知",
        "support_level": None,
        "resistance_level": None,
        "signal": "观望",
        "confidence": 0.3,
        "analysis_details": {
            "trend_analysis": "AI分析失败，使用默认值",
            "volume_analysis": error_message,
            "key_levels": "无",
            "risk_assessment": "高"
        }
    }