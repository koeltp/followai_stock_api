"""
配置模块
包含系统所有配置信息
"""

import json
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self._config = None
        self._qwen_api_config = None
    
    def load_config(self) -> Dict[str, Any]:
        """从配置文件加载配置"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if not config:
                raise ValueError("配置文件为空")
            self._config = config
            return config
    
    @property
    def config(self) -> Dict[str, Any]:
        """获取配置"""
        if self._config is None:
            self.load_config()
        return self._config
    
    @property
    def app_config(self) -> Dict[str, Any]:
        """获取应用配置"""
        app_config = self.config.get('app')
        if not app_config:
            raise ValueError("应用配置缺失，请在config.json中配置 app")
        return app_config
    
    @property
    def cors_config(self) -> Dict[str, Any]:
        """获取CORS配置"""
        cors_config = self.config.get('cors')
        if not cors_config:
            raise ValueError("CORS配置缺失，请在config.json中配置 cors")
        return cors_config
    
    @property
    def baostock_config(self) -> Dict[str, Any]:
        """获取Baostock配置"""
        baostock_config = self.config.get('baostock')
        if not baostock_config:
            raise ValueError("Baostock配置缺失，请在config.json中配置 baostock")
        return baostock_config
    
    @property
    def api_config(self) -> Dict[str, Any]:
        """获取API配置"""
        api_config = self.config.get('api')
        if not api_config:
            raise ValueError("API配置缺失，请在config.json中配置 api")
        return api_config
    
    @property
    def api_price_config(self) -> Dict[str, Any]:
        """获取API价格配置"""
        api_price_config = self.config.get('api_price')
        if not api_price_config:
            raise ValueError("API价格配置缺失，请在config.json中配置 api_price")
        return api_price_config
    
    def get_qwen_api_config(self) -> Dict[str, Any]:
        """从数据库获取Qwen API配置"""
        if self._qwen_api_config is not None:
            return self._qwen_api_config
        
        from app.db.database import get_config_value
        
        api_key = get_config_value('qwen_api_key')
        base_url = get_config_value('qwen_base_url')
        model = get_config_value('qwen_model') or get_config_value('qwen_model_name')
        
        if not api_key:
            raise ValueError("Qwen API密钥未配置，请在系统配置页面配置 qwen_api_key")
        if not base_url:
            raise ValueError("Qwen API地址未配置，请在系统配置页面配置 qwen_base_url")
        if not model:
            raise ValueError("Qwen 模型未配置，请在系统配置页面配置 qwen_model")
        
        self._qwen_api_config = {
            "api_key": api_key,
            "base_url": base_url,
            "model": model
        }
        return self._qwen_api_config


# 创建配置管理器实例
config_manager = ConfigManager()

# 导出配置
APP_CONFIG = config_manager.app_config
CORS_CONFIG = config_manager.cors_config
BAOSTOCK_CONFIG = config_manager.baostock_config
API_CONFIG = config_manager.api_config
API_PRICE_CONFIG = config_manager.api_price_config
get_qwen_api_config = config_manager.get_qwen_api_config