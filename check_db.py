import json
import pymysql

# 读取配置文件
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

db_config = config['database']
print('Database config:', db_config)

try:
    # 连接数据库
    conn = pymysql.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        db=db_config['db'],
        charset=db_config['charset'],
        cursorclass=pymysql.cursors.DictCursor
    )
    print('Database connected successfully')
    
    # 检查表结构
    cursor = conn.cursor()
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    print('Tables:')
    for table in tables:
        print('  -', list(table.values())[0])
    
    # 检查 stocks 表数据
    if any('stocks' in list(t.values())[0] for t in tables):
        cursor.execute('SELECT COUNT(*) as count FROM stocks')
        result = cursor.fetchone()
        print('Stocks count:', result['count'])
    else:
        print('stocks table not found')
    
    conn.close()
except Exception as e:
    print('Error:', str(e))
