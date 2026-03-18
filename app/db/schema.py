#!/usr/bin/env python3
"""
数据库表结构定义和初始化模块
"""

import os
import json
from app.db.connection import get_db_connection


def init_database():
    """初始化数据库表结构"""
    try:
        conn = get_db_connection()
        if not conn:
            print("数据库连接失败，无法初始化")
            return False
        try:
            with conn.cursor() as cursor:
                # 检查 system_config 表是否已有数据
                cursor.execute('SELECT COUNT(*) FROM system_config')
                config_count = cursor.fetchone()['COUNT(*)']
                is_new_database = config_count == 0
                
                # 创建股票表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stocks (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        code VARCHAR(20) NOT NULL UNIQUE,
                        name VARCHAR(100) NOT NULL,
                        market_type VARCHAR(10) NOT NULL DEFAULT 'A',
                        is_hs300 TINYINT(1) DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                
                # 创建股票历史数据表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stock_history (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        stock_id INT NOT NULL,
                        date DATE NOT NULL,
                        open DECIMAL(10,2),
                        high DECIMAL(10,2),
                        low DECIMAL(10,2),
                        close DECIMAL(10,2),
                        volume DECIMAL(20,2),
                        amount DECIMAL(20,2),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE KEY idx_date_stock_id (date, stock_id),
                        FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                
                # 创建威科夫分析结果表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS wyckoff_analysis (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        stock_id INT NOT NULL,
                        start_date DATE NULL,
                        end_date DATE NULL,
                        trend VARCHAR(200) NOT NULL,
                        volume_pattern VARCHAR(200) NOT NULL,
                        support_level DECIMAL(10,2),
                        resistance_level DECIMAL(10,2),
                        trade_signal VARCHAR(50) NOT NULL,
                        confidence DECIMAL(5,2) NOT NULL,
                        analysis_details TEXT,
                        token_usage INT DEFAULT 0,
                        cost DECIMAL(10,2) DEFAULT 0.00,
                        chat_completion_id VARCHAR(100) NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                
                # 创建系统配置表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_config (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        key_name VARCHAR(50) NOT NULL UNIQUE,
                        key_value TEXT NOT NULL,
                        description VARCHAR(255),
                        parent VARCHAR(50) DEFAULT '0',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                
                # 创建分析日志表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_log (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        stock_id INT NOT NULL,
                        start_date DATE NULL,
                        end_date DATE NULL,
                        prompt TEXT NOT NULL,
                        response TEXT NOT NULL,
                        chat_completion_id VARCHAR(100) NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                
                # 只有在新创建的数据库中才执行 SQL 脚本
                if is_new_database:
                    # 执行 system_config.sql 脚本插入配置数据
                    sql_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql', 'system_config.sql')
                    print(f"查找 SQL 脚本: {sql_file_path}")
                    if os.path.exists(sql_file_path):
                        print(f"找到 SQL 脚本: {sql_file_path}")
                        try:
                            with open(sql_file_path, 'r', encoding='utf-8') as f:
                                sql_script = f.read()
                            
                            # 分割 SQL 语句并执行
                            sql_statements = sql_script.split(';')
                            for statement in sql_statements:
                                statement = statement.strip()
                                if statement:
                                    try:
                                        # 替换数据库名，确保使用正确的数据库
                                        statement = statement.replace('xszb.', '')
                                        cursor.execute(statement)
                                        print(f"执行 SQL 语句成功")
                                    except Exception as e:
                                        print(f"执行 SQL 语句失败: {str(e)}")
                                        continue
                            print("配置数据插入成功")
                        except Exception as e:
                            print(f"执行 SQL 脚本失败: {str(e)}")
                    else:
                        print(f"SQL 脚本不存在: {sql_file_path}")
                else:
                    print("数据库已有配置数据，跳过执行 SQL 脚本")
            
            conn.commit()
            print("数据库初始化成功")
            return True
        finally:
            conn.close()
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
        return False
