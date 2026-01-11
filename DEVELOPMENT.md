# 开发指南 (DEVELOPMENT.md)

## 🛠️ 开发环境设置

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/mysub-manager.git
cd mysub-manager
```

### 2. 创建虚拟环境

推荐使用 `uv` 包管理器（自动管理虚拟环境）：

```bash
# 安装 uv（如果尚未安装）
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

或者使用传统方式：

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. 安装开发依赖

```bash
# 使用 uv 包管理器安装依赖
uv sync
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 根据需要编辑 .env 文件
```

## 📁 项目结构说明

```text
mysub-manager/
├── src/                    # 源代码目录
│   ├── main.py            # 应用入口
│   ├── config.py          # 全局配置（VERSION 等）
│   ├── remind.py          # 到期提醒脚本
│   ├── utils/             # 工具函数
│   │   ├── data_loader.py # 数据加载和计算
│   │   ├── currency.py    # 汇率换算（BOT API）
│   │   ├── notifications.py # 邮件通知
│   │   ├── exporter.py    # 报告导出
│   │   ├── history.py     # 历史趋势
│   │   └── validator.py   # 数据验证
│   └── components/        # UI 组件
│       ├── dashboard.py   # 仪表盘
│       ├── table.py       # 订阅列表
│       └── analytics.py   # 统计分析
├── data/                  # 数据文件（不提交到 Git）
├── tests/                 # 测试文件
│   ├── test_calculator.py
│   ├── test_currency.py
│   ├── test_validator.py
│   └── test_exporter.py
└── assets/                # 静态资源
```

## 🔄 开发工作流

### 使用 Cursor + Claude Opus

1. **在 Cursor 中打开项目**
   ```bash
   cursor .
   ```

2. **配置 AI 模型**
   - 打开 Cursor 设置 (Cmd/Ctrl + ,)
   - 选择 **Claude Opus** 作为默认模型
   - 确保 `.cursorrules` 文件生效

3. **AI 辅助开发技巧**

   **场景 1: 生成新功能**
   ```
   Prompt: 
   请帮我实现一个导出 PDF 报告的功能，要求：
   1. 包含所有订阅数据
   2. 添加支出饼图
   3. 美化排版
   使用 reportlab 库，遵循项目代码规范
   ```

   **场景 2: 调试问题**
   ```
   Prompt:
   我的 Streamlit 页面在点击删除按钮后没有刷新，
   这是相关代码：[粘贴代码]
   请帮我分析问题并给出解决方案
   ```

   **场景 3: 优化代码**
   ```
   Prompt:
   请帮我优化 data_loader.py 中的 load_subscriptions 函数，
   要求：
   1. 提高性能
   2. 增强错误处理
   3. 添加类型提示
   ```

## 🧪 测试

### 运行单元测试

```bash
pytest tests/ -v
```

### 运行测试覆盖率

```bash
pytest --cov=src tests/
```

### 运行特定测试

```bash
pytest tests/test_calculator.py -v
```

## 📝 代码规范

### Python 风格

- 遵循 **PEP 8** 规范
- 使用 **black** 格式化代码
- 使用 **flake8** 检查代码质量
- 使用 **mypy** 进行类型检查

### 运行代码检查

```bash
# 格式化代码
black src/

# 检查代码质量
flake8 src/

# 类型检查
mypy src/
```

### 命名规范

- **文件名**: 小写字母 + 下划线 (snake_case)
  - `data_loader.py` ✅
  - `DataLoader.py` ❌

- **函数名**: 小写字母 + 下划线
  - `load_subscriptions()` ✅
  - `LoadSubscriptions()` ❌

- **类名**: 大驼峰 (PascalCase)
  - `SubscriptionManager` ✅
  - `subscription_manager` ❌

- **常量**: 全大写 + 下划线
  - `WARNING_DAYS` ✅
  - `warningDays` ❌

## 🔧 常见开发任务

### 1. 添加新的服务类型

编辑 `data/Service.csv`:
```csv
服务性质
AI
视频
软件
新类型  # 添加这一行
```

### 2. 修改 KPI 计算逻辑

编辑 `src/components/dashboard.py` 中的 `render_kpi_cards()` 函数

### 3. 添加新的图表

在 `src/components/analytics.py` 中创建新函数:
```python
def render_new_chart(df: pd.DataFrame):
    """渲染新图表"""
    # 你的实现
```

然后在 `render_analytics()` 中调用

### 4. 自定义主题颜色

编辑 `src/config.py`:
```python
PRIMARY_COLOR = "#FF4B4B"  # 修改这里
```

## 🐛 调试技巧

### 1. Streamlit 调试模式

```python
# 在代码中添加
st.write("调试信息:", some_variable)
```

### 2. 查看 Session State

```python
# 在任何页面添加
st.sidebar.write("Session State:", st.session_state)
```

### 3. 清除缓存

```python
# 在函数中
st.cache_data.clear()

# 或在浏览器中按 C 键
```

## 🚀 性能优化

### 1. 使用缓存

```python
@st.cache_data(ttl=300)  # 缓存 5 分钟
def expensive_function():
    # 耗时操作
```

### 2. 避免重复计算

```python
# 不好的做法
for i in range(len(df)):
    df.at[i, 'monthly_cost'] = calculate(df.at[i, 'amount'])

# 好的做法
df['monthly_cost'] = df.apply(lambda row: calculate(row['amount']), axis=1)
```

## 📦 发布新版本

### 1. 更新版本号

编辑 `src/config.py`:
```python
VERSION = "1.1.0"
```

### 2. 更新 CHANGELOG

创建 `CHANGELOG.md` 并记录变更

### 3. 创建 Git Tag

```bash
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

## 🤝 贡献指南

### Commit 消息规范

```
<type>: <subject>

<body> (可选)

<footer> (可选)
```

**Type 类型**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具

**示例**:
```
feat: 添加导出 PDF 功能

实现了将订阅数据导出为 PDF 报告的功能，
包含数据表格和支出饼图。

Closes #123
```

### Pull Request 流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📚 学习资源

- [Streamlit 官方文档](https://docs.streamlit.io)
- [Pandas 文档](https://pandas.pydata.org/docs/)
- [Plotly 文档](https://plotly.com/python/)
- [PEP 8 风格指南](https://peps.python.org/pep-0008/)

## 🆘 获取帮助

- 查看 [README.md](README.md)
- 阅读 [Issues](https://github.com/yourusername/mysub-manager/issues)
- 使用 Cursor AI 辅助开发

---

Happy Coding! 🚀
