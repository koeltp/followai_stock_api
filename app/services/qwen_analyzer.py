"""
Qwen分析器模块
使用Qwen3.5-Plus API进行股票分析
"""

import json
import re
from typing import Dict, Any
from openai import OpenAI
from app.config import get_qwen_api_config
from app.db.config import get_config_value
from app.db.analysis_log import save_analysis_log


def calculate_cost(token_usage: Dict[str, int]) -> float:
    """计算API调用成本"""
    input_tokens = token_usage.get('input_tokens', 0)
    output_tokens = token_usage.get('output_tokens', 0)
    
    # 从数据库获取价格配置
    input_price = float(get_config_value('qwen_input_price', 0.015))
    output_price = float(get_config_value('qwen_output_price', 0.06))
    
    input_cost = (input_tokens / 1000) * input_price
    output_cost = (output_tokens / 1000) * output_price
    
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

股票名称：{stock_data['name']}
分析周期：{stock_data['start_date']} 到 {stock_data['end_date']}
历史数据：
{json.dumps(stock_data['data'], ensure_ascii=False)}
请按照以下格式输出分析结果：
1. 趋势分析：判断当前股票处于什么趋势（上升、下降、横盘）
2. 量价关系：分析成交量与价格的关系
3. 支撑阻力：识别关键支撑位和阻力位
4. 交易信号：给出买入、卖出或持有信号
5. 置信度：给出分析结果的置信度（0-1之间）
6. 详细分析：提供详细的分析过程

请以JSON格式返回分析结果，包含以下字段：
- trend: 趋势
- volume_pattern: 量价模式
- support_level: 支撑位
- resistance_level: 阻力位
- signal: 交易信号
- confidence: 置信度
- analysis_details: 详细分析，必须是一个JSON对象，包含以下字段：
  - trend_analysis: 趋势分析详情
  - volume_analysis: 成交量分析详情
  - key_levels: 关键价位分析详情
  - risk_assessment: 风险评估详情

重要要求：
1. 请使用简体中文进行分析和回答
2. 分析结果要专业、客观、准确
3. 确保返回的JSON格式正确且完整
"""
    
    # 从配置中获取参数
    temperature = float(get_config_value('qwen_temperature', 0.3))
    max_tokens = int(get_config_value('qwen_max_tokens', 2000))
    
    # 创建OpenAI客户端
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    # 发送请求
    try:
        print(f"提示词: {prompt}")
        print(f"模型: {model}")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一位专业的股票分析师，精通威科夫操盘法。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        print("响应结果：", response)
        
        # 保存分析日志
        # 提取chat_completion_id
        chat_completion_id = response.id if hasattr(response, 'id') else ''
        
        log_data = {
            'code': stock_data['code'],
            'name': stock_data['name'],
            'start_date': stock_data['start_date'],
            'end_date': stock_data['end_date'],
            'prompt': prompt,
            'response': str(response),  # 保存整个response对象
            'chat_completion_id': chat_completion_id
        }
        analysis_log_id = save_analysis_log(log_data)
        
        # 解析响应
        content = response.choices[0].message.content
        
        # 提取JSON部分
        json_match = re.search(r'\{[\s\S]*\}', content)
        if not json_match:
            raise ValueError("无法从响应中提取JSON")
        
        analysis_result = json.loads(json_match.group(0))
        
        # 确保必要字段存在且格式正确
        required_fields = ['trend', 'volume_pattern', 'signal', 'confidence', 'analysis_details']
        for field in required_fields:
            if field not in analysis_result:
                # 如果缺少字段，使用默认值
                if field == 'confidence':
                    analysis_result[field] = 0.5
                elif field == 'analysis_details':
                    analysis_result[field] = {"error": "缺少详细分析"}
                else:
                    analysis_result[field] = "未知"
        
        # 直接设置股票基本信息
        analysis_result['code'] = stock_data['code']
        analysis_result['name'] = stock_data['name']
        analysis_result['start_date'] = stock_data['start_date']
        analysis_result['end_date'] = stock_data['end_date']
        
        # 确保confidence是浮点数
        if not isinstance(analysis_result['confidence'], (int, float)):
            try:
                analysis_result['confidence'] = float(analysis_result['confidence'])
            except:
                analysis_result['confidence'] = 0.5
        
        # 确保analysis_details是字典
        if not isinstance(analysis_result['analysis_details'], dict):
            analysis_result['analysis_details'] = {"analysis": str(analysis_result['analysis_details'])}
        
        # 添加token使用情况和成本
        if response.usage:
            token_usage = {
                'input_tokens': response.usage.prompt_tokens,
                'output_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            analysis_result['token_usage'] = token_usage['total_tokens']
            analysis_result['cost'] = calculate_cost(token_usage)
        else:
            analysis_result['token_usage'] = 0
            analysis_result['cost'] = 0.0
        
        # 确保support_level和resistance_level是可解析的
        if 'support_level' not in analysis_result:
            analysis_result['support_level'] = None
        if 'resistance_level' not in analysis_result:
            analysis_result['resistance_level'] = None
        
        # 添加chat_completion_id到分析结果
        analysis_result['chat_completion_id'] = chat_completion_id
        
        return analysis_result
    except Exception as e:
        # 分析失败时返回默认结果
        print(f"分析失败: {str(e)}")
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