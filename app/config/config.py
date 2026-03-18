"""
配置模块
包含系统所有配置信息
"""

import json
import os
from typing import Dict, Any


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
    def llm_model_config(self) -> Dict[str, Any]:
        """获取LLM模型配置"""
        llm_model_config = self.config.get('llm_model_config')
        if not llm_model_config:
            raise ValueError("LLM模型配置缺失，请在config.json中配置 llm_model_config")
        return llm_model_config
    
    def get_qwen_api_config(self) -> Dict[str, Any]:
        """从数据库获取Qwen API配置"""
        if self._qwen_api_config is not None:
            return self._qwen_api_config
        
        from app.db.config import get_config_value
        
        api_key = get_config_value('qwen_api_key', '')
        base_url = get_config_value('qwen_base_url', '')
        model = get_config_value('qwen_model_name', '')
        
        if not api_key:
            raise ValueError("Qwen API密钥未配置，请在系统配置页面配置 qwen_api_key")
        if not base_url:
            raise ValueError("Qwen API地址未配置，请在系统配置页面配置 qwen_base_url")
        if not model:
            raise ValueError("Qwen 模型未配置，请在系统配置页面配置 qwen_model_name")
        
        self._qwen_api_config = {
            "api_key": api_key,
            "base_url": base_url,
            "model": model
        }
        return self._qwen_api_config
    
    def get_longport_config(self) -> Dict[str, Any]:
        """从数据库获取LongPort配置"""
        from app.db.config import get_config_value
        
        app_key = get_config_value('longport_app_key', '')
        app_secret = get_config_value('longport_app_secret', '')
        access_token = get_config_value('longport_access_token', '')
        region = get_config_value('longport_region', 'cn')
        
        if not app_key:
            raise ValueError("LongPort App Key未配置，请在系统配置页面配置 longport_app_key")
        if not app_secret:
            raise ValueError("LongPort App Secret未配置，请在系统配置页面配置 longport_app_secret")
        if not access_token:
            raise ValueError("LongPort Access Token未配置，请在系统配置页面配置 longport_access_token")
        
        return {
            "app_key": app_key,
            "app_secret": app_secret,
            "access_token": access_token,
            "region": region
        }


# 创建配置管理器实例
config_manager = ConfigManager()

# 导出配置
APP_CONFIG = config_manager.app_config
CORS_CONFIG = config_manager.cors_config
BAOSTOCK_CONFIG = config_manager.baostock_config
LLM_MODEL_CONFIG = config_manager.llm_model_config
get_qwen_api_config = config_manager.get_qwen_api_config
get_longport_config = config_manager.get_longport_config