# API 项目说明

## 项目简介

这是一个集成 qwen3.5-plus 大模型的智能股票分析 API 服务，通过千问大模型的深度分析能力，结合经典的威科夫操盘法，为投资者提供专业的股票筛选和分析工具。

### 核心技术特点

- **千问大模型智能分析**：集成 qwen3.5-plus 大模型，对股票数据进行深度分析，提供更准确的市场判断和投资建议
- **威科夫操盘法**：采用经典的威科夫操盘法理论，通过分析股票的价格、成交量和市场结构，识别潜在的趋势转折点和交易机会
- **多市场支持**：支持 A 股、美股、港股的股票数据获取和分析
- **实时数据**：对接 Baostock 和 LongPort 数据接口，获取最新的股票历史数据和市场信息
- **自动化分析**：支持定时任务自动更新数据和执行分析，减少人工干预
- **数据库自动创建**：系统启动时自动创建数据库和表结构，确保系统正常运行

### 主要功能

- 多市场股票数据获取与管理（A股、美股、港股）
- 基于威科夫操盘法的单只股票深度分析
- 利用 AI 模型进行智能选股和筛选
- 分析历史记录管理和查询
- 系统配置管理和优化
- 股票历史数据同步与管理
- 自动判断并添加股票代码前缀（sh./sz.）
- 支持从数据库读取历史数据，避免重复调用 API
- 统一数据访问方式，使用属性访问而非字典访问
- 支持多种时间格式转换

## 系统要求

- Python 3.8+
- pip 包管理器
- MySQL 数据库服务

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/koeltp/followai_stock_api.git
cd followai_stock/api
```

### 2. 创建虚拟环境（可选但推荐）

#### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux/Mac
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置文件

修改 `config.json` 文件中的以下配置项：
- **数据库配置**：host、port、user、password、db
- **应用配置**：title、description、version
- **CORS 配置**：allow_origins

### 5. 运行项目

开发模式：
```bash
uvicorn main:app --reload
```

生产模式：
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

项目启动后，API 服务运行在：`http://localhost:8001`

## 首次使用指南

### 步骤 1：启动服务

1. 确保 MySQL 数据库服务已启动
2. 运行 API 服务（参考「快速开始」部分）
3. 服务启动时会自动创建数据库和表结构
4. 自动执行系统配置初始化脚本

### 步骤 2：配置模型 KEY

1. 启动 Web 应用（参考 Web 项目 README）
2. 登录系统后，点击左侧菜单的「系统配置」
3. 在配置列表中找到以下配置项并填写：
   - `qwen_api_key`：Qwen API 密钥（从阿里云百炼控制台获取）
   - `longport_app_key`：LongPort API App Key（用于获取美股和港股数据）
   - `longport_app_secret`：LongPort API App Secret
   - `longport_access_token`：LongPort API Access Token
4. 点击「保存」按钮完成配置

### 步骤 3：添加股票

1. 在 Web 应用的「股票列表」页面
2. 点击「添加股票」按钮
3. 选择市场类型并输入股票代码
4. 点击「确定」按钮添加股票

### 步骤 4：同步 K 线数据

1. 在股票列表中找到刚添加的股票
2. 点击「同步历史K线数据」按钮
3. 等待同步完成
4. 同步成功后会显示提示信息

### 步骤 5：执行分析

1. 在股票列表中点击股票的「分析」按钮
2. 在分析页面中选择日期范围
3. 点击「开始分析」按钮
4. 等待分析完成
5. 查看分析结果

## 项目结构

```
api/
├── app/             # 应用主目录
│   ├── config/      # 配置管理
│   ├── db/          # 数据库操作
│   │   ├── analysis.py        # 分析历史相关操作
│   │   ├── analysis_log.py    # 分析日志相关操作
│   │   ├── config.py          # 系统配置相关操作
│   │   ├── connection.py      # 数据库连接管理
│   │   ├── schema.py          # 表结构定义和初始化
│   │   ├── stock.py           # 股票数据相关操作
│   │   └── utils.py           # 辅助函数
│   ├── routes/      # API 路由
│   ├── schemas/     # 数据验证模式
│   ├── services/    # 业务逻辑
│   │   ├── baostock_client.py  # 宝信数据客户端
│   │   ├── longport_client.py  # LongPort数据客户端（美股/港股）
│   │   ├── qwen_analyzer.py    # 千问大模型分析器
│   │   └── wyckoff_analysis.py # 威科夫分析逻辑
│   ├── sql/         # SQL脚本
│   │   └── system_config.sql   # 系统配置初始化脚本
│   └── tasks/       # 定时任务
├── config.json      # 主配置文件
├── main.py          # 应用入口
└── requirements.txt # 依赖包
```

## API 文档

项目启动后，可以通过以下地址访问 API 文档：

- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## 主要 API 端点

- `GET /health` - 健康检查
- `GET /stocks/list` - 获取股票列表（支持多市场）
- `POST /stocks/add` - 添加股票
- `POST /stocks/sync` - 同步股票历史数据
- `GET /stocks/wyckoff/analysis` - 单只股票威科夫分析
- `POST /stocks/wyckoff/screening` - 执行威科夫筛选
- `GET /stocks/wyckoff/analysis-history` - 获取分析历史
- `GET /stocks/wyckoff/analysis-logs` - 获取分析日志
- `POST /stocks/wyckoff/reparse/{log_id}` - 重新解析分析日志
- `GET /config` - 获取所有配置
- `POST /config` - 更新配置

## 定时任务

项目启动时会自动设置以下定时任务：

- 每天更新沪深300成分股列表
- 定期执行股票分析

## 常见问题

### 1. 数据库连接错误
- 检查 `config.json` 中的数据库配置是否正确
- 确保 MySQL 服务已启动
- 确保数据库用户有足够的权限

### 2. 模型 KEY 配置错误
- 检查 Qwen API Key 是否正确
- 检查 LongPort API 配置是否完整
- 确保网络连接正常，能够访问 API 服务

### 3. 同步数据失败
- 检查模型 KEY 是否正确配置
- 检查网络连接是否正常
- 检查股票代码是否正确
- 对于美股/港股，确保 LongPort API 配置正确

### 4. 分析失败
- 检查历史数据是否已同步
- 检查模型 KEY 是否正确配置
- 检查网络连接是否正常
- 查看 API 日志获取详细错误信息

### 5. 服务启动失败
- 检查依赖包是否安装完整
- 检查端口是否被占用
- 查看启动日志获取详细错误信息

## 技术栈

- **后端框架**：FastAPI
- **数据库**：MySQL
- **数据接口**：Baostock、LongPort
- **AI 模型**：Qwen 3.5 Plus
- **定时任务**：APScheduler

## 联系方式

邮箱：tp@taipi.top

如有问题，请联系项目维护人员。