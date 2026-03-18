#!/usr/bin/env python3
"""
股票数据相关操作模块
"""

from app.db.connection import get_db_connection, check_db_connection


def save_stock_to_db(stock_data):
    """保存股票信息到数据库"""
    print(f"尝试保存股票: {stock_data['code']} - {stock_data['name']}")
    if not check_db_connection():
        return False
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 检查股票是否已存在
                cursor.execute('SELECT id FROM stocks WHERE code = %s', (stock_data['code'],))
                existing = cursor.fetchone()
                if existing:
                    # 更新股票信息
                    update_sql = '''
                        UPDATE stocks SET name = %s, market_type = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE code = %s
                    '''
                    cursor.execute(update_sql, (
                        stock_data['name'],
                        stock_data.get('market_type', 'A'),
                        stock_data['code']
                    ))
                    print(f"更新股票信息: {stock_data['code']} - {stock_data['name']}")
                else:
                    # 插入新股票
                    insert_sql = '''
                        INSERT INTO stocks (code, name, market_type, is_hs300)
                        VALUES (%s, %s, %s, %s)
                    '''
                    cursor.execute(insert_sql, (
                        stock_data['code'],
                        stock_data['name'],
                        stock_data.get('market_type', 'A'),
                        stock_data.get('is_hs300', 0)
                    ))
                    print(f"插入新股票: {stock_data['code']} - {stock_data['name']}")
            conn.commit()
            return True
        finally:
            conn.close()
    except Exception as e:
        print(f"数据库保存失败: {str(e)}")
        return False


def save_stock_history_to_db(stock_data):
    """保存股票历史数据到数据库"""
    if not check_db_connection():
        return
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 检查 stock_data 的类型
                if isinstance(stock_data, list):
                    # 如果是列表，假设列表中的每个元素都包含 code 字段
                    if not stock_data:
                        print("空数据列表，跳过保存")
                        return
                    
                    # 获取第一个元素的 code
                    code = stock_data[0].get('code', '')
                    print(f"尝试保存股票历史数据: {code}")
                    
                    # 获取股票的 stock_id
                    cursor.execute('SELECT id FROM stocks WHERE code = %s', (code,))
                    result = cursor.fetchone()
                    if not result:
                        print(f"股票代码 {code} 不存在，跳过保存")
                        return
                    stock_id = result['id']
                    
                    # 批量插入数据
                    values = []
                    for item in stock_data:
                        try:
                            # 处理字典类型的 item
                            if isinstance(item, dict):
                                date = item.get('date', '')
                                open_price = item.get('open', 0)
                                high = item.get('high', 0)
                                low = item.get('low', 0)
                                close = item.get('close', 0)
                                volume = item.get('volume', 0)
                                amount = item.get('amount', 0)
                            # 处理列表类型的 item（假设是按顺序排列的）
                            elif isinstance(item, list) and len(item) >= 7:
                                date = item[0]
                                open_price = item[1]
                                high = item[2]
                                low = item[3]
                                close = item[4]
                                volume = item[5]
                                amount = item[6]
                            else:
                                continue
                            
                            values.append((
                                stock_id,
                                date,
                                open_price,
                                high,
                                low,
                                close,
                                volume,
                                amount
                            ))
                        except Exception as e:
                            print(f"处理数据项失败: {str(e)}")
                            continue
                    
                    # 使用 INSERT IGNORE 避免唯一键冲突
                    if values:
                        sql = '''
                            INSERT IGNORE INTO stock_history 
                            (stock_id, date, open, high, low, close, volume, amount)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        '''
                        cursor.executemany(sql, values)
                        print(f"批量插入股票历史数据成功，影响行数: {cursor.rowcount}")
                    else:
                        print("没有有效的数据项可插入")
                elif isinstance(stock_data, dict):
                    # 如果是字典，按照原来的逻辑处理
                    print(f"尝试保存股票历史数据: {stock_data.get('code', '')} - {stock_data.get('name', '')}")
                    
                    # 获取股票的 stock_id
                    code = stock_data.get('code', '')
                    if not code:
                        print("股票代码为空，跳过保存")
                        return
                    
                    cursor.execute('SELECT id FROM stocks WHERE code = %s', (code,))
                    result = cursor.fetchone()
                    if not result:
                        print(f"股票代码 {code} 不存在，跳过保存")
                        return
                    stock_id = result['id']
                    
                    # 批量插入数据
                    if 'data' in stock_data and stock_data['data']:
                        values = []
                        for item in stock_data['data']:
                            try:
                                # 处理字典类型的 item
                                if isinstance(item, dict):
                                    date = item.get('date', '')
                                    open_price = item.get('open', 0)
                                    high = item.get('high', 0)
                                    low = item.get('low', 0)
                                    close = item.get('close', 0)
                                    volume = item.get('volume', 0)
                                    amount = item.get('amount', 0)
                                # 处理列表类型的 item（假设是按顺序排列的）
                                elif isinstance(item, list) and len(item) >= 7:
                                    date = item[0]
                                    open_price = item[1]
                                    high = item[2]
                                    low = item[3]
                                    close = item[4]
                                    volume = item[5]
                                    amount = item[6]
                                else:
                                    continue
                                
                                values.append((
                                    stock_id,
                                    date,
                                    open_price,
                                    high,
                                    low,
                                    close,
                                    volume,
                                    amount
                                ))
                            except Exception as e:
                                print(f"处理数据项失败: {str(e)}")
                                continue
                        
                        # 使用 INSERT IGNORE 避免唯一键冲突
                        if values:
                            sql = '''
                                INSERT IGNORE INTO stock_history 
                                (stock_id, date, open, high, low, close, volume, amount)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            '''
                            cursor.executemany(sql, values)
                            print(f"批量插入股票历史数据成功，影响行数: {cursor.rowcount}")
                        else:
                            print("没有有效的数据项可插入")
                    else:
                        print("数据为空，跳过保存")
                else:
                    print(f"未知的数据类型: {type(stock_data)}")
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"保存股票历史数据失败: {str(e)}")


def get_stock_history_from_db(code: str, start_date: str = None, end_date: str = None) -> list:
    """从数据库获取股票历史数据"""
    if not check_db_connection():
        return []
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                where_clause = "s.code = %s"
                params = [code]
                
                if start_date:
                    where_clause += " AND sh.date >= %s"
                    params.append(start_date)
                
                if end_date:
                    where_clause += " AND sh.date <= %s"
                    params.append(end_date)
                
                sql = f'''
                    SELECT sh.date, s.code, s.name, sh.open, sh.high, sh.low, sh.close, sh.volume, sh.amount
                    FROM stock_history sh
                    JOIN stocks s ON sh.stock_id = s.id
                    WHERE {where_clause}
                    ORDER BY sh.date
                '''
                print(params)
                print(f"执行SQL: {sql}")
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                return [
                    {
                        'date': str(row['date']) if row['date'] else '',
                        'code': row['code'],
                        'name': row['name'],
                        'open': float(row['open']) if row['open'] else 0,
                        'high': float(row['high']) if row['high'] else 0,
                        'low': float(row['low']) if row['low'] else 0,
                        'close': float(row['close']) if row['close'] else 0,
                        'volume': int(row['volume']) if row['volume'] else 0,
                        'amount': float(row['amount']) if row['amount'] else 0,
                    }
                    for row in rows
                ]
        finally:
            conn.close()
    except Exception as e:
        print(f"从数据库获取股票历史数据失败: {str(e)}")
        return []


def get_stock_by_code(code: str):
    """根据股票代码获取股票信息"""
    if not check_db_connection():
        return None
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM stocks WHERE code = %s', (code,))
                return cursor.fetchone()
        finally:
            conn.close()
    except Exception as e:
        print(f"获取股票信息失败: {str(e)}")
        return None


def get_stock_name_from_db(code: str) -> str:
    """从数据库获取股票名称"""
    if not check_db_connection():
        return code
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT name FROM stocks WHERE code = %s', (code,))
                result = cursor.fetchone()
                return result['name'] if result else code
        finally:
            conn.close()
    except Exception as e:
        print(f"获取股票名称失败: {str(e)}")
        return code


def get_hs300_stocks_from_db(page: int = 1, page_size: int = 10, search: str = None) -> dict:
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
                total = cursor.fetchone()['COUNT(*)']
                
                # 获取分页数据
                offset = (page - 1) * page_size
                query_params = params + [page_size, offset]
                cursor.execute(f'''
                    SELECT id, code, name, is_hs300, created_at, updated_at
                    FROM stocks
                    WHERE {where_clause}
                    ORDER BY id DESC
                    LIMIT %s OFFSET %s
                ''', query_params)
                rows = cursor.fetchall()
                
                items = [
                    {
                        "id": row['id'],
                        "code": row['code'],
                        "name": row['name'],
                        "is_hs300": bool(row['is_hs300']),
                        "created_at": str(row['created_at']) if row['created_at'] else None,
                        "updated_at": str(row['updated_at']) if row['updated_at'] else None
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


def get_all_stocks_from_db(page: int = 1, page_size: int = 10, search: str = None, market: str = None) -> dict:
    """从数据库获取所有股票（支持分页和搜索）"""
    if not check_db_connection():
        return {"total": 0, "items": []}
    
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                where_clause = "1=1"
                params = []
                
                if search:
                    where_clause += " AND (code LIKE %s OR name LIKE %s)"
                    params.extend([f'%{search}%', f'%{search}%'])
                
                if market:
                    where_clause += " AND market_type = %s"
                    params.append(market)
                
                count_sql = f"SELECT COUNT(*) FROM stocks WHERE {where_clause}"
                cursor.execute(count_sql, params)
                total = cursor.fetchone()['COUNT(*)']
                
                offset = (page - 1) * page_size
                query_params = params + [page_size, offset]
                
                cursor.execute(f'''
                    SELECT id, code, name, market_type, is_hs300, created_at, updated_at
                    FROM stocks
                    WHERE {where_clause}
                    ORDER BY id DESC
                    LIMIT %s OFFSET %s
                ''', query_params)
                rows = cursor.fetchall()
                
                items = [
                    {
                        "id": row['id'],
                        "code": row['code'],
                        "name": row['name'],
                        "market_type": row['market_type'],
                        "is_hs300": bool(row['is_hs300']),
                        "created_at": str(row['created_at']) if row['created_at'] else None,
                        "updated_at": str(row['updated_at']) if row['updated_at'] else None
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
        print(f"获取股票列表失败: {str(e)}")
        return {"total": 0, "items": []}
