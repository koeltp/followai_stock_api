# API 项目说明

## 项目简介

这是一个集成 qwen3.5-plus 大模型的智能股票分析 API 服务，通过千问大模型的深度分析能力，结合经典的威科夫操盘法，为投资者提供专业的股票筛选和分析工具。

### 核心技术特点

- **千问大模型智能分析**：集成 qwen3.5-plus 大模型，对股票数据进行深度分析，提供更准确的市场判断和投资建议
- **威科夫操盘法**：采用经典的威科夫操盘法理论，通过分析股票的价格、成交量和市场结构，识别潜在的趋势转折点和交易机会。威科夫操盘法是由理查德·威科夫（Richard Wyckoff）创立的技术分析方法，核心包括：
  - **累积与派发**：识别主力资金的吸筹和出货阶段
  - **成交量分析**：通过成交量变化判断市场强弱和趋势可信度
  - **价格结构**：分析价格形态和支撑阻力位
  - **市场阶段**：识别市场的四个阶段（吸筹、上升、派发、下降）
  - **量价关系**：通过量价配合判断市场情绪和趋势方向
- **实时数据**：对接 Baostock 数据接口，获取最新的股票历史数据和市场信息
- **自动化分析**：支持定时任务自动更新数据和执行分析，减少人工干预

### 主要功能

- 沪深300成分股数据获取与管理
- 基于威科夫操盘法的单只股票深度分析
- 利用 AI 模型进行智能选股和筛选
- 分析历史记录管理和查询
- 系统配置管理和优化

## 项目结构

```
api/
├── app/             # 应用主目录
│   ├── config/      # 配置管理
│   ├── db/          # 数据库操作
│   ├── models/      # 数据模型
│   ├── routes/      # API 路由
│   ├── schemas/     # 数据验证模式
│   ├── services/    # 业务逻辑
│   └── tasks/       # 定时任务
├── config.json      # 主配置文件
├── init_config.json # 初始化配置文件
├── main.py          # 应用入口
└── requirements.txt # 依赖包
```

## 环境要求

- Python 3.8+  
- pip 包管理器

## 安装步骤

### 1. 克隆项目
#### 1.1 克隆 API 项目
```bash
git clone https://github.com/koeltp/followai_stock_api.git
cd followai_stock/api
```
#### 1.2 克隆 Web 项目
```bash
git clone https://github.com/koeltp/followai_stock_web.git
cd followai_stock/web
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

1. **初始化配置文件**：`init_config.json` 是项目初始化时使用的配置文件，用于初始化数据库，初始化完成后不再使用。

   主要需要配置以下项：
   - `qwen_api_key`：Qwen API 密钥，需要去 [阿里云百炼控制台](https://bailian.console.aliyun.com/#/home) 获取

   其他配置项可以保持不变。

2. **主配置文件**：`config.json` 是项目运行时使用的配置文件，需要根据实际情况修改以下配置项：
   - 数据库配置（host、port、user、password、db）
   - 应用配置（title、description、version）
   - CORS 配置（allow_origins）

   注意：`config.json` 中的配置不会写入数据库，而是直接被应用读取使用。

## 运行项目

### 开发模式

```bash
uvicorn main:app --reload
```

### 生产模式

```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

## API 文档

项目启动后，可以通过以下地址访问 API 文档：

- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## 主要 API 端点

- `GET /health` - 健康检查
- `GET /stocks/hs300` - 获取沪深300成分股
- `GET /stocks/wyckoff/analysis` - 单只股票威科夫分析
- `POST /stocks/wyckoff/screening` - 执行威科夫筛选
- `GET /stocks/wyckoff/history` - 获取筛选历史
- `GET /stocks/wyckoff/analysis-history` - 获取分析历史
- `GET /stocks/wyckoff/analysis-logs` - 获取分析日志
- `POST /stocks/wyckoff/reparse/{log_id}` - 重新解析分析日志
- `GET /stocks/history` - 获取股票历史数据
- `GET /config` - 获取所有配置
- `POST /config` - 更新配置

## 定时任务

项目启动时会自动设置以下定时任务：

- 每天更新沪深300成分股列表
- 定期执行股票分析

## 注意事项

1. 确保数据库服务已启动并创建了相应的数据库
2. 首次运行时会自动初始化数据库表结构
3. 部分 API 需要较长时间执行，建议使用异步调用
4. 威科夫分析功能依赖于历史数据，请确保数据已同步

## 故障排查

- 如果遇到数据库连接错误，请检查 `config.json` 中的数据库配置
- 如果遇到依赖包安装错误，请确保使用了正确的 Python 版本
- 如果遇到 API 调用超时，请检查网络连接和服务状态

## 联系方式

邮箱：tp@taipi.top

如有问题，请联系项目维护人员。