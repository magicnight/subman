# MySub Manager 📊

> 个人订阅管理助手 - 让每一笔订阅都清晰可见

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.30+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🎯 项目简介

MySub Manager 是一款基于 Streamlit 的轻量级订阅管理工具，帮助你：

- ✅ 可视化管理所有订阅服务（AI 工具、流媒体、软件会员等）
- 💰 自动计算月均支出（统一年付和月付）
- ⏰ 智能到期提醒（7天内到期自动预警）
- 📈 可视化支出分析（按服务类型统计）

### 为什么开发这个工具？

现有的 Excel 管理方式存在痛点：
- ❌ 被动管理，容易忘记取消自动续费
- ❌ 成本模糊，难以直观了解月度开销
- ❌ 手机端编辑体验差

MySub Manager 将静态数据转化为**动态财务看板**，让订阅管理变得简单高效。

## 🚀 快速开始

### 环境要求

- Python 3.9 或更高版本
- pip 包管理工具

### 安装步骤

1. **克隆项目**（或下载压缩包）

```bash
git clone https://github.com/yourusername/mysub-manager.git
cd mysub-manager
```

2. **安装依赖**（使用 uv 包管理器）

```bash
# 安装 uv（如果尚未安装）
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 同步依赖
uv sync
```

> 💡 项目使用 `pyproject.toml` + `uv.lock` 管理依赖，确保环境一致性

3. **准备数据文件**

将你的订阅数据整理成 CSV 格式，放在 `data/` 目录下：

```
data/
├── subscriptions.csv    # 主数据文件
├── Service.csv          # 服务类型枚举（AI/视频/软件/系统）
└── Subscribe.csv        # 订阅周期枚举（年付/月付）
```

📝 CSV 文件格式参考下方 [数据格式](#-数据格式) 章节

4. **运行应用**

```bash
# 方式一：使用一键启动脚本
# Windows
start.bat
# 或
start.ps1

# macOS/Linux
./start.sh

# 方式二：手动运行
uv run streamlit run src/main.py
```

浏览器会自动打开 `http://localhost:8501`

## 📁 项目结构

```
mysub-manager/
├── src/
│   ├── main.py                 # 🎯 Streamlit 主应用入口
│   ├── config.py               # ⚙️ 全局配置
│   ├── utils/                  # 🛠️ 工具函数
│   │   ├── data_loader.py      # 数据加载和计算
│   │   ├── currency.py         # 汇率换算
│   │   ├── notifications.py    # 邮件通知
│   │   ├── exporter.py         # 报告导出
│   │   └── validator.py        # 数据验证
│   └── components/             # 🧩 UI 组件
│       ├── dashboard.py        # 仪表盘
│       ├── table.py            # 订阅列表
│       └── analytics.py        # 统计分析
├── data/
│   ├── subscriptions.csv       # 📋 订阅数据
│   ├── Service.csv             # 🏷️ 服务类型
│   └── Subscribe.csv           # 🔄 订阅周期
├── assets/                     # 🎨 静态资源
├── tests/                      # 🧪 测试文件
├── pyproject.toml              # 📦 项目配置和依赖
├── .gitignore                  # 🚫 Git 忽略规则
├── .cursorignore               # 🚫 Cursor 忽略规则
├── .cursorrules                # 🤖 Cursor AI 规则
└── README.md                   # 📖 项目文档（本文件）
```

## 📊 数据格式

### subscriptions.csv

| 字段名       | 类型    | 示例       | 说明                |
| ------------ | ------- | ---------- | ------------------- |
| 名称         | String  | Claude Pro | 服务名称            |
| 供应商       | String  | Anthropic  | 供应商（可选）      |
| 服务性质     | String  | AI         | 对应 Service.csv    |
| 订阅类型     | String  | 年付       | 对应 Subscribe.csv  |
| 金额         | Float   | 210.54     | 原币种金额          |
| 下次付费时间 | Date    | 2026-02-26 | ISO 格式 YYYY-MM-DD |
| 自动续费     | Boolean | FALSE      | 是否自动扣款        |

**示例数据**:

```csv
名称,供应商,服务性质,订阅类型,金额,下次付费时间,自动续费
Claude Pro,Anthropic,AI,年付,210.54,2026-02-26,FALSE
Netflix,Netflix,视频,月付,419.00,2026-02-01,TRUE
```

### Service.csv（服务类型枚举）

```csv
服务性质
AI
视频
软件
系统
```

### Subscribe.csv（订阅周期枚举）

```csv
订阅类型
年付
月付
```

## 🎨 功能特性

### 1️⃣ 仪表盘 (Dashboard)

- 📊 **KPI 卡片**: 订阅总数、月均总支出、近期预警数量
- 🚨 **红绿灯预警**: 7天内到期且自动续费的项目高亮显示
- 💡 **一目了然**: 快速掌握订阅整体状况

### 2️⃣ 订阅列表 (Subscription List)

- 📋 **完整展示**: 名称、类型、金额、到期时间、剩余天数等
- 🔄 **动态排序**: 点击表头按任意字段排序
- 🎨 **视觉区分**: 已过期项目自动置灰

### 3️⃣ 数据管理 (CRUD)

- ➕ **新增订阅**: 侧边栏表单快速添加
- 🗑️ **删除订阅**: 一键删除不需要的项目
- 💾 **自动保存**: 修改实时同步到 CSV 文件

### 4️⃣ 统计分析 (Analytics)

- 🥧 **支出饼图**: 按服务类型分析月均成本占比
- 📈 **趋势分析**: （待开发）历史支出趋势
- 🔍 **深度洞察**: 发现你在哪类服务上花费最多

## 🛣️ 开发路线图

### ✅ Phase 1: MVP (已完成)
- [x] CSV 数据读取与清洗
- [x] 仪表盘 KPI 指标展示
- [x] 基础表格展示和排序
- [x] 本地运行部署

### ✅ Phase 2: 交互升级 (已完成)
- [x] 新增订阅表单功能
- [x] 编辑订阅功能
- [x] 数据写入 CSV 功能
- [x] 饼图分析功能

### ✅ Phase 3: 扩展功能 (已完成)
- [x] 汇率换算支持（多货币 → THB）
- [x] 邮件到期提醒推送
- [x] 历史数据趋势分析
- [x] 导出报告（Excel/CSV/Markdown）

## 🔧 开发指南

### 使用 Cursor + Claude Opus 开发

本项目已配置 `.cursorrules` 文件，优化了 AI 辅助开发体验。

**推荐工作流**:

1. 在 Cursor 中打开项目
2. 使用 **Cmd/Ctrl + K** 调用 AI 辅助
3. 选择 **Claude Opus** 模型（代码生成质量最佳）
4. 参考 `.cursorrules` 中的 Prompt 示例

### 代码规范

- 遵循 **PEP 8** 规范
- 使用类型提示 (Type Hints)
- 添加中文 docstring
- 关键函数编写单元测试

### Git 提交规范

```
feat: 新功能
fix: 修复 Bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建工具
```

示例: `git commit -m "feat: 添加订阅到期邮件提醒"`

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Streamlit](https://streamlit.io) - 优雅的 Python Web 框架
- [Pandas](https://pandas.pydata.org) - 强大的数据处理库
- [Plotly](https://plotly.com) - 交互式可视化库

## 📮 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 📧 Email: your.email@example.com
- 💬 Issue: [GitHub Issues](https://github.com/yourusername/mysub-manager/issues)

---

⭐ 如果这个项目对你有帮助，请给一个 Star！

**Made with ❤️ by [Your Name]**
