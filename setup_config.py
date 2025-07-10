#!/usr/bin/env python3
"""
配置向导脚本
帮助用户快速配置头条文章监控系统
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs


def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🚀 头条文章监控系统配置向导")
    print("=" * 60)
    print()


def extract_user_id_from_url(url):
    """从URL中提取用户ID"""
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # 尝试从share_uid参数获取
        if 'share_uid' in query_params:
            return query_params['share_uid'][0]

        # 尝试从URL路径中提取 - 新格式
        path_match = re.search(r'/c/user/token/([^/\'"]+)', url)
        if path_match:
            return path_match.group(1)

        # 尝试旧格式
        path_match = re.search(r'/c/user/(\w+)/', url)
        if path_match:
            return path_match.group(1)

        return None
    except:
        return None


def get_toutiao_config():
    """获取头条配置"""
    print("📰 配置头条博主信息")
    print("-" * 30)
    print("请输入博主的主页链接或任意文章链接")
    print("示例: https://www.toutiao.com/c/user/token/用户ID/")
    print()

    while True:
        blogger_url = input("请输入博主链接: ").strip()
        if not blogger_url:
            print("❌ 链接不能为空，请重新输入")
            continue

        if not blogger_url.startswith('http'):
            print("❌ 请输入完整的HTTP链接")
            continue

        # 确保URL包含正确的参数
        if '/c/user/token/' in blogger_url:
            if '?source=profile&tab=article' not in blogger_url:
                if '?' in blogger_url:
                    blogger_url += '&source=profile&tab=article'
                else:
                    blogger_url += '?source=profile&tab=article'
            print(f"✅ 博主链接配置完成")
            break
        else:
            print("❌ 请输入正确的博主主页链接格式")
            print("正确格式: https://www.toutiao.com/c/user/token/用户ID/")
            continue

    while True:
        try:
            interval = input("请输入检查间隔（分钟，建议30-60）[默认30]: ").strip()
            if not interval:
                interval = 30
            else:
                interval = int(interval)

            if interval < 10:
                print("❌ 检查间隔不能少于10分钟")
                continue

            break
        except ValueError:
            print("❌ 请输入有效的数字")

    return {
        "blogger_url": blogger_url,
        "check_interval_minutes": interval
    }


def get_feishu_config():
    """获取飞书配置"""
    print("\n🤖 配置飞书机器人")
    print("-" * 30)
    print("请先在飞书群组中添加自定义机器人，并获取Webhook URL")
    print("操作步骤：群设置 -> 群机器人 -> 添加机器人 -> 自定义机器人")
    print()
    
    while True:
        webhook_url = input("请输入飞书机器人Webhook URL: ").strip()
        if not webhook_url:
            print("❌ Webhook URL不能为空")
            continue
        
        if not webhook_url.startswith('https://open.feishu.cn/open-apis/bot/v2/hook/'):
            print("❌ Webhook URL格式不正确")
            print("正确格式应该是: https://open.feishu.cn/open-apis/bot/v2/hook/...")
            continue
        
        break
    
    secret = input("请输入飞书机器人密钥（可选，直接回车跳过）: ").strip()
    
    return {
        "webhook_url": webhook_url,
        "secret": secret if secret else ""
    }


def get_database_config():
    """获取数据库配置"""
    print("\n💾 配置数据库")
    print("-" * 30)
    
    db_path = input("请输入数据库文件路径 [默认: articles.db]: ").strip()
    if not db_path:
        db_path = "articles.db"
    
    return {
        "path": db_path
    }


def get_logging_config():
    """获取日志配置"""
    print("\n📝 配置日志")
    print("-" * 30)
    
    print("日志级别选项:")
    print("1. DEBUG - 详细调试信息")
    print("2. INFO - 一般信息（推荐）")
    print("3. WARNING - 警告信息")
    print("4. ERROR - 错误信息")
    
    while True:
        choice = input("请选择日志级别 [默认: 2]: ").strip()
        if not choice:
            choice = "2"
        
        level_map = {
            "1": "DEBUG",
            "2": "INFO", 
            "3": "WARNING",
            "4": "ERROR"
        }
        
        if choice in level_map:
            level = level_map[choice]
            break
        else:
            print("❌ 请输入1-4之间的数字")
    
    log_file = input("请输入日志文件路径 [默认: monitor.log]: ").strip()
    if not log_file:
        log_file = "monitor.log"
    
    return {
        "level": level,
        "file": log_file
    }


def save_config(config):
    """保存配置到文件"""
    print("\n💾 保存配置...")
    
    config_path = "config.json"
    
    # 备份现有配置
    if Path(config_path).exists():
        backup_path = "config.json.backup"
        Path(config_path).rename(backup_path)
        print(f"已备份现有配置到: {backup_path}")
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 配置已保存到: {config_path}")
        return True
    except Exception as e:
        print(f"❌ 保存配置失败: {e}")
        return False


def test_config():
    """测试配置"""
    print("\n🔧 测试配置...")
    
    try:
        # 导入测试模块
        from toutiao.crawler import ToutiaoCrawler
        
        # 测试URL解析
        with open("config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        crawler = ToutiaoCrawler()
        user_id = config['toutiao']['user_id']
        
        if user_id:
            print(f"✅ 用户ID配置正确: {user_id}")
        else:
            print("⚠️ 用户ID为空，请确保配置正确")
        
        print("✅ 基础配置测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False


def show_next_steps():
    """显示后续步骤"""
    print("\n🎉 配置完成！")
    print("=" * 60)
    print("后续步骤:")
    print("1. 测试系统: python test_system.py")
    print("2. 手动测试: python main.py test")
    print("3. 启动监控: python main.py start")
    print()
    print("服务管理:")
    print("- 查看状态: python main.py status")
    print("- 手动检查: python main.py check")
    print()
    print("如需修改配置，可以重新运行此脚本或直接编辑 config.json 文件")
    print("=" * 60)


def main():
    """主函数"""
    print_banner()
    
    try:
        # 收集配置信息
        toutiao_config = get_toutiao_config()
        feishu_config = get_feishu_config()
        database_config = get_database_config()
        logging_config = get_logging_config()
        
        # 组装完整配置
        config = {
            "toutiao": toutiao_config,
            "feishu": feishu_config,
            "database": database_config,
            "logging": logging_config
        }
        
        # 显示配置摘要
        print("\n📋 配置摘要")
        print("-" * 30)
        print(f"博主链接: {toutiao_config['blogger_url']}")
        print(f"用户ID: {toutiao_config['user_id']}")
        print(f"检查间隔: {toutiao_config['check_interval_minutes']}分钟")
        print(f"飞书Webhook: {feishu_config['webhook_url'][:50]}...")
        print(f"数据库路径: {database_config['path']}")
        print(f"日志级别: {logging_config['level']}")
        print()
        
        # 确认保存
        confirm = input("确认保存配置？(y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ 配置已取消")
            return 1
        
        # 保存配置
        if not save_config(config):
            return 1
        
        # 测试配置
        test_config()
        
        # 显示后续步骤
        show_next_steps()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n❌ 配置已取消")
        return 1
    except Exception as e:
        print(f"\n❌ 配置过程中发生错误: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
