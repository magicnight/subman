#!/bin/bash
# MySub Manager 快速启动脚本
# 使用 uv 包管理器

echo "🚀 启动 MySub Manager..."
echo ""

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ 未检测到 uv，请先安装 uv 包管理器"
    echo "💡 安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv 已安装"
echo ""

# 同步依赖（uv 会自动创建/管理虚拟环境）
echo "📦 同步项目依赖..."
uv sync

# 检查数据文件
if [ ! -f "data/subscriptions.csv" ]; then
    echo "⚠️  未找到订阅数据文件，使用示例数据"
fi

echo ""
echo "✨ 启动 Streamlit 应用..."
echo "🌐 浏览器将自动打开 http://localhost:8501"
echo "📝 按 Ctrl+C 停止应用"
echo ""

# 使用 uv run 运行应用
uv run streamlit run src/main.py
