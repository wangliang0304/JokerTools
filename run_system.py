#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
头条文章监控系统启动脚本
提供简化的系统操作界面
"""

import sys
import os
import json
import subprocess
from pathlib import Path

def print_banner():
    """打印系统横幅"""
    print("=" * 60)
    print("🚀 头条文章监控系统")
    print("=" * 60)
    print("基于优化后的Selenium爬虫，支持完整的文章信息提取")
    print("包括：文章ID、标题、作者、发布时间、阅读数、评论数、摘要")
    print("=" * 60)

def check_config():
    """检查配置文件"""
    config_file = Path("config.json")
    if not config_file.exists():
        print("❌ 配置文件 config.json 不存在")
        print("请先创建配置文件，参考以下模板：")
        print_config_template()
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查必要配置
        if config['feishu']['webhook_url'] == "YOUR_FEISHU_WEBHOOK_URL_HERE":
            print("⚠️  请在 config.json 中设置正确的飞书Webhook URL")
            return False
        
        print("✅ 配置文件检查通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置文件检查失败: {e}")
        return False

def print_config_template():
    """打印配置文件模板"""
    template = '''
{
  "toutiao": {
    "blogger_url": "https://www.toutiao.com/c/user/token/YOUR_BLOGGER_TOKEN/",
    "check_interval_minutes": 30
  },
  "feishu": {
    "webhook_url": "YOUR_FEISHU_WEBHOOK_URL_HERE",
    "secret": "YOUR_FEISHU_SECRET_HERE"
  },
  "database": {
    "path": "articles.db"
  },
  "logging": {
    "level": "INFO",
    "file": "monitor.log"
  }
}
'''
    print(template)

def run_command(cmd, description):
    """运行命令"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"✅ {description}成功")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description}失败")
            if result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description}异常: {e}")
        return False

def install_dependencies():
    """安装依赖"""
    print("\n📦 安装系统依赖...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本: {sys.version}")
    
    # 安装依赖包
    return run_command("pip install -r requirements.txt", "安装Python依赖包")

def test_system():
    """测试系统"""
    print("\n🧪 测试系统组件...")
    
    # 运行完整系统测试
    if run_command("python test_complete_system.py", "完整系统测试"):
        print("✅ 系统测试通过")
        return True
    else:
        print("❌ 系统测试失败，请检查错误信息")
        return False

def test_crawler():
    """测试爬虫"""
    print("\n🕷️ 测试爬虫组件...")
    return run_command("python test_selenium_crawler.py", "Selenium爬虫测试")

def start_monitoring():
    """启动监控服务"""
    print("\n🚀 启动监控服务...")
    print("按 Ctrl+C 停止监控")
    
    try:
        subprocess.run("python main.py start", shell=True)
    except KeyboardInterrupt:
        print("\n👋 监控服务已停止")

def show_status():
    """显示系统状态"""
    print("\n📊 查看系统状态...")
    run_command("python main.py status", "获取系统状态")

def manual_check():
    """手动执行检查"""
    print("\n🔍 手动执行文章检查...")
    run_command("python main.py check", "手动检查文章")

def show_menu():
    """显示菜单"""
    print("\n📋 请选择操作:")
    print("1. 安装依赖")
    print("2. 测试爬虫")
    print("3. 测试系统")
    print("4. 查看状态")
    print("5. 手动检查")
    print("6. 启动监控")
    print("0. 退出")
    print("-" * 30)

def main():
    """主函数"""
    print_banner()
    
    while True:
        show_menu()
        
        try:
            choice = input("请输入选项 (0-6): ").strip()
            
            if choice == "0":
                print("👋 再见！")
                break
            elif choice == "1":
                install_dependencies()
            elif choice == "2":
                test_crawler()
            elif choice == "3":
                if check_config():
                    test_system()
            elif choice == "4":
                if check_config():
                    show_status()
            elif choice == "5":
                if check_config():
                    manual_check()
            elif choice == "6":
                if check_config():
                    start_monitoring()
            else:
                print("❌ 无效选项，请重新选择")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    main()
    # manual_check()