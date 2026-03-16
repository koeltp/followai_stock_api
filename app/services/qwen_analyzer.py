"""
Qwen分析器模块
使用Qwen3.5-Plus API进行股票分析
"""

import json
from typing import Dict, Any
import requests
from app.config import get_qwen_api_config, API_PRICE_CONFIG


def calculate_cost(token_usage: Dict[str, int]) -> float:
    """计算API调用成本"""
    input_tokens = token_usage.get('input_tokens', 0)
    output_tokens = token_usage.get('output_tokens', 0)
    
    input_cost = (input_tokens / 1000) * API_PRICE_CONFIG.get('input_price', 0.015)
    output_cost = (output_tokens / 1000) * API_PRICE_CONFIG.get('output_price', 0.06)
    
    return round(input_cost + output_cost, 4)


def analyze_with_qwen(stock_data: Dict[str, Any]) -> Dict[str, Any]:
    """使用Qwen进行股票分析"""
    # 获取API配置
    qwen_config = get_qwen_api_config()
    api_key = qwen_config['api_key']
    base_url = qwen_config['base_url']
    model = qwen_config['model']
    
    # 准备分析提示
    prompt = f"""你是一位专业的股票分析师，精通威科夫操盘法。请根据以下股票数据进行分析：

股票代码：{stock_data['code']}
股票名称：{stock_data['name']}
分析周期：{stock_data['start_date']} 到 {stock_data['end_date']}

历史数据：
{json.dumps(stock_data['data'][-30:], ensure_ascii=False)}  # 只取最近30天数据

请按照以下格式输出分析结果：
1. 趋势分析：判断当前股票处于什么趋势（上升、下降、横盘）
2. 量价关系：分析成交量与价格的关系
3. 支撑阻力：识别关键支撑位和阻力位
4. 交易信号：给出买入、卖出或持有信号
5. 置信度：给出分析结果的置信度（0-1之间）
6. 详细分析：提供详细的分析过程

请以JSON格式返回分析结果，包含以下字段：
- code: 股票代码
- name: 股票名称
- start_date: 分析开始日期
- end_date: 分析结束日期
- trend: 趋势
- volume_pattern: 量价模式
- support_level: 支撑位
- resistance_level: 阻力位
- signal: 交易信号
- confidence: 置信度
- analysis_details: 详细分析
"""
    
    # 构建请求
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是一位专业的股票分析师，精通威科夫操盘法。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    # 发送请求
    try:
        response = requests.post(base_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # 提取JSON部分
        import re
        json_match = re.search(r'\{[\s\S]*\}', content)
        if not json_match:
            raise ValueError("无法从响应中提取JSON")
        
        analysis_result = json.loads(json_match.group(0))
        
        # 添加token使用情况和成本
        if 'usage' in result:
            token_usage = result['usage']
            analysis_result['token_usage'] = token_usage.get('total_tokens', 0)
            analysis_result['cost'] = calculate_cost(token_usage)
        else:
            analysis_result['token_usage'] = 0
            analysis_result['cost'] = 0.0
        
        return analysis_result
    except Exception as e:
        # 分析失败时返回默认结果
        return {
            "code": stock_data['code'],
            "name": stock_data['name'],
            "start_date": stock_data['start_date'],
            "end_date": stock_data['end_date'],
            "trend": "未知",
            "volume_pattern": "未知",
            "support_level": None,
            "resistance_level": None,
            "signal": "持有",
            "confidence": 0.5,
            "analysis_details": {
                "error": f"分析失败: {str(e)}"
            },
            "token_usage": 0,
            "cost": 0.0
        }