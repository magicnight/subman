@echo off
REM MySub Manager 快速启动脚本 (Windows)
REM 使用 uv 包管理器

echo.
echo 🚀 启动 MySub Manager...
echo.

REM 检查 uv 是否安装
uv --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 uv，请先安装 uv 包管理器
    echo 💡 安装命令: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)

echo ✅ uv 已安装
echo.

REM 同步依赖（uv 会自动创建/管理虚拟环境）
echo 📦 同步项目依赖...
uv sync

REM 检查数据文件
if not exist "data\subscriptions.csv" (
    echo ⚠️  未找到订阅数据文件，使用示例数据
)

echo.
echo ✨ 启动 Streamlit 应用...
echo 🌐 浏览器将自动打开 http://localhost:8501
echo 📝 按 Ctrl+C 停止应用
echo.

REM 使用 uv run 运行应用
uv run streamlit run src\main.py

pause
