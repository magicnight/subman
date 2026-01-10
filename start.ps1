# MySub Manager 快速启动脚本 (PowerShell)
# 使用 uv 包管理器

Write-Host ""
Write-Host "🚀 启动 MySub Manager..." -ForegroundColor Cyan
Write-Host ""

# 检查 uv 是否安装
try {
    $null = Get-Command uv -ErrorAction Stop
    Write-Host "✅ uv 已安装" -ForegroundColor Green
} catch {
    Write-Host "❌ 未检测到 uv，请先安装 uv 包管理器" -ForegroundColor Red
    Write-Host "💡 安装命令: " -NoNewline -ForegroundColor Yellow
    Write-Host "irm https://astral.sh/uv/install.ps1 | iex"
    Read-Host "按 Enter 键退出"
    exit 1
}

Write-Host ""

# 同步依赖（uv 会自动创建/管理虚拟环境）
Write-Host "📦 同步项目依赖..." -ForegroundColor Yellow
uv sync

# 检查数据文件
if (-not (Test-Path "data\subscriptions.csv")) {
    Write-Host "⚠️  未找到订阅数据文件，使用示例数据" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✨ 启动 Streamlit 应用..." -ForegroundColor Magenta
Write-Host "🌐 浏览器将自动打开 http://localhost:8501" -ForegroundColor Cyan
Write-Host "📝 按 Ctrl+C 停止应用" -ForegroundColor Gray
Write-Host ""

# 使用 uv run 运行应用
uv run streamlit run src\main.py
