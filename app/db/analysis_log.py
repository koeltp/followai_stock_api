#!/usr/bin/env python3
"""
分析日志相关操作模块
"""

import re
from app.db.connection import get_db_connection, check_db_connection


def save_analysis_log(log_data):
    """保存分析日志到数据库"""
    if not check_db_connection():
        return 0
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 获取股票的 stock_id
                code = log_data['code']
                cursor.execute('SELECT id FROM stocks WHERE code = %s', (code,))
                result = cursor.fetchone()
                if not result:
                    print(f"股票代码 {code} 不存在，跳过保存")
                    return 0
                stock_id = result['id']
                
                # 准备参数
                params = (
                    stock_id,
                    log_data.get('start_date'),
                    log_data.get('end_date'),
                    log_data['prompt'],
                    log_data['response'],
                    log_data.get('chat_completion_id')
                )
                
                # 插入日志数据
                sql = '''
                    INSERT INTO analysis_log 
                    (stock_id, start_date, end_date, prompt, response, chat_completion_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                '''
                
                cursor.execute(sql, params)
                conn.commit()
                
                print(f"保存分析日志成功，股票代码: {code}")
                return cursor.lastrowid
        finally:
            conn.close()
    except Exception as e:
        print(f"保存分析日志失败: {str(e)}")
        return 0


def get_analysis_logs(code: str = None, page: int = 1, page_size: int = 10, search: str = None, start_date: str = None, end_date: str = None) -> dict:
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
                    pure_code = re.sub(r'^[a-z]+\.', '', code, flags=re.IGNORECASE)
                    where_clauses.append("(s.code = %s OR s.code = %s)")
                    params.extend([code, pure_code])
                
                if search:
                    where_clauses.append("(s.code LIKE %s OR s.name LIKE %s)")
                    params.extend([f'%{search}%', f'%{search}%'])
                
                if start_date:
                    where_clauses.append("al.created_at >= %s")
                    params.append(f"{start_date} 00:00:00")
                
                if end_date:
                    where_clauses.append("al.created_at <= %s")
                    params.append(f"{end_date} 23:59:59")
                
                where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
                # 获取总数
                count_sql = f"SELECT COUNT(*) FROM analysis_log al JOIN stocks s ON al.stock_id = s.id WHERE {where_clause}"
                cursor.execute(count_sql, params)
                total = cursor.fetchone()['COUNT(*)']
                
                # 获取分页数据
                offset = (page - 1) * page_size
                query_params = params + [page_size, offset]
                cursor.execute(f'''
                    SELECT al.id, s.code, s.name, al.start_date, al.end_date, al.prompt, al.response, 
                           al.chat_completion_id, al.created_at
                    FROM analysis_log al
                    JOIN stocks s ON al.stock_id = s.id
                    WHERE {where_clause}
                    ORDER BY al.created_at DESC
                    LIMIT %s OFFSET %s
                ''', query_params)
                rows = cursor.fetchall()
                
                # 格式化数据
                items = []
                for row in rows:
                    items.append({
                        "id": row['id'],
                        "code": row['code'],
                        "name": row['name'],
                        "start_date": str(row['start_date']) if row['start_date'] else None,
                        "end_date": str(row['end_date']) if row['end_date'] else None,
                        "prompt": row['prompt'],
                        "response": row['response'],
                        "chat_completion_id": row['chat_completion_id'] if 'chat_completion_id' in row else '',
                        "created_at": str(row['created_at']) if 'created_at' in row else ''
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
        print(f"get_analysis_logs获取分析日志失败: {str(e)}")
        return {"total": 0, "page": page, "page_size": page_size, "items": []}


def get_analysis_log_by_id(log_id: int) -> dict:
    """根据ID获取分析日志"""
    if not check_db_connection():
        return {}
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT al.id, s.code, s.name, al.start_date, al.end_date, al.prompt, al.response, 
                           al.chat_completion_id, al.created_at
                    FROM analysis_log al
                    JOIN stocks s ON al.stock_id = s.id
                    WHERE al.id = %s
                ''', (log_id,))
                row = cursor.fetchone()
                
                if not row:
                    return {}
                
                return {
                    "id": row['id'],
                    "code": row['code'],
                    "name": row['name'],
                    "start_date": str(row['start_date']) if row['start_date'] else None,
                    "end_date": str(row['end_date']) if row['end_date'] else None,
                    "prompt": row['prompt'],
                    "response": row['response'],
                    "chat_completion_id": row['chat_completion_id'] if 'chat_completion_id' in row else '',
                    "created_at": str(row['created_at']) if 'created_at' in row else ''
                }
        finally:
            conn.close()
    except Exception as e:
        print(f"获取分析日志失败: {str(e)}")
        return {}
