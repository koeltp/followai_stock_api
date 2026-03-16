import pymysql

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='HA9iHSrKEKgaPpna7',
    db='xszb'
)

# 创建游标
cursor = conn.cursor()

# 查询最近5条分析记录
print('Last 5 analysis records:')
cursor.execute('SELECT id, code, created_at FROM wyckoff_analysis ORDER BY created_at DESC LIMIT 5')
results = cursor.fetchall()
for row in results:
    print(row)

# 查询股票数据
print('\nHS300 stocks count:')
cursor.execute('SELECT COUNT(*) FROM stocks WHERE is_hs300 = 1')
count = cursor.fetchone()
print(f'Total stocks: {count[0]}')

# 查询最近5条股票记录
print('\nLast 5 stock records:')
cursor.execute('SELECT code, name, is_hs300, created_at FROM stocks ORDER BY created_at DESC LIMIT 5')
results = cursor.fetchall()
for row in results:
    print(row)

# 查询系统配置
print('\nSystem config count:')
cursor.execute('SELECT COUNT(*) FROM system_config')
count = cursor.fetchone()
print(f'Total configs: {count[0]}')

print('\nAll system configs:')
cursor.execute('SELECT id, config_key, config_value, description, parent FROM system_config ORDER BY parent, config_key')
results = cursor.fetchall()
for row in results:
    print(row)

# 关闭游标和连接
cursor.close()
conn.close()