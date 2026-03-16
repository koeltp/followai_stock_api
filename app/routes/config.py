"""
配置路由模块
包含配置相关路由
"""

from fastapi import APIRouter, HTTPException
from app.db import get_all_configs, update_config_value

# 创建路由器
router = APIRouter(prefix="/config")


@router.get("")
def get_config_endpoint():
    """获取所有系统配置"""
    try:
        configs = get_all_configs()
        return {"configs": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.post("")
def update_config_endpoint(config: dict):
    """更新系统配置"""
    try:
        config_key = config.get('config_key')
        config_value = config.get('config_value')
        description = config.get('description')
        
        if not config_key or config_value is None:
            raise HTTPException(status_code=400, detail="配置键和值不能为空")
        
        success = update_config_value(config_key, config_value, description)
        if success:
            return {"message": "配置更新成功"}
        else:
            raise HTTPException(status_code=500, detail="配置更新失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")