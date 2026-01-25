#!/bin/bash
# MySub Manager - Linux 服务器部署脚本
# 使用方法: ./deploy.sh [选项]
# 选项:
#   --install    安装依赖和服务
#   --start      启动服务
#   --stop       停止服务
#   --restart    重启服务
#   --status     查看服务状态
#   --logs       查看日志
#   --update     更新代码

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
APP_NAME="subman"
APP_USER="${APP_USER:-$USER}"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"
LOG_DIR="${APP_DIR}/logs"
PORT="${PORT:-8501}"
HOST="${HOST:-0.0.0.0}"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查是否为 root 用户（某些操作需要）
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "此操作需要 root 权限，请使用 sudo"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    print_info "检查系统依赖..."
    
    local missing_deps=()
    
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! command -v uv &> /dev/null; then
        print_warning "未检测到 uv，将自动安装..."
        install_uv
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_error "缺少以下依赖: ${missing_deps[*]}"
        print_info "请先安装缺少的依赖"
        exit 1
    fi
    
    print_success "依赖检查完成"
}

# 安装 uv
install_uv() {
    print_info "安装 uv 包管理器..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # 添加到 PATH（如果不在 PATH 中）
    if ! command -v uv &> /dev/null; then
        export PATH="$HOME/.cargo/bin:$PATH"
        if [ -f "$HOME/.bashrc" ]; then
            echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> "$HOME/.bashrc"
        fi
    fi
    
    print_success "uv 安装完成"
}

# 安装项目依赖
install_dependencies() {
    print_info "安装项目依赖..."
    cd "$APP_DIR"
    
    # 同步依赖
    uv sync
    
    print_success "依赖安装完成"
}

# 创建必要的目录
create_directories() {
    print_info "创建必要的目录..."
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$APP_DIR/data"
    
    # 确保数据文件存在
    if [ ! -f "$APP_DIR/data/subscriptions.csv" ]; then
        print_warning "未找到 subscriptions.csv，创建示例文件..."
        cat > "$APP_DIR/data/subscriptions.csv" << 'EOF'
名称,供应商,服务性质,订阅类型,金额,货币,下次付费时间,自动续费
示例服务,示例供应商,AI,月付,100.00,THB,2025-12-31,FALSE
EOF
    fi
    
    print_success "目录创建完成"
}

# 创建 systemd 服务文件
create_systemd_service() {
    check_root
    
    print_info "创建 systemd 服务文件..."
    
    # 获取 uv 的完整路径
    UV_PATH=$(which uv || echo "$HOME/.cargo/bin/uv")
    
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=MySub Manager - Subscription Management Tool
After=network.target

[Service]
Type=simple
User=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${PATH}:${HOME}/.cargo/bin"
ExecStart=${UV_PATH} run streamlit run src/main.py --server.port=${PORT} --server.address=${HOST} --server.headless=true
Restart=always
RestartSec=10
StandardOutput=append:${LOG_DIR}/app.log
StandardError=append:${LOG_DIR}/error.log

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载 systemd
    systemctl daemon-reload
    
    print_success "systemd 服务文件创建完成"
}

# 安装服务
install_service() {
    print_info "开始安装服务..."
    
    check_dependencies
    install_dependencies
    create_directories
    create_systemd_service
    
    # 启用服务
    systemctl enable "${APP_NAME}.service"
    
    print_success "服务安装完成！"
    print_info "使用以下命令管理服务:"
    echo "  启动: sudo systemctl start ${APP_NAME}"
    echo "  停止: sudo systemctl stop ${APP_NAME}"
    echo "  状态: sudo systemctl status ${APP_NAME}"
    echo "  日志: sudo journalctl -u ${APP_NAME} -f"
}

# 启动服务
start_service() {
    if [ "$EUID" -eq 0 ]; then
        systemctl start "${APP_NAME}.service"
        print_success "服务已启动"
    else
        print_info "启动应用（前台运行）..."
        cd "$APP_DIR"
        uv run streamlit run src/main.py --server.port="${PORT}" --server.address="${HOST}"
    fi
}

# 停止服务
stop_service() {
    if [ "$EUID" -eq 0 ]; then
        systemctl stop "${APP_NAME}.service"
        print_success "服务已停止"
    else
        print_warning "请使用 sudo 停止 systemd 服务，或使用 Ctrl+C 停止前台进程"
    fi
}

# 重启服务
restart_service() {
    if [ "$EUID" -eq 0 ]; then
        systemctl restart "${APP_NAME}.service"
        print_success "服务已重启"
    else
        print_warning "请使用 sudo 重启 systemd 服务"
    fi
}

# 查看服务状态
show_status() {
    if [ "$EUID" -eq 0 ]; then
        systemctl status "${APP_NAME}.service"
    else
        print_info "应用状态:"
        if pgrep -f "streamlit run" > /dev/null; then
            print_success "应用正在运行"
            ps aux | grep "streamlit run" | grep -v grep
        else
            print_warning "应用未运行"
        fi
    fi
}

# 查看日志
show_logs() {
    if [ "$EUID" -eq 0 ]; then
        journalctl -u "${APP_NAME}.service" -f
    else
        if [ -f "${LOG_DIR}/app.log" ]; then
            tail -f "${LOG_DIR}/app.log"
        else
            print_warning "日志文件不存在"
        fi
    fi
}

# 更新代码
update_code() {
    print_info "更新代码..."
    cd "$APP_DIR"
    
    if [ -d ".git" ]; then
        git pull origin main
        install_dependencies
        
        if [ "$EUID" -eq 0 ]; then
            restart_service
        fi
        
        print_success "代码更新完成"
    else
        print_warning "未检测到 Git 仓库"
    fi
}

# 主函数
main() {
    case "${1:-}" in
        --install)
            install_service
            ;;
        --start)
            start_service
            ;;
        --stop)
            stop_service
            ;;
        --restart)
            restart_service
            ;;
        --status)
            show_status
            ;;
        --logs)
            show_logs
            ;;
        --update)
            update_code
            ;;
        *)
            echo "MySub Manager 部署脚本"
            echo ""
            echo "使用方法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --install    安装依赖和服务（需要 root 权限）"
            echo "  --start      启动服务"
            echo "  --stop       停止服务"
            echo "  --restart    重启服务"
            echo "  --status     查看服务状态"
            echo "  --logs       查看日志"
            echo "  --update     更新代码并重启服务"
            echo ""
            echo "环境变量:"
            echo "  APP_USER     运行服务的用户（默认: 当前用户）"
            echo "  PORT         服务端口（默认: 8501）"
            echo "  HOST         监听地址（默认: 0.0.0.0）"
            echo ""
            echo "示例:"
            echo "  sudo $0 --install    # 安装服务"
            echo "  sudo $0 --start      # 启动服务"
            echo "  $0 --status          # 查看状态"
            exit 1
            ;;
    esac
}

main "$@"
