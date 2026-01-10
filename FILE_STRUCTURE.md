# 项目文件总览 (FILE_STRUCTURE.md)

## 📂 完整目录结构

```
mysub-manager/
├── 📄 配置文件
│   ├── .gitignore              # Git 忽略规则
│   ├── .cursorignore           # Cursor AI 忽略规则
│   ├── .cursorrules            # Cursor AI 开发规则（重要！）
│   ├── .env.example            # 环境变量示例
│   └── requirements.txt        # Python 依赖列表
│
├── 📚 文档
│   ├── README.md               # 项目主文档（从这里开始）
│   ├── QUICKSTART.md           # 快速入门指南（5分钟上手）
│   ├── DEVELOPMENT.md          # 开发指南（深度开发必读）
│   ├── FILE_STRUCTURE.md       # 本文件（项目结构说明）
│   └── LICENSE                 # MIT 开源协议
│
├── 🚀 启动脚本
│   ├── start.sh                # Linux/macOS 启动脚本
│   └── start.bat               # Windows 启动脚本
│
├── 💾 数据目录
│   └── data/
│       ├── subscriptions.csv   # 主订阅数据（示例数据）
│       ├── Service.csv         # 服务类型枚举
│       └── Subscribe.csv       # 订阅周期枚举
│
├── 💻 源代码
│   └── src/
│       ├── main.py             # Streamlit 应用入口
│       ├── config.py           # 全局配置
│       │
│       ├── utils/              # 工具函数包
│       │   ├── __init__.py
│       │   └── data_loader.py  # 数据加载和处理
│       │
│       └── components/         # UI 组件包
│           ├── __init__.py
│           ├── dashboard.py    # 仪表盘组件
│           ├── table.py        # 订阅列表组件
│           └── analytics.py    # 统计分析组件
│
├── 🧪 测试
│   └── tests/
│       ├── __init__.py
│       └── test_calculator.py  # 计算器测试用例
│
└── 🎨 资源
    └── assets/                 # 静态资源（图片、图标等）
```

## 📋 核心文件说明

### 配置类文件

#### `.cursorrules` ⭐ **重要**
这是 Cursor AI 的开发规则文件，包含：
- 项目技术栈说明
- 代码规范要求
- AI 提示词示例
- 文件组织规范

**使用场景**: 在 Cursor 中开发时，AI 会自动读取此文件作为上下文

#### `requirements.txt`
Python 依赖列表，包含：
- Streamlit (Web 框架)
- Pandas (数据处理)
- Plotly (数据可视化)
- 其他工具库

**使用方法**: `pip install -r requirements.txt`

#### `.gitignore`
Git 版本控制忽略规则，包含：
- Python 缓存文件 (`__pycache__/`, `*.pyc`)
- 虚拟环境 (`venv/`, `.venv/`)
- 数据文件 (`data/*.csv` - 保护隐私)
- IDE 配置 (`.vscode/`, `.idea/`)

#### `.env.example`
环境变量配置模板，用于：
- 数据路径配置
- 预警天数设置
- 邮件/Telegram 通知配置（未来功能）

**使用方法**: `cp .env.example .env` 然后编辑

### 文档类文件

#### `README.md` 📖 **必读**
项目主文档，包含：
- 项目介绍和特性
- 安装和使用说明
- 数据格式定义
- 开发路线图

**适合人群**: 所有用户

#### `QUICKSTART.md` 🚀 **新手必读**
5 分钟快速上手指南，包含：
- 环境准备
- 快速安装
- 基础操作
- 常见问题

**适合人群**: 初次使用者

#### `DEVELOPMENT.md` 🛠️ **开发者必读**
深度开发指南，包含：
- 开发环境配置
- Cursor AI 使用技巧
- 代码规范详解
- 性能优化建议

**适合人群**: 需要修改代码或添加功能的开发者

### 源代码文件

#### `src/main.py`
**用途**: Streamlit 应用入口文件
**职责**:
- 页面配置和初始化
- 侧边栏渲染（导航 + 新增表单）
- 页面路由控制

**关键函数**:
- `main()`: 主入口函数
- `render_sidebar()`: 渲染侧边栏
- `render_add_form()`: 渲染新增订阅表单

#### `src/config.py`
**用途**: 全局配置文件
**包含**:
- 文件路径配置
- 日期和币种格式
- UI 样式常量
- 数据验证规则

**可修改项**:
- `WARNING_DAYS`: 预警天数（默认 7）
- `CURRENCY_SYMBOL`: 币种符号（默认 ฿）
- `PRIMARY_COLOR`: 主题颜色

#### `src/utils/data_loader.py`
**用途**: 数据加载和持久化
**核心功能**:
- `load_subscriptions()`: 加载 CSV 数据
- `save_subscriptions()`: 保存数据到 CSV
- `add_subscription()`: 添加新订阅
- `delete_subscription()`: 删除订阅
- `calculate_monthly_cost()`: 计算月均成本

**特点**:
- 使用 `@st.cache_data` 缓存提升性能
- 完整的错误处理
- 自动数据类型转换

#### `src/components/dashboard.py`
**用途**: 仪表盘页面
**功能模块**:
- `render_dashboard()`: 主渲染函数
- `render_warning_banner()`: 到期预警横幅
- `render_kpi_cards()`: KPI 指标卡片
- `render_quick_stats()`: 快速统计

**展示内容**:
- 订阅总数、月均支出、年度预估
- 7天内到期预警
- 服务类型和订阅类型分布
- 最贵订阅 Top 3

#### `src/components/table.py`
**用途**: 订阅列表页面
**功能模块**:
- `render_subscription_table()`: 主渲染函数
- `render_filters()`: 筛选和排序
- `prepare_display_dataframe()`: 数据准备
- `render_delete_section()`: 删除功能

**特性**:
- 支持按服务类型筛选
- 支持多种排序方式
- 已过期订阅置灰显示
- 即将到期订阅高亮警告

#### `src/components/analytics.py`
**用途**: 统计分析页面
**功能模块**:
- `render_analytics()`: 主渲染函数
- `render_expense_pie_chart()`: 支出饼图
- `render_subscription_type_chart()`: 类型分布图
- `render_timeline_chart()`: 付费时间线

**可视化类型**:
- Plotly 饼图（支出构成）
- Plotly 柱状图（类型分布）
- Plotly 时间线图（付费日程）

### 数据文件

#### `data/subscriptions.csv` 💾 **核心数据**
**格式**:
```csv
名称,供应商,服务性质,订阅类型,金额,下次付费时间,自动续费
Claude Pro,Anthropic,AI,年付,210.54,2026-02-26,FALSE
```

**字段说明**:
- `名称`: 服务名称（必填）
- `供应商`: 供应商名称（可选）
- `服务性质`: 服务类型，对应 Service.csv（必填）
- `订阅类型`: 订阅周期，对应 Subscribe.csv（必填）
- `金额`: 订阅金额（必填，数字）
- `下次付费时间`: 下次扣费日期（必填，YYYY-MM-DD）
- `自动续费`: 是否自动续费（必填，TRUE/FALSE）

#### `data/Service.csv`
**用途**: 服务类型枚举
**示例**:
```csv
服务性质
AI
视频
软件
系统
```

#### `data/Subscribe.csv`
**用途**: 订阅周期枚举
**示例**:
```csv
订阅类型
年付
月付
季付
```

### 测试文件

#### `tests/test_calculator.py`
**用途**: 单元测试
**测试内容**:
- 月均成本计算逻辑
- 不同订阅类型的转换

**运行方法**:
```bash
pytest tests/test_calculator.py -v
```

## 🎯 文件使用场景

### 场景 1: 首次使用
**阅读顺序**:
1. `README.md` - 了解项目
2. `QUICKSTART.md` - 快速上手
3. 运行 `start.sh` 或 `start.bat`

### 场景 2: 日常使用
**涉及文件**:
- `data/subscriptions.csv` - 编辑订阅数据
- `src/main.py` - 启动应用

### 场景 3: 添加新功能
**阅读顺序**:
1. `DEVELOPMENT.md` - 学习开发流程
2. `.cursorrules` - 了解代码规范
3. `src/components/` - 参考现有组件

**修改文件**:
- `src/components/` - 添加新组件
- `src/main.py` - 添加路由
- `requirements.txt` - 添加依赖（如需要）

### 场景 4: 自定义配置
**修改文件**:
- `src/config.py` - 修改全局配置
- `data/Service.csv` - 添加服务类型
- `data/Subscribe.csv` - 添加订阅类型

### 场景 5: 调试问题
**查看文件**:
- `DEVELOPMENT.md` - 调试技巧
- `tests/` - 运行测试
- 日志输出（Streamlit 控制台）

## 📝 文件权限说明

### 不要提交到 Git 的文件
- `data/*.csv` - 个人数据（隐私保护）
- `.env` - 环境变量（敏感信息）
- `venv/` - 虚拟环境（太大）
- `__pycache__/` - Python 缓存（自动生成）

### 应该提交到 Git 的文件
- 所有源代码 (`src/`)
- 所有文档 (`.md` 文件)
- 配置文件 (`.gitignore`, `.cursorrules`, `requirements.txt`)
- 启动脚本 (`start.sh`, `start.bat`)

## 🔄 文件更新频率

### 经常变动
- `data/subscriptions.csv` - 每次添加/删除订阅

### 偶尔变动
- `src/components/` - 添加新功能时
- `src/config.py` - 调整配置时

### 很少变动
- `requirements.txt` - 添加新依赖时
- `.cursorrules` - 更新开发规范时
- 文档文件 - 功能变更时

---

💡 **提示**: 这份文档是你的项目导航地图，建议收藏备用！
