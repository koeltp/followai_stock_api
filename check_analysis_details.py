import pymysql
import json

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='HA9iHSrKEKgaPpna7',
    db='xszb'
)

# 创建游标
cursor = conn.cursor()

# 查询最近一条记录的 analysis_details
cursor.execute('SELECT analysis_details FROM wyckoff_analysis ORDER BY created_at DESC LIMIT 1')

# 获取结果
result = cursor.fetchone()

if result and result[0]:
    print('Analysis Details:')
    # 如果是字符串，尝试解析为JSON
    if isinstance(result[0], str):
        details = json.loads(result[0])
        print(json.dumps(details, indent=2, ensure_ascii=False))
    else:
        print(result[0])
else:
    print('No analysis details found')

# 关闭游标和连接
cursor.close()
conn.close()