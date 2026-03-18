#!/usr/bin/env python3
"""
分析历史相关操作模块
"""

import json
import re
from app.db.connection import get_db_connection, check_db_connection


def save_wyckoff_analysis_to_db(analysis: dict, chat_completion_id: str = ''):
    """保存威科夫分析结果到数据库"""
    if not check_db_connection():
        return
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 获取股票的 stock_id
                code = analysis['code']
                cursor.execute('SELECT id FROM stocks WHERE code = %s', (code,))
                result = cursor.fetchone()
                if not result:
                    print(f"股票代码 {code} 不存在，跳过保存")
                    return
                stock_id = result['id']
                
                # 直接保存分析记录，不检查重复
                # 每次分析都保存，即使时间范围相同
                
                # 处理 support_level 和 resistance_level
                support_level = analysis.get('support_level')
                resistance_level = analysis.get('resistance_level')
                try:
                    if support_level:
                        support_level = float(support_level)
                    if resistance_level:
                        resistance_level = float(resistance_level)
                except (ValueError, TypeError):
                    support_level = None
                    resistance_level = None
                
                # 处理 confidence
                confidence = analysis.get('confidence', 0)
                try:
                    confidence = float(confidence)
                except (ValueError, TypeError):
                    confidence = 0.0
                
                # 处理 analysis_details
                analysis_details = analysis.get('analysis_details', {})
                analysis_details_str = json.dumps(analysis_details, ensure_ascii=False)
                
                # 检查是否已有相同 chat_completion_id 的记录
                cursor.execute('''
                    SELECT id FROM wyckoff_analysis 
                    WHERE chat_completion_id = %s
                ''', (chat_completion_id,))
                existing = cursor.fetchone()
                if existing:
                    # 更新现有记录
                    update_wyckoff_analysis(cursor, stock_id, analysis, support_level, resistance_level, confidence, analysis_details_str, chat_completion_id, existing['id'])
                    print(f"更新威科夫分析结果成功，chat_completion_id: {chat_completion_id}")
                else:
                    # 如果不存在，插入新记录
                    insert_wyckoff_analysis(cursor, stock_id, analysis, support_level, resistance_level, confidence, analysis_details_str, chat_completion_id)
                    print(f"插入威科夫分析结果成功，chat_completion_id: {chat_completion_id}")
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"保存威科夫分析结果失败: {str(e)}")
        print(f"分析数据: {analysis}")


def insert_wyckoff_analysis(cursor, stock_id, analysis, support_level, resistance_level, confidence, analysis_details_str, chat_completion_id):
    """插入威科夫分析结果"""
    params = (
        stock_id,
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
        (stock_id, start_date, end_date, trend, volume_pattern, support_level, resistance_level, trade_signal, confidence, analysis_details, token_usage, cost, chat_completion_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cursor.execute(sql, params)


def update_wyckoff_analysis(cursor, stock_id, analysis, support_level, resistance_level, confidence, analysis_details_str, chat_completion_id, analysis_id):
    """更新威科夫分析结果"""
    params = (
        stock_id,
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
        chat_completion_id,
        analysis_id
    )
    sql = '''
        UPDATE wyckoff_analysis 
        SET stock_id = %s, start_date = %s, end_date = %s, trend = %s, 
            volume_pattern = %s, support_level = %s, resistance_level = %s, 
            trade_signal = %s, confidence = %s, analysis_details = %s, 
            token_usage = %s, cost = %s, chat_completion_id = %s
        WHERE id = %s
    '''
    cursor.execute(sql, params)


def get_analysis_history(code: str = None, page: int = 1, page_size: int = 10, search: str = None, start_date: str = None, end_date: str = None, market: str = None) -> dict:
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
                    # 直接使用股票代码查询
                    where_clauses.append("s.code = %s")
                    params.append(code)
                
                if search:
                    where_clauses.append("(s.code LIKE %s OR s.name LIKE %s)")
                    params.extend([f'%{search}%', f'%{search}%'])
                
                if start_date:
                    where_clauses.append("wa.end_date >= %s")
                    params.append(start_date)
                
                if end_date:
                    where_clauses.append("wa.end_date <= %s")
                    params.append(end_date)
                
                if market:
                    # 直接使用 market_type 字段过滤
                    where_clauses.append("s.market_type = %s")
                    params.append(market)
                
                where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
                # 获取总数
                count_sql = f"SELECT COUNT(*) FROM wyckoff_analysis wa JOIN stocks s ON wa.stock_id = s.id WHERE {where_clause}"
                cursor.execute(count_sql, params)
                total = cursor.fetchone()['COUNT(*)']
                
                # 获取分页数据
                offset = (page - 1) * page_size
                query_params = params + [page_size, offset]
                query_sql = f'''
                    SELECT wa.id, s.code, s.name, wa.start_date, wa.end_date, wa.trend, wa.volume_pattern, 
                           wa.support_level, wa.resistance_level, wa.trade_signal, wa.confidence, 
                           wa.analysis_details, wa.token_usage, wa.cost, wa.chat_completion_id, wa.created_at
                    FROM wyckoff_analysis wa
                    JOIN stocks s ON wa.stock_id = s.id
                    WHERE {where_clause}
                    ORDER BY wa.created_at DESC
                    LIMIT %s OFFSET %s
                '''
                cursor.execute(query_sql, query_params)
                rows = cursor.fetchall()
                
                # 格式化数据
                items = []
                for row in rows:
                    # 处理analysis_details字段
                    analysis_details = None
                    if row['analysis_details']:
                        try:
                            analysis_details = json.loads(row['analysis_details'])
                        except Exception as e:
                            print(f"解析 analysis_details 失败: {str(e)}")
                            # 如果解析失败，直接使用原始字符串
                            analysis_details = row['analysis_details']
                    
                    items.append({
                        "id": row['id'],
                        "code": row['code'],
                        "name": row['name'],
                        "start_date": str(row['start_date']) if row['start_date'] else None,
                        "end_date": str(row['end_date']) if row['end_date'] else None,
                        "trend": row['trend'],
                        "volume_pattern": row['volume_pattern'],
                        "support_level": row['support_level'],
                        "resistance_level": row['resistance_level'],
                        "signal": row['trade_signal'],
                        "confidence": float(row['confidence']) if row['confidence'] is not None else 0.0,
                        "analysis_details": analysis_details,
                        "token_usage": row['token_usage'] if 'token_usage' in row else 0,
                        "cost": float(row['cost']) if 'cost' in row and row['cost'] is not None else 0.00,
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
        print(f"get_analysis_history获取分析历史失败: {str(e)}")
        return {"total": 0, "page": page, "page_size": page_size, "items": []}


def get_screening_history(limit: int = 50) -> dict:
    """获取筛选历史记录"""
    if not check_db_connection():
        return {"message": "数据库不可用", "records": []}
    print(f"获取筛选历史记录，limit: {limit}")
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = '''
                    SELECT wa.*, s.name as stock_name
                    FROM wyckoff_analysis wa
                    JOIN stocks s ON wa.stock_id = s.id
                    ORDER BY wa.created_at DESC
                    LIMIT %s
                '''
                cursor.execute(sql, (limit,))
                rows = cursor.fetchall()
                
                # 转换为字典格式
                result = []
                for row in rows:
                    record = {
                        "id": row['id'],
                        "stock_id": row['stock_id'],
                        "code": row['code'],
                        "name": row['stock_name'],  # 使用从 stocks 表获取的名称
                        "start_date": str(row['start_date']) if row['start_date'] else None,
                        "end_date": str(row['end_date']) if row['end_date'] else None,
                        "trend": row['trend'],
                        "volume_pattern": row['volume_pattern'],
                        "support_level": row['support_level'],
                        "resistance_level": row['resistance_level'],
                        "signal": row['trade_signal'],
                        "confidence": float(row['confidence']) if row['confidence'] is not None else 0.0,
                        "analysis_details": None,
                        "token_usage": row['token_usage'] if 'token_usage' in row else 0,
                        "cost": float(row['cost']) if 'cost' in row and row['cost'] is not None else 0.00,
                        "chat_completion_id": row['chat_completion_id'] if 'chat_completion_id' in row else '',
                        "created_at": str(row['created_at']) if 'created_at' in row else ''
                    }
                    
                    # 处理 analysis_details 字段
                    if row['analysis_details']:
                        try:
                            record['analysis_details'] = json.loads(row['analysis_details'])
                        except:
                            record['analysis_details'] = row['analysis_details']
                    
                    result.append(record)
                
                return {"total": len(result), "records": result}
        finally:
            conn.close()
    except Exception as e:
        raise Exception(f"获取历史记录失败: {str(e)}")
