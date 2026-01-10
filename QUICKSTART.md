# 快速入门指南 (QUICKSTART.md)

## 🎯 5 分钟快速上手

### 第一步：准备环境

确保已安装 Python 3.9+：
```bash
python --version  # 或 python3 --version
```

### 第二步：安装依赖

**方式 1：使用启动脚本（推荐）**

macOS/Linux:
```bash
./start.sh
```

Windows:
```bash
start.bat
```

**方式 2：手动安装**

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 第三步：准备数据

项目已包含示例数据（`data/subscriptions.csv`），可以直接使用。

如果你想使用自己的数据：
1. 打开 `data/subscriptions.csv`
2. 按照格式填入你的订阅数据
3. 保存文件（确保使用 UTF-8 编码）

### 第四步：启动应用

```bash
streamlit run src/main.py
```

浏览器会自动打开 `http://localhost:8501`

## 📊 界面导航

启动后你会看到三个主要页面：

### 1. 📊 仪表盘
- 查看订阅总数、月均支出
- 到期预警提醒
- 快速统计信息

### 2. 📋 订阅列表
- 查看所有订阅详情
- 筛选和排序
- 删除订阅

### 3. 📈 统计分析
- 支出构成饼图
- 订阅类型分布
- 付费时间线

## ➕ 添加第一个订阅

1. 在左侧边栏找到 **"➕ 添加订阅"** 表单
2. 填写以下信息：
   - **服务名称**: 例如 "Netflix"
   - **服务性质**: 选择 "视频"
   - **订阅类型**: 选择 "月付"
   - **金额**: 输入 419
   - **下次付费时间**: 选择日期
   - **自动续费**: 勾选或不勾选
3. 点击 **"✅ 添加订阅"** 按钮
4. 成功！你的第一个订阅已添加

## 🎨 自定义配置

### 修改预警天数

编辑 `src/config.py`:
```python
WARNING_DAYS = 7  # 改为你想要的天数
```

### 修改币种符号

编辑 `src/config.py`:
```python
CURRENCY_SYMBOL = "฿"  # 泰铢
# CURRENCY_SYMBOL = "$"  # 美元
# CURRENCY_SYMBOL = "¥"  # 人民币
```

### 添加新的服务类型

编辑 `data/Service.csv`，添加新行：
```csv
服务性质
AI
视频
软件
你的新类型  # 添加这里
```

## 💡 使用技巧

### 技巧 1: 快速查看即将到期的订阅
1. 打开 **订阅列表**
2. 选择排序方式为 **"剩余天数（升序）"**
3. 最上面的就是最快到期的

### 技巧 2: 找出最贵的订阅
1. 打开 **订阅列表**
2. 选择排序方式为 **"月均成本（降序）"**

### 技巧 3: 分析某一类支出
1. 打开 **统计分析**
2. 查看支出构成饼图
3. 找出占比最大的服务类型

### 技巧 4: 批量管理
- 在 Excel 中编辑 `data/subscriptions.csv`
- 保存后重新加载页面即可看到更新

## ⚠️ 常见问题

### Q: 页面显示乱码？
**A**: CSV 文件编码问题，用记事本打开后另存为 UTF-8-BOM 编码

### Q: 添加订阅后没有显示？
**A**: 刷新页面（F5）或点击侧边栏的导航按钮

### Q: 删除订阅失败？
**A**: 检查 `data/subscriptions.csv` 文件是否被其他程序占用（如 Excel）

### Q: 月均成本计算不对？
**A**: 确保订阅类型正确（年付会自动除以 12）

### Q: 如何备份数据？
**A**: 直接复制 `data/` 文件夹即可

## 🚀 下一步

现在你已经掌握了基础操作，可以：

1. **探索更多功能**
   - 阅读 [README.md](README.md) 了解完整功能
   - 查看 [DEVELOPMENT.md](DEVELOPMENT.md) 学习开发

2. **使用 Cursor AI 辅助开发**
   - 参考 `.cursorrules` 中的提示
   - 使用 Claude Opus 模型获得最佳代码生成质量

3. **自定义和扩展**
   - 添加新的统计图表
   - 实现邮件提醒功能
   - 集成汇率换算

## 📞 需要帮助？

- 查看 [常见问题](#️-常见问题)
- 阅读完整 [README](README.md)
- 提交 [Issue](https://github.com/yourusername/mysub-manager/issues)

---

享受 MySub Manager 带来的便利！ 🎉
