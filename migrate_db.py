"""
数据库迁移脚本
用于更新数据库表结构，添加analysis_log表和更新wyckoff_analysis表
"""

import pymysql
import json
import os

def migrate_database():
    """迁移数据库表结构"""
    try:
        # 直接从config.json读取数据库配置
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        db_config = config.get('database')
        if not db_config:
            raise ValueError("数据库配置缺失，请在config.json中配置 database")
        
        # 连接数据库
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        print("开始数据库迁移...")
        
        # 创建analysis_log表
        print("创建analysis_log表...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                code VARCHAR(10) NOT NULL,
                name VARCHAR(50) NOT NULL,
                start_date DATE NULL,
                end_date DATE NULL,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                chat_completion_id VARCHAR(100) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
        print("analysis_log表创建成功")
        
        # 为wyckoff_analysis表添加chat_completion_id字段
        print("为wyckoff_analysis表添加chat_completion_id字段...")
        try:
            cursor.execute('''
                ALTER TABLE wyckoff_analysis ADD COLUMN chat_completion_id VARCHAR(100) NULL;
            ''')
            print("chat_completion_id字段添加成功")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("chat_completion_id字段已存在，跳过")
            else:
                print(f"添加chat_completion_id字段失败: {str(e)}")
        
        # 移除wyckoff_analysis表的analysis_log_id字段（如果存在）
        print("移除wyckoff_analysis表的analysis_log_id字段...")
        try:
            cursor.execute('''
                ALTER TABLE wyckoff_analysis DROP COLUMN analysis_log_id;
            ''')
            print("analysis_log_id字段移除成功")
        except Exception as e:
            if "check that column/key exists" in str(e):
                print("analysis_log_id字段不存在，跳过")
            else:
                print(f"移除analysis_log_id字段失败: {str(e)}")
        
        # 移除外键约束（如果存在）
        print("移除外键约束...")
        try:
            cursor.execute('''
                ALTER TABLE wyckoff_analysis DROP FOREIGN KEY fk_analysis_log;
            ''')
            print("外键约束移除成功")
        except Exception as e:
            if "check that column/key exists" in str(e):
                print("外键约束不存在，跳过")
            else:
                print(f"移除外键约束失败: {str(e)}")
        
        # 修改字段长度
        print("修改字段长度...")
        try:
            cursor.execute('''
                ALTER TABLE wyckoff_analysis MODIFY COLUMN trend VARCHAR(200) NOT NULL;
            ''')
            print("trend字段长度修改成功")
        except Exception as e:
            print(f"修改trend字段长度失败: {str(e)}")
        
        try:
            cursor.execute('''
                ALTER TABLE wyckoff_analysis MODIFY COLUMN volume_pattern VARCHAR(200) NOT NULL;
            ''')
            print("volume_pattern字段长度修改成功")
        except Exception as e:
            print(f"修改volume_pattern字段长度失败: {str(e)}")
        
        try:
            cursor.execute('''
                ALTER TABLE wyckoff_analysis MODIFY COLUMN trade_signal VARCHAR(50) NOT NULL;
            ''')
            print("trade_signal字段长度修改成功")
        except Exception as e:
            print(f"修改trade_signal字段长度失败: {str(e)}")
        
        conn.commit()
        print("数据库迁移完成！")
        
    except Exception as e:
        print(f"数据库迁移失败: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate_database()
