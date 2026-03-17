"""
数据库模块
处理所有数据库操作
"""

import pymysql
from typing import List, Dict, Any
import json
import os
from app.config import config_manager

# 加载配置
CONFIG = config_manager.config

# 数据库配置
DB_CONFIG = CONFIG.get('database')
if not DB_CONFIG:
    raise ValueError("数据库配置缺失，请在config.json中配置 database")

# 验证数据库必要配置
required_db_keys = ['host', 'port', 'user', 'password', 'db']
for key in required_db_keys:
    if key not in DB_CONFIG:
        raise ValueError(f"数据库配置缺少必要字段: {key}")


# 数据库连接状态
DB_AVAILABLE = None


def check_db_connection():
    """检查数据库连接状态"""
    global DB_AVAILABLE
    if DB_AVAILABLE is None:
        try:
            conn = pymysql.connect(**DB_CONFIG)
            conn.ping()
            conn.close()
            DB_AVAILABLE = True
        except Exception as e:
            print(f"数据库连接失败: {str(e)}")
            DB_AVAILABLE = False
    return DB_AVAILABLE


def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


def init_database():
    """初始化数据库"""
    try:
        # 首先尝试连接数据库
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset=DB_CONFIG['charset']
        )
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['db']}")
        cursor.execute(f"USE {DB_CONFIG['db']}")
        
        # 创建股票基本信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                code VARCHAR(10) NOT NULL PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                is_hs300 TINYINT(1) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
        
        # 创建股票历史数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL,
                code VARCHAR(10) NOT NULL,
                open DECIMAL(10,2),
                high DECIMAL(10,2),
                low DECIMAL(10,2),
                close DECIMAL(10,2),
                volume DECIMAL(20,2),
                amount DECIMAL(20,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY idx_date_code (date, code)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
        
        # 创建威科夫分析结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wyckoff_analysis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                code VARCHAR(10) NOT NULL,
                name VARCHAR(50) NOT NULL,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
        
        # 移除wyckoff_analysis表的唯一键约束（如果存在）
        try:
            cursor.execute('''
                ALTER TABLE wyckoff_analysis DROP INDEX IF EXISTS idx_code_date;
            ''')
            print("移除wyckoff_analysis表的唯一键约束成功")
        except Exception as e:
            print(f"移除唯一键约束失败: {str(e)}")
        
        # 为已有的wyckoff_analysis表添加chat_completion_id字段
        try:
            cursor.execute('''
                ALTER TABLE wyckoff_analysis ADD COLUMN IF NOT EXISTS chat_completion_id VARCHAR(100) NULL;
            ''')
            print("为wyckoff_analysis表添加chat_completion_id字段成功")
        except Exception as e:
            print(f"添加chat_completion_id字段失败: {str(e)}")
        
        # 移除analysis_log_id字段（如果存在）
        try:
            cursor.execute('''
                ALTER TABLE wyckoff_analysis DROP COLUMN IF EXISTS analysis_log_id;
            ''')
            print("从wyckoff_analysis表移除analysis_log_id字段成功")
        except Exception as e:
            print(f"移除analysis_log_id字段失败: {str(e)}")
        
        # 移除外键约束（如果存在）
        try:
            cursor.execute('''
                ALTER TABLE wyckoff_analysis DROP FOREIGN KEY IF EXISTS fk_analysis_log;
            ''')
            print("从wyckoff_analysis表移除外键约束成功")
        except Exception as e:
            print(f"移除外键约束失败: {str(e)}")
        
        # 修改字段长度
        try:
            cursor.execute('''
                ALTER TABLE wyckoff_analysis MODIFY COLUMN trend VARCHAR(200) NOT NULL;
            ''')
            print("修改wyckoff_analysis表trend字段长度成功")
        except Exception as e:
            print(f"修改trend字段长度失败: {str(e)}")
        
        try:
            cursor.execute('''
                ALTER TABLE wyckoff_analysis MODIFY COLUMN volume_pattern VARCHAR(200) NOT NULL;
            ''')
            print("修改wyckoff_analysis表volume_pattern字段长度成功")
        except Exception as e:
            print(f"修改volume_pattern字段长度失败: {str(e)}")
        
        try:
            cursor.execute('''
                ALTER TABLE wyckoff_analysis MODIFY COLUMN trade_signal VARCHAR(50) NOT NULL;
            ''')
            print("修改wyckoff_analysis表trade_signal字段长度成功")
        except Exception as e:
            print(f"修改trade_signal字段长度失败: {str(e)}")
        
        # 创建系统配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                id INT AUTO_INCREMENT PRIMARY KEY,
                config_key VARCHAR(100) NOT NULL UNIQUE,
                config_value TEXT NOT NULL,
                description VARCHAR(255),
                parent INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
        
        # 创建分析日志表
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
        
        # 从初始化配置文件读取默认配置数据
        init_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'init_config.json')
        if os.path.exists(init_config_path):
            with open(init_config_path, 'r', encoding='utf-8') as f:
                init_config = json.load(f)
                system_config = init_config.get('system_config', {})
        else:
            system_config = CONFIG.get('system_config', {})
        
        # 插入顶级父级配置
        top_configs = system_config.get('top_configs', [])
        for config in top_configs:
            cursor.execute('''
                INSERT INTO system_config (config_key, config_value, description, parent)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    config_value = VALUES(config_value),
                    description = VALUES(description),
                    parent = VALUES(parent),
                    updated_at = CURRENT_TIMESTAMP
            ''', (config['config_key'], config['config_value'], config['description'], config['parent']))
        
        # 获取父级配置的ID映射
        parent_ids = {}
        for config in top_configs:
            cursor.execute('SELECT id FROM system_config WHERE config_key = %s', (config['config_key'],))
            result = cursor.fetchone()
            if result:
                parent_ids[config['config_key']] = result[0]
        
        # 插入qwen_model的子级配置
        model_configs = system_config.get('model_configs', [])
        for config in model_configs:
            parent_key = config['parent']
            parent_id = parent_ids.get(parent_key, 0)
            cursor.execute('''
                INSERT INTO system_config (config_key, config_value, description, parent)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    config_value = VALUES(config_value),
                    description = VALUES(description),
                    parent = VALUES(parent),
                    updated_at = CURRENT_TIMESTAMP
            ''', (config['config_key'], config['config_value'], config['description'], parent_id))
        
        # 插入价格配置
        price_configs = system_config.get('price_configs', [])
        for config in price_configs:
            parent_key = config['parent']
            parent_id = parent_ids.get(parent_key, 0)
            cursor.execute('''
                INSERT INTO system_config (config_key, config_value, description, parent)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    config_value = VALUES(config_value),
                    description = VALUES(description),
                    parent = VALUES(parent),
                    updated_at = CURRENT_TIMESTAMP
            ''', (config['config_key'], config['config_value'], config['description'], parent_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
        return False


def save_stock_to_db(stock: Dict[str, str]):
    """保存股票基本信息到数据库"""
    print(f"尝试保存股票到数据库: {stock}")
    if not check_db_connection():
        print("数据库连接不可用，跳过保存")
        return
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = '''
                    INSERT INTO stocks (code, name, is_hs300)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        name = VALUES(name),
                        is_hs300 = VALUES(is_hs300)
                '''
                cursor.execute(sql, (stock['code'], stock['name'], stock.get('is_hs300', 0)))
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"保存股票失败: {str(e)}")


def get_stock_name_from_db(code: str) -> str:
    """从数据库获取股票名称"""
    if not check_db_connection():
        return None
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT name FROM stocks WHERE code = %s', (code,))
                result = cursor.fetchone()
                return result[0] if result else None
        finally:
            conn.close()
    except Exception as e:
        print(f"获取股票名称失败: {str(e)}")
        return None


def save_stock_history_to_db(history_data: List[Dict[str, Any]]):
    """批量保存股票历史数据到数据库"""
    if not check_db_connection() or not history_data:
        return
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = '''
                    INSERT INTO stock_history (date, code, open, high, low, close, volume, amount)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        open = VALUES(open),
                        high = VALUES(high),
                        low = VALUES(low),
                        close = VALUES(close),
                        volume = VALUES(volume),
                        amount = VALUES(amount)
                '''
                for data in history_data:
                    cursor.execute(sql, (
                        data['date'],
                        data['code'],
                        data['open'],
                        data['high'],
                        data['low'],
                        data['close'],
                        data['volume'],
                        data['amount']
                    ))
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"数据库保存失败: {str(e)}")


def parse_price_value(value):
    """解析价格值，提取数字部分"""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, list):
        # 如果是列表，取第一个元素
        if value:
            return parse_price_value(value[0])
        return None
    if isinstance(value, str):
        # 提取数字部分
        import re
        # 匹配数字，包括小数点
        matches = re.findall(r'\d+\.?\d*', value)
        if matches:
            try:
                return float(matches[0])
            except:
                return None
    return None


def save_analysis_log(log_data: Dict[str, Any]) -> int:
    """保存分析日志到数据库"""
    if not check_db_connection():
        return 0
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 验证日志数据
                required_fields = ['code', 'name', 'prompt', 'response']
                for field in required_fields:
                    if field not in log_data:
                        print(f"日志数据缺少必要字段: {field}")
                        return 0
                
                # 准备参数
                params = (
                    log_data['code'],
                    log_data['name'],
                    log_data.get('start_date'),
                    log_data.get('end_date'),
                    log_data['prompt'],
                    log_data['response'],
                    log_data.get('chat_completion_id')
                )
                
                # 插入日志数据
                sql = '''
                    INSERT INTO analysis_log 
                    (code, name, start_date, end_date, prompt, response, chat_completion_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                '''
                
                cursor.execute(sql, params)
                conn.commit()
                
                # 返回插入的日志ID
                return cursor.lastrowid
        finally:
            conn.close()
    except Exception as e:
        print(f"保存分析日志失败: {str(e)}")
        return 0

def save_wyckoff_analysis_to_db(analysis: Dict[str, Any], chat_completion_id: str = ''):
    """保存威科夫分析结果到数据库"""
    if not check_db_connection():
        return
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 验证分析数据
                required_fields = ['code', 'name', 'end_date', 'trend', 'volume_pattern', 'signal', 'confidence', 'analysis_details']
                for field in required_fields:
                    if field not in analysis:
                        print(f"分析数据缺少必要字段: {field}")
                        return
                
                # 解析价格值
                support_level = parse_price_value(analysis.get('support_level'))
                resistance_level = parse_price_value(analysis.get('resistance_level'))
                
                # 确保confidence是标量值
                confidence = analysis['confidence']
                if isinstance(confidence, (list, dict)):
                    confidence = 0.5  # 默认值
                
                # 确保analysis_details是可序列化的
                analysis_details = analysis['analysis_details']
                if isinstance(analysis_details, str):
                    # 如果已经是字符串，直接使用
                    analysis_details_str = analysis_details
                else:
                    # 否则序列化
                    analysis_details_str = json.dumps(analysis_details, ensure_ascii=False)
                
                # 检查是否已存在相同chat_completion_id的记录
                if chat_completion_id:
                    cursor.execute('''
                        SELECT id FROM wyckoff_analysis WHERE chat_completion_id = %s
                    ''', (chat_completion_id,))
                    existing_id = cursor.fetchone()
                    
                    if existing_id:
                        # 如果存在，更新记录
                        params = (
                            analysis['trend'],
                            analysis['volume_pattern'],
                            support_level,
                            resistance_level,
                            analysis['signal'],
                            confidence,
                            analysis_details_str,
                            analysis.get('token_usage', 0),
                            analysis.get('cost', 0.00),
                            chat_completion_id
                        )
                        sql = '''
                            UPDATE wyckoff_analysis 
                            SET trend = %s, volume_pattern = %s, support_level = %s, 
                                resistance_level = %s, trade_signal = %s, confidence = %s, 
                                analysis_details = %s, token_usage = %s, cost = %s
                            WHERE chat_completion_id = %s
                        '''
                        cursor.execute(sql, params)
                        print(f"更新威科夫分析结果成功，chat_completion_id: {chat_completion_id}")
                    else:
                        # 如果不存在，插入新记录
                        params = (
                            analysis['code'],
                            analysis['name'],
                            analysis.get('start_date'),
                            analysis['end_date'],
                            analysis['trend'],
                            analysis['volume_pattern'],
                            support_level,
                            resistance_level,
                            analysis['signal'],
                            confidence,
                            analysis_details_str,
                            analysis.get('token_usage', 0),
                            analysis.get('cost', 0.00),
                            chat_completion_id
                        )
                        sql = '''
                            INSERT INTO wyckoff_analysis 
                            (code, name, start_date, end_date, trend, volume_pattern, support_level, resistance_level, trade_signal, confidence, analysis_details, token_usage, cost, chat_completion_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        '''
                        cursor.execute(sql, params)
                        print(f"插入威科夫分析结果成功，chat_completion_id: {chat_completion_id}")
                else:
                    # 没有chat_completion_id，直接插入新记录
                    params = (
                        analysis['code'],
                        analysis['name'],
                        analysis.get('start_date'),
                        analysis['end_date'],
                        analysis['trend'],
                        analysis['volume_pattern'],
                        support_level,
                        resistance_level,
                        analysis['signal'],
                        confidence,
                        analysis_details_str,
                        analysis.get('token_usage', 0),
                        analysis.get('cost', 0.00),
                        chat_completion_id
                    )
                    sql = '''
                        INSERT INTO wyckoff_analysis 
                        (code, name, start_date, end_date, trend, volume_pattern, support_level, resistance_level, trade_signal, confidence, analysis_details, token_usage, cost, chat_completion_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
                    cursor.execute(sql, params)
                    print(f"插入威科夫分析结果成功，无chat_completion_id")
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"保存威科夫分析结果失败: {str(e)}")
        print(f"分析数据: {analysis}")


def get_analysis_history(code: str = None, page: int = 1, page_size: int = 10, search: str = None, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
    """获取分析历史记录"""
    if not check_db_connection():
        return {"total": 0, "items": []}
    
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 构建查询条件
                where_clauses = []
                params = []
                
                if code:
                    # 提取股票代码的纯数字部分，处理带前缀的情况
                    import re
                    pure_code = re.sub(r'^[a-z]+\.', '', code, flags=re.IGNORECASE)
                    where_clauses.append("(code = %s OR code = %s)")
                    params.extend([code, pure_code])
                    print(f"查询股票代码: {code}, 纯数字代码: {pure_code}")
                
                if search:
                    where_clauses.append("(code LIKE %s OR name LIKE %s)")
                    params.extend([f'%{search}%', f'%{search}%'])
                
                if start_date:
                    where_clauses.append("end_date >= %s")
                    params.append(start_date)
                
                if end_date:
                    where_clauses.append("end_date <= %s")
                    params.append(end_date)
                
                where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
                # 获取总数
                count_sql = f"SELECT COUNT(*) FROM wyckoff_analysis WHERE {where_clause}"
                cursor.execute(count_sql, params)
                total = cursor.fetchone()[0]
                
                # 获取分页数据
                offset = (page - 1) * page_size
                query_params = params + [page_size, offset]
                query_sql = f'''
                    SELECT id, code, name, start_date, end_date, trend, volume_pattern, 
                           support_level, resistance_level, trade_signal, confidence, 
                           analysis_details, token_usage, cost, chat_completion_id, created_at
                    FROM wyckoff_analysis
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                '''
                cursor.execute(query_sql, query_params)
                rows = cursor.fetchall()
                
                # 格式化数据 - 使用元组索引访问
                items = []
                for row in rows:
                    # 处理analysis_details字段
                    analysis_details = None
                    if row[11]:
                        try:
                            analysis_details = json.loads(row[11])
                        except Exception as e:
                            print(f"解析 analysis_details 失败: {str(e)}")
                            # 如果解析失败，直接使用原始字符串
                            analysis_details = row[11]
                    
                    items.append({
                        "id": row[0],
                        "code": row[1],
                        "name": row[2],
                        "start_date": str(row[3]) if row[3] else None,
                        "end_date": str(row[4]) if row[4] else None,
                        "trend": row[5],
                        "volume_pattern": row[6],
                        "support_level": row[7],
                        "resistance_level": row[8],
                        "signal": row[9],
                        "confidence": float(row[10]) if row[10] is not None else 0.0,
                        "analysis_details": analysis_details,
                        "token_usage": row[12] if len(row) > 12 else 0,
                        "cost": float(row[13]) if len(row) > 13 and row[13] is not None else 0.00,
                        "chat_completion_id": row[14] if len(row) > 14 else '',
                        "created_at": str(row[15]) if len(row) > 15 else str(row[14])
                    })
                
                return {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "items": items
                }
        finally:
            conn.close()
    except Exception as e:
        print(f"get_analysis_history获取分析历史失败: {str(e)}")
        return {"total": 0, "page": page, "page_size": page_size, "items": []}


def get_analysis_logs(code: str = None, page: int = 1, page_size: int = 10, search: str = None, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
    """获取分析日志记录"""
    if not check_db_connection():
        return {"total": 0, "page": page, "page_size": page_size, "items": []}
    
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 构建查询条件
                where_clauses = []
                params = []
                
                if code:
                    # 提取股票代码的纯数字部分，处理带前缀的情况
                    import re
                    pure_code = re.sub(r'^[a-z]+\.', '', code, flags=re.IGNORECASE)
                    where_clauses.append("(code = %s OR code = %s)")
                    params.extend([code, pure_code])
                
                if search:
                    where_clauses.append("(code LIKE %s OR name LIKE %s)")
                    params.extend([f'%{search}%', f'%{search}%'])
                
                if start_date:
                    where_clauses.append("created_at >= %s")
                    params.append(f"{start_date} 00:00:00")
                
                if end_date:
                    where_clauses.append("created_at <= %s")
                    params.append(f"{end_date} 23:59:59")
                
                where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
                
                # 获取总数
                count_sql = f"SELECT COUNT(*) FROM analysis_log WHERE {where_clause}"
                cursor.execute(count_sql, params)
                total = cursor.fetchone()[0]
                
                # 获取分页数据
                offset = (page - 1) * page_size
                query_params = params + [page_size, offset]
                cursor.execute(f'''
                    SELECT id, code, name, start_date, end_date, prompt, response, 
                           chat_completion_id, created_at
                    FROM analysis_log
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                ''', query_params)
                rows = cursor.fetchall()
                
                # 格式化数据
                items = []
                for row in rows:
                    items.append({
                        "id": row[0],
                        "code": row[1],
                        "name": row[2],
                        "start_date": str(row[3]) if row[3] else None,
                        "end_date": str(row[4]) if row[4] else None,
                        "prompt": row[5],
                        "response": row[6],
                        "chat_completion_id": row[7] if len(row) > 7 else '',
                        "created_at": str(row[8]) if len(row) > 8 else str(row[7])
                    })
                
                return {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "items": items
                }
        finally:
            conn.close()
    except Exception as e:
        print(f"获取分析日志失败: {str(e)}")
        return {"total": 0, "page": page, "page_size": page_size, "items": []}


def get_analysis_log_by_id(log_id: int) -> Dict[str, Any]:
    """根据ID获取分析日志"""
    if not check_db_connection():
        return {}
    
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT id, code, name, start_date, end_date, prompt, response, 
                           chat_completion_id, created_at
                    FROM analysis_log
                    WHERE id = %s
                ''', (log_id,))
                row = cursor.fetchone()
                
                if not row:
                    return {}
                
                return {
                    "id": row[0],
                    "code": row[1],
                    "name": row[2],
                    "start_date": str(row[3]) if row[3] else None,
                    "end_date": str(row[4]) if row[4] else None,
                    "prompt": row[5],
                    "response": row[6],
                    "chat_completion_id": row[7] if len(row) > 7 else '',
                    "created_at": str(row[8]) if len(row) > 8 else str(row[7])
                }
        finally:
            conn.close()
    except Exception as e:
        print(f"获取分析日志失败: {str(e)}")
        return {}


def get_screening_history(limit: int = 50) -> Dict[str, Any]:
    """获取筛选历史记录"""
    if not check_db_connection():
        return {"message": "数据库不可用", "records": []}
    print(f"获取筛选历史记录，limit: {limit}")
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = '''
                    SELECT * FROM wyckoff_analysis
                    ORDER BY created_at DESC
                    LIMIT %s
                '''
                cursor.execute(sql, (limit,))
                records = cursor.fetchall()
                
                # 转换为字典格式
                result = []
                for record in records:
                    if record.get('analysis_details'):
                        try:
                            record['analysis_details'] = json.loads(record['analysis_details'])
                        except:
                            pass
                    result.append(record)
                
                return {"total": len(result), "records": result}
        finally:
            conn.close()
    except Exception as e:
        raise Exception(f"获取历史记录失败: {str(e)}")


def get_hs300_stocks_from_db(page: int = 1, page_size: int = 10, search: str = None) -> Dict[str, Any]:
    """从数据库获取沪深300成分股（支持分页和搜索）"""
    if not check_db_connection():
        return {"total": 0, "items": []}
    
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 构建查询条件
                where_clause = "is_hs300 = 1"
                params = []
                
                if search:
                    where_clause += " AND (code LIKE %s OR name LIKE %s)"
                    params.extend([f'%{search}%', f'%{search}%'])
                
                # 获取总数
                count_sql = f"SELECT COUNT(*) FROM stocks WHERE {where_clause}"
                cursor.execute(count_sql, params)
                total = cursor.fetchone()[0]
                
                # 获取分页数据
                offset = (page - 1) * page_size
                query_params = params + [page_size, offset]
                cursor.execute(f'''
                    SELECT code, name, is_hs300, created_at, updated_at
                    FROM stocks
                    WHERE {where_clause}
                    ORDER BY code
                    LIMIT %s OFFSET %s
                ''', query_params)
                rows = cursor.fetchall()
                
                items = [
                    {
                        "code": row[0],
                        "name": row[1],
                        "is_hs300": bool(row[2]),
                        "created_at": str(row[3]) if row[3] else None,
                        "updated_at": str(row[4]) if row[4] else None
                    }
                    for row in rows
                ]
                
                return {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "items": items
                }
        finally:
            conn.close()
    except Exception as e:
        print(f"获取沪深300股票失败: {str(e)}")
        return {"total": 0, "items": []}


def get_config_value(key: str, default=None) -> str:
    """获取系统配置值"""
    if not check_db_connection():
        return default
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT config_value FROM system_config WHERE config_key = %s', (key,))
                result = cursor.fetchone()
                return result[0] if result else default
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
                        INSERT INTO system_config (config_key, config_value, description)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            config_value = VALUES(config_value),
                            description = VALUES(description),
                            updated_at = CURRENT_TIMESTAMP
                    '''
                    cursor.execute(sql, (key, value, description))
                else:
                    sql = '''
                        INSERT INTO system_config (config_key, config_value)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE
                            config_value = VALUES(config_value),
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


def get_all_configs() -> List[Dict[str, Any]]:
    """获取所有配置"""
    if not check_db_connection():
        return []
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = '''
                    SELECT id, config_key, config_value, description, parent, created_at, updated_at
                    FROM system_config
                    ORDER BY parent, config_key
                '''
                cursor.execute(sql)
                rows = cursor.fetchall()
                # 使用元组索引访问
                return [
                    {
                        "id": row[0],
                        "config_key": row[1],
                        "config_value": row[2],
                        "description": row[3],
                        "parent": row[4],
                        "created_at": str(row[5]) if row[5] else None,
                        "updated_at": str(row[6]) if row[6] else None
                    }
                    for row in rows
                ]
        finally:
            conn.close()
    except Exception as e:
        print(f"获取所有配置失败: {str(e)}")
        return []