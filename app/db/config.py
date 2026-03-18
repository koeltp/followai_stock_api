#!/usr/bin/env python3
"""
系统配置相关操作模块
"""

from app.db.connection import get_db_connection, check_db_connection


def get_config_value(key: str, default=None) -> str:
    """获取系统配置值"""
    if not check_db_connection():
        return default
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 尝试使用 key_name 和 key_value 字段
                try:
                    cursor.execute('SELECT key_value FROM system_config WHERE key_name = %s', (key,))
                    result = cursor.fetchone()
                    return result['key_value'] if result else default
                except Exception as e:
                    # 如果失败，尝试使用旧的字段名 config_key 和 config_value
                    print(f"使用新字段名失败: {str(e)}")
                    cursor.execute('SELECT config_value FROM system_config WHERE config_key = %s', (key,))
                    result = cursor.fetchone()
                    return result['config_value'] if result else default
        finally:
            conn.close()
    except Exception as e:
        print(f"获取配置失败: {str(e)}")
        return default


def update_config_value(key: str, value: str, description: str = None) -> bool:
    """更新系统配置"""
    if not check_db_connection():
        return False
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                if description:
                    sql = '''
                        INSERT INTO system_config (key_name, key_value, description)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            key_value = VALUES(key_value),
                            description = VALUES(description),
                            updated_at = CURRENT_TIMESTAMP
                    '''
                    cursor.execute(sql, (key, value, description))
                else:
                    sql = '''
                        INSERT INTO system_config (key_name, key_value)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE
                            key_value = VALUES(key_value),
                            updated_at = CURRENT_TIMESTAMP
                    '''
                    cursor.execute(sql, (key, value))
            conn.commit()
            return True
        finally:
            conn.close()
    except Exception as e:
        print(f"更新配置失败: {str(e)}")
        return False


def get_all_configs() -> list:
    """获取所有配置"""
    if not check_db_connection():
        return []
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = '''
                    SELECT id, key_name, key_value, description, parent, created_at, updated_at
                    FROM system_config
                    ORDER BY parent, key_name
                '''
                cursor.execute(sql)
                rows = cursor.fetchall()
                # 使用字典键访问
                return [
                    {
                        "id": row['id'],
                        "key_name": row['key_name'],
                        "key_value": row['key_value'],
                        "description": row['description'],
                        "parent": row['parent'],
                        "created_at": str(row['created_at']) if row['created_at'] else None,
                        "updated_at": str(row['updated_at']) if row['updated_at'] else None
                    }
                    for row in rows
                ]
        finally:
            conn.close()
    except Exception as e:
        print(f"获取配置列表失败: {str(e)}")
        return []
