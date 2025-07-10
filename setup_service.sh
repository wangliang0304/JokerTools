#!/bin/bash

# 头条文章监控系统服务安装脚本
# 适用于 Linux 系统 (systemd)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 检查系统要求
check_requirements() {
    print_info "检查系统要求..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装，请先安装Python3"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 未安装，请先安装pip3"
        exit 1
    fi
    
    # 检查systemd
    if ! command -v systemctl &> /dev/null; then
        print_error "systemd 未找到，此脚本仅支持systemd系统"
        exit 1
    fi
    
    print_info "系统要求检查通过"
}

# 安装Python依赖
install_dependencies() {
    print_info "安装Python依赖..."
    
    if [[ -f "requirements.txt" ]]; then
        pip3 install --user -r requirements.txt
        print_info "依赖安装完成"
    else
        print_error "requirements.txt 文件未找到"
        exit 1
    fi
}

# 创建systemd服务文件
create_service_file() {
    print_info "创建systemd服务文件..."
    
    local current_dir=$(pwd)
    local current_user=$(whoami)
    local python_path=$(which python3)
    
    local service_content="[Unit]
Description=Toutiao Article Monitor
After=network.target

[Service]
Type=simple
User=${current_user}
WorkingDirectory=${current_dir}
ExecStart=${python_path} main.py start
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target"

    echo "$service_content" | sudo tee /etc/systemd/system/toutiao-monitor.service > /dev/null
    print_info "服务文件创建完成: /etc/systemd/system/toutiao-monitor.service"
}

# 配置服务
setup_service() {
    print_info "配置systemd服务..."
    
    # 重新加载systemd配置
    sudo systemctl daemon-reload
    
    # 启用服务
    sudo systemctl enable toutiao-monitor.service
    
    print_info "服务配置完成"
}

# 检查配置文件
check_config() {
    print_info "检查配置文件..."
    
    if [[ ! -f "config.json" ]]; then
        print_warning "config.json 文件不存在，请先配置系统"
        print_info "你可以编辑 config.json 文件来配置系统"
        return 1
    fi
    
    # 简单检查配置文件格式
    if ! python3 -c "import json; json.load(open('config.json'))" 2>/dev/null; then
        print_error "config.json 文件格式错误"
        return 1
    fi
    
    print_info "配置文件检查通过"
    return 0
}

# 测试系统
test_system() {
    print_info "测试系统组件..."
    
    if python3 main.py test; then
        print_info "系统测试通过"
        return 0
    else
        print_error "系统测试失败，请检查配置"
        return 1
    fi
}

# 显示使用说明
show_usage() {
    print_info "服务安装完成！"
    echo
    echo "服务管理命令:"
    echo "  启动服务: sudo systemctl start toutiao-monitor"
    echo "  停止服务: sudo systemctl stop toutiao-monitor"
    echo "  重启服务: sudo systemctl restart toutiao-monitor"
    echo "  查看状态: sudo systemctl status toutiao-monitor"
    echo "  查看日志: sudo journalctl -u toutiao-monitor -f"
    echo
    echo "手动管理命令:"
    echo "  测试系统: python3 main.py test"
    echo "  查看状态: python3 main.py status"
    echo "  手动检查: python3 main.py check"
    echo
    print_warning "请确保已正确配置 config.json 文件中的飞书Webhook URL"
}

# 主函数
main() {
    print_info "开始安装头条文章监控系统服务..."
    
    # 检查权限
    check_root
    
    # 检查系统要求
    check_requirements
    
    # 安装依赖
    install_dependencies
    
    # 检查配置文件
    if check_config; then
        # 测试系统
        if ! test_system; then
            print_warning "系统测试失败，但仍会继续安装服务"
            print_warning "请检查配置文件后手动启动服务"
        fi
    else
        print_warning "配置文件检查失败，请先配置系统"
    fi
    
    # 创建服务文件
    create_service_file
    
    # 配置服务
    setup_service
    
    # 显示使用说明
    show_usage
    
    print_info "安装完成！"
}

# 运行主函数
main "$@"
