#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整系统测试脚本
按照README.md设计测试整个头条文章监控系统
"""

import sys
import os
import json
import logging
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from toutiao.crawler_selenium import ToutiaoSeleniumCrawler
from toutiao.database import ArticleDatabase
from toutiao.feishu_notifier import FeishuNotifier
from toutiao.monitor import ArticleMonitor

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('system_test.log', encoding='utf-8')
        ]
    )

def test_crawler_component():
    """测试爬虫组件"""
    print("\n" + "="*60)
    print("1. 测试爬虫组件 (ToutiaoSeleniumCrawler)")
    print("="*60)
    
    try:
        # 初始化爬虫
        crawler = ToutiaoSeleniumCrawler()
        blogger_url = "https://www.toutiao.com/c/user/token/MS4wLjABAAAAu8TLqbwurnpNAkvSb1SB60loMjrybIwxT3py56-uKRM/"
        
        print(f"博主URL: {blogger_url}")
        
        # 测试访问
        print("测试博主URL访问...")
        if crawler.test_user_access(blogger_url):
            print("✅ 博主URL访问正常")
        else:
            print("❌ 博主URL访问失败")
            return False
        
        # 测试文章列表获取
        print("测试文章列表获取...")
        articles = crawler.get_articles_from_url(blogger_url, 3)
        
        if articles:
            print(f"✅ 成功获取 {len(articles)} 篇文章")
            
            # 显示文章信息
            for i, article in enumerate(articles, 1):
                print(f"\n  文章 {i}:")
                print(f"    ID: {article['article_id']}")
                print(f"    标题: {article['title'][:50]}...")
                print(f"    阅读数: {article.get('read_count', 0)}")
                print(f"    评论数: {article.get('comment_count', 0)}")
            
            # 测试文章详情获取
            print(f"\n测试文章详情获取...")
            first_article = articles[0]
            details = crawler.get_article_details(first_article['article_id'])
            
            if details and details.get('publish_time'):
                print(f"✅ 成功获取文章详情")
                print(f"    发布时间: {details['publish_time']}")
                print(f"    作者: {details['author']}")
                print(f"    摘要: {details['summary'][:100]}...")
            else:
                print("❌ 文章详情获取失败")
                return False
        else:
            print("❌ 未获取到文章")
            return False
        
        crawler.close()
        print("✅ 爬虫组件测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 爬虫组件测试失败: {e}")
        return False

def test_database_component():
    """测试数据库组件"""
    print("\n" + "="*60)
    print("2. 测试数据库组件 (ArticleDatabase)")
    print("="*60)
    
    try:
        # 初始化数据库
        db = ArticleDatabase("test_articles.db")
        
        # 测试文章
        test_article = {
            'article_id': f'test_{int(time.time())}',
            'title': '测试文章标题',
            'url': 'https://test.com/article/123',
            'author': '测试作者',
            'summary': '这是一个测试文章的摘要',
            'publish_time': '2025-01-01 12:00:00',
            'read_count': 1000,
            'comment_count': 50
        }
        
        # 测试添加文章
        print("测试添加文章...")
        if db.add_article(test_article):
            print("✅ 文章添加成功")
        else:
            print("❌ 文章添加失败")
            return False
        
        # 测试文章存在检查
        print("测试文章存在检查...")
        if db.article_exists(test_article['article_id']):
            print("✅ 文章存在检查正常")
        else:
            print("❌ 文章存在检查失败")
            return False
        
        # 测试获取最新文章
        print("测试获取最新文章...")
        latest_articles = db.get_latest_articles(5)
        if latest_articles:
            print(f"✅ 成功获取 {len(latest_articles)} 篇最新文章")
        else:
            print("❌ 获取最新文章失败")
            return False
        
        # 测试标记为已通知
        print("测试标记为已通知...")
        if db.mark_as_notified(test_article['article_id']):
            print("✅ 标记为已通知成功")
        else:
            print("❌ 标记为已通知失败")
            return False
        
        print("✅ 数据库组件测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据库组件测试失败: {e}")
        return False

def test_feishu_component():
    """测试飞书通知组件"""
    print("\n" + "="*60)
    print("3. 测试飞书通知组件 (FeishuNotifier)")
    print("="*60)
    
    try:
        # 从配置文件读取飞书配置
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        webhook_url = config['feishu']['webhook_url']
        secret = config['feishu'].get('secret')
        
        if webhook_url == "YOUR_FEISHU_WEBHOOK_URL_HERE":
            print("⚠️  飞书Webhook URL未配置，跳过飞书通知测试")
            print("   请在config.json中设置正确的飞书Webhook URL")
            return True
        
        # 初始化飞书通知器
        notifier = FeishuNotifier(webhook_url, secret)
        
        # 测试连接
        print("测试飞书连接...")
        if notifier.test_connection():
            print("✅ 飞书连接测试成功")
        else:
            print("❌ 飞书连接测试失败")
            return False
        
        # 测试文章通知
        print("测试文章通知...")
        test_article = {
            'title': '🧪 系统测试文章',
            'author': '测试作者',
            'publish_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': '这是一个系统测试文章，用于验证飞书通知功能是否正常工作。',
            'url': 'https://test.com/article/test',
            'read_count': 1500,
            'comment_count': 25
        }
        
        if notifier.send_article_notification(test_article):
            print("✅ 文章通知发送成功")
        else:
            print("❌ 文章通知发送失败")
            return False
        
        print("✅ 飞书通知组件测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 飞书通知组件测试失败: {e}")
        return False

def test_monitor_component():
    """测试监控组件"""
    print("\n" + "="*60)
    print("4. 测试监控组件 (ArticleMonitor)")
    print("="*60)
    
    try:
        # 初始化监控器
        monitor = ArticleMonitor('config.json')
        
        # 测试系统
        print("测试监控系统...")
        if monitor.test_system():
            print("✅ 监控系统测试通过")
        else:
            print("❌ 监控系统测试失败")
            return False
        
        # 测试检查周期
        print("测试检查周期...")
        monitor.run_check_cycle()
        print("✅ 检查周期执行完成")
        
        # 测试状态获取
        print("测试状态获取...")
        status = monitor.get_status()
        if status:
            print("✅ 状态获取成功")
            print(f"    博主URL: {status.get('blogger_url', 'N/A')}")
            print(f"    最新文章数量: {status.get('latest_articles_count', 0)}")
            print(f"    未通知文章数量: {status.get('unnotified_count', 0)}")
        else:
            print("❌ 状态获取失败")
            return False
        
        print("✅ 监控组件测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 监控组件测试失败: {e}")
        return False

def main():
    """主测试函数"""
    setup_logging()
    
    print("🚀 头条文章监控系统完整测试")
    print("按照README.md设计测试所有组件")
    print(f"测试时间: {datetime.now()}")
    
    # 测试结果
    results = {
        'crawler': False,
        'database': False,
        'feishu': False,
        'monitor': False
    }
    
    # 依次测试各个组件
    results['crawler'] = test_crawler_component()
    results['database'] = test_database_component()
    results['feishu'] = test_feishu_component()
    results['monitor'] = test_monitor_component()
    
    # 总结测试结果
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    
    success_count = sum(results.values())
    total_count = len(results)
    
    for component, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{component.ljust(10)}: {status}")
    
    print(f"\n总体结果: {success_count}/{total_count} 组件测试通过")
    
    if success_count == total_count:
        print("🎉 所有组件测试通过！系统可以正常运行")
        print("\n下一步:")
        print("1. 配置config.json中的飞书Webhook URL")
        print("2. 运行 python main.py test 进行最终测试")
        print("3. 运行 python main.py start 启动监控服务")
    else:
        print("⚠️  部分组件测试失败，请检查错误信息并修复")
    
    print(f"\n详细日志已保存到: system_test.log")

if __name__ == "__main__":
    main()
