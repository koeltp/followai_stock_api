#!/usr/bin/env python3
"""
数据库连接管理模块
"""

import pymysql
from app.config import config_manager

# 加载配置
CONFIG = config_manager.config
DB_CONFIG = CONFIG.get('database')


def get_db_connection():
    """获取数据库连接"""
    try:
        # 先尝试连接到数据库
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            db=DB_CONFIG['db'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            init_command="SET time_zone = '+8:00'"
        )
        return conn
    except pymysql.err.OperationalError as e:
        # 检查是否是数据库不存在的错误
        if "Unknown database" in str(e):
            print(f"数据库 {DB_CONFIG['db']} 不存在，尝试创建...")
            try:
                # 先连接到 MySQL 服务器（不指定数据库）
                conn = pymysql.connect(
                    host=DB_CONFIG['host'],
                    port=DB_CONFIG['port'],
                    user=DB_CONFIG['user'],
                    password=DB_CONFIG['password'],
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor
                )
                # 创建数据库
                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['db']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                conn.close()
                print(f"数据库 {DB_CONFIG['db']} 创建成功")
                # 再次尝试连接到新创建的数据库
                conn = pymysql.connect(
                    host=DB_CONFIG['host'],
                    port=DB_CONFIG['port'],
                    user=DB_CONFIG['user'],
                    password=DB_CONFIG['password'],
                    db=DB_CONFIG['db'],
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor,
                    init_command="SET time_zone = '+8:00'"
                )
                return conn
            except Exception as create_error:
                print(f"创建数据库失败: {str(create_error)}")
                return None
        else:
            print(f"获取数据库连接失败: {str(e)}")
            return None
    except Exception as e:
        print(f"获取数据库连接失败: {str(e)}")
        return None


def check_db_connection():
    """检查数据库连接是否正常"""
    conn = None
    try:
        conn = get_db_connection()
        return conn is not None
    finally:
        if conn:
            conn.close()
