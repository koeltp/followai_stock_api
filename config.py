"""
配置模块
包含系统所有配置信息
"""

import json
import os

# 从配置文件读取配置
def load_config():
    """从配置文件加载配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        if not config:
            raise ValueError("配置文件为空")
        return config

# 加载配置
CONFIG = load_config()

# FastAPI应用配置
APP_CONFIG = CONFIG.get('app')
if not APP_CONFIG:
    raise ValueError("应用配置缺失，请在config.json中配置 app")

# CORS配置
CORS_CONFIG = CONFIG.get('cors')
if not CORS_CONFIG:
    raise ValueError("CORS配置缺失，请在config.json中配置 cors")

# Baostock配置
BAOSTOCK_CONFIG = CONFIG.get('baostock')
if not BAOSTOCK_CONFIG:
    raise ValueError("Baostock配置缺失，请在config.json中配置 baostock")

# API请求配置
API_CONFIG = CONFIG.get('api')
if not API_CONFIG:
    raise ValueError("API配置缺失，请在config.json中配置 api")

# API价格配置
API_PRICE_CONFIG = CONFIG.get('api_price')
if not API_PRICE_CONFIG:
    raise ValueError("API价格配置缺失，请在config.json中配置 api_price")

# Qwen3.5-Plus API配置 - 延迟加载
QWEN_API_CONFIG = None

def get_qwen_api_config():
    """从数据库获取Qwen API配置"""
    global QWEN_API_CONFIG
    if QWEN_API_CONFIG is not None:
        return QWEN_API_CONFIG
    
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from database import get_config_value
    
    api_key = get_config_value('qwen_api_key')
    base_url = get_config_value('qwen_base_url')
    model = get_config_value('qwen_model') or get_config_value('qwen_model_name')
    
    if not api_key:
        raise ValueError("Qwen API密钥未配置，请在系统配置页面配置 qwen_api_key")
    if not base_url:
        raise ValueError("Qwen API地址未配置，请在系统配置页面配置 qwen_base_url")
    if not model:
        raise ValueError("Qwen 模型未配置，请在系统配置页面配置 qwen_model")
    
    QWEN_API_CONFIG = {
        "api_key": api_key,
        "base_url": base_url,
        "model": model
    }
    return QWEN_API_CONFIG
