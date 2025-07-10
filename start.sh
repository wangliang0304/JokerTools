#!/bin/bash

# 头条文章监控系统启动脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_title() {
    echo -e "${BLUE}$1${NC}"
}

# 显示横幅
show_banner() {
    echo "========================================"
    print_title "🚀 头条文章监控系统"
    echo "========================================"
    echo
}

# 检查Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        print_info "请先安装 Python 3.7+"
        exit 1
    fi
}

# 检查配置文件
check_config() {
    if [[ ! -f "config.json" ]]; then
        print_warning "配置文件不存在"
        echo -n "是否运行配置向导？(y/n): "
        read -r choice
        if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
            python3 setup_config.py
            if [[ $? -ne 0 ]]; then
                print_error "配置失败"
                exit 1
            fi
        else
            print_info "请先运行配置向导: python3 setup_config.py"
            exit 1
        fi
    fi
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."
    if ! python3 -c "import requests" &> /dev/null; then
        print_info "安装依赖..."
        pip3 install -r requirements.txt
        if [[ $? -ne 0 ]]; then
            print_error "依赖安装失败"
            exit 1
        fi
    fi
}

# 显示菜单
show_menu() {
    echo
    echo "请选择操作:"
    echo "1. 启动监控服务"
    echo "2. 测试系统"
    echo "3. 查看状态"
    echo "4. 手动检查"
    echo "5. 配置向导"
    echo "6. 退出"
    echo
}

# 启动监控
start_monitor() {
    echo
    print_info "启动监控服务..."
    print_warning "按 Ctrl+C 停止服务"
    echo
    python3 main.py start
}

# 测试系统
test_system() {
    echo
    print_info "测试系统..."
    python3 main.py test
    echo
    read -p "按回车键继续..."
}

# 查看状态
show_status() {
    echo
    print_info "查看状态..."
    python3 main.py status
    echo
    read -p "按回车键继续..."
}

# 手动检查
manual_check() {
    echo
    print_info "手动检查..."
    python3 main.py check
    echo
    read -p "按回车键继续..."
}

# 配置向导
config_wizard() {
    echo
    print_info "运行配置向导..."
    python3 setup_config.py
    echo
    read -p "按回车键继续..."
}

# 主循环
main_loop() {
    while true; do
        show_menu
        echo -n "请输入选择 (1-6): "
        read -r choice
        
        case $choice in
            1)
                start_monitor
                ;;
            2)
                test_system
                ;;
            3)
                show_status
                ;;
            4)
                manual_check
                ;;
            5)
                config_wizard
                ;;
            6)
                echo
                print_info "再见！"
                exit 0
                ;;
            *)
                print_error "无效选择，请重新输入"
                ;;
        esac
    done
}

# 主函数
main() {
    show_banner
    check_python
    check_config
    check_dependencies
    
    # 如果有命令行参数，直接执行
    if [[ $# -gt 0 ]]; then
        case $1 in
            start)
                start_monitor
                ;;
            test)
                python3 main.py test
                ;;
            status)
                python3 main.py status
                ;;
            check)
                python3 main.py check
                ;;
            config)
                python3 setup_config.py
                ;;
            *)
                echo "用法: $0 [start|test|status|check|config]"
                exit 1
                ;;
        esac
    else
        main_loop
    fi
}

# 运行主函数
main "$@"
