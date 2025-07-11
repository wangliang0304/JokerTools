#!/usr/bin/env python3
"""
头条文章监控系统主程序

使用方法：
    python main.py [命令] [选项]

命令：
    start       启动监控服务
    test        测试系统组件
    status      查看监控状态
    check       手动执行一次检查

选项：
    --config    指定配置文件路径（默认：config.json）
    --help      显示帮助信息
"""

import sys
import argparse
import json
import logging
from pathlib import Path

from toutiao.monitor import ArticleMonitor


def setup_basic_logging():
    """设置基础日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def check_config_file(config_path: str) -> bool:
    """
    检查配置文件是否存在和有效
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        bool: 配置文件有效返回True
    """
    if not Path(config_path).exists():
        print(f"❌ 配置文件不存在: {config_path}")
        print("请先创建配置文件，参考 config.json 模板")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查必要的配置项
        required_keys = [
            'toutiao.blogger_url',
            'feishu.webhook_url',
            'database.path'
        ]
        
        for key in required_keys:
            keys = key.split('.')
            value = config
            for k in keys:
                if k not in value:
                    print(f"❌ 配置文件缺少必要项: {key}")
                    return False
                value = value[k]
        
        # 检查飞书Webhook URL
        if not config['feishu']['webhook_url'] or config['feishu']['webhook_url'] == 'YOUR_FEISHU_WEBHOOK_URL_HERE':
            print("❌ 请在配置文件中设置正确的飞书Webhook URL")
            return False
        
        print("✅ 配置文件检查通过")
        return True
        
    except json.JSONDecodeError:
        print(f"❌ 配置文件格式错误: {config_path}")
        return False
    except Exception as e:
        print(f"❌ 配置文件检查失败: {e}")
        return False


def cmd_start(args):
    """启动监控服务"""
    print("🚀 启动头条文章监控服务...")
    
    if not check_config_file(args.config):
        return 1
    
    try:
        monitor = ArticleMonitor(args.config)
        monitor.start_monitoring()
        return 0
    except KeyboardInterrupt:
        print("\n👋 监控服务已停止")
        return 0
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1


def cmd_test(args):
    """测试系统组件"""
    print("🔧 测试系统组件...")
    
    if not check_config_file(args.config):
        return 1
    
    try:
        monitor = ArticleMonitor(args.config)
        if monitor.test_system_with_notification():
            print("✅ 系统测试通过")
            return 0
        else:
            print("❌ 系统测试失败")
            return 1
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return 1


def cmd_status(args):
    """查看监控状态"""
    print("📊 查看监控状态...")
    
    if not check_config_file(args.config):
        return 1
    
    try:
        monitor = ArticleMonitor(args.config)
        status = monitor.get_status()
        
        print(f"博主URL: {status.get('blogger_url', 'N/A')}")
        print(f"最新文章数量: {status.get('latest_articles_count', 0)}")
        print(f"未通知文章数量: {status.get('unnotified_count', 0)}")
        print(f"最后检查时间: {status.get('last_check_time', 'N/A')}")
        
        latest_articles = status.get('latest_articles', [])
        if latest_articles:
            print("\n最新文章:")
            for i, article in enumerate(latest_articles[:3], 1):
                print(f"  {i}. {article.get('title', 'N/A')}")
                print(f"     发布时间: {article.get('publish_time', 'N/A')}")
                print(f"     已通知: {'是' if article.get('notified') else '否'}")
        
        return 0
    except Exception as e:
        print(f"❌ 获取状态失败: {e}")
        return 1


def cmd_check(args):
    """手动执行一次检查"""
    print("🔍 手动执行文章检查...")
    
    if not check_config_file(args.config):
        return 1
    
    try:
        monitor = ArticleMonitor(args.config)
        monitor.run_check_cycle()
        print("✅ 检查完成")
        return 0
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return 1


def main():
    """主函数"""
    setup_basic_logging()
    
    parser = argparse.ArgumentParser(
        description='头条文章监控系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py start                    # 启动监控服务
  python main.py test                     # 测试系统组件
  python main.py status                   # 查看监控状态
  python main.py check                    # 手动执行一次检查
  python main.py start --config my.json  # 使用指定配置文件启动
        """
    )
    
    parser.add_argument(
        'command',
        choices=['start', 'test', 'status', 'check'],
        help='要执行的命令'
    )
    
    parser.add_argument(
        '--config',
        default='config.json',
        help='配置文件路径 (默认: config.json)'
    )
    
    args = parser.parse_args()
    
    # 执行对应的命令
    commands = {
        'start': cmd_start,
        'test': cmd_test,
        'status': cmd_status,
        'check': cmd_check
    }
    
    try:
        exit_code = commands[args.command](args)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
        sys.exit(0)


if __name__ == '__main__':
    main()