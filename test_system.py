#!/usr/bin/env python3
"""
系统测试脚本
用于验证各个组件是否正常工作
"""

import json
import sys
import logging
from pathlib import Path

# 设置基础日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    try:
        from toutiao.crawler import ToutiaoCrawler
        from toutiao.database import ArticleDatabase
        from toutiao.feishu_notifier import FeishuNotifier
        from toutiao.monitor import ArticleMonitor
        print("✅ 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_config():
    """测试配置文件"""
    print("🔍 测试配置文件...")
    
    config_path = "config.json"
    if not Path(config_path).exists():
        print(f"❌ 配置文件不存在: {config_path}")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查必要字段
        required_fields = [
            ('toutiao', 'user_id'),
            ('feishu', 'webhook_url'),
            ('database', 'path')
        ]
        
        for section, field in required_fields:
            if section not in config:
                print(f"❌ 配置缺少节: {section}")
                return False
            if field not in config[section]:
                print(f"❌ 配置缺少字段: {section}.{field}")
                return False
        
        print("✅ 配置文件格式正确")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 配置文件读取失败: {e}")
        return False

def test_database():
    """测试数据库功能"""
    print("🔍 测试数据库功能...")
    
    try:
        from toutiao.database import ArticleDatabase
        
        # 使用临时数据库
        db = ArticleDatabase("test.db")
        
        # 测试添加文章
        test_article = {
            'article_id': 'test_123',
            'title': '测试文章',
            'url': 'https://test.com/article/123',
            'author': '测试作者',
            'summary': '这是一篇测试文章'
        }
        
        if db.add_article(test_article):
            print("✅ 数据库写入测试通过")
        else:
            print("❌ 数据库写入测试失败")
            return False
        
        # 测试查询
        if db.article_exists('test_123'):
            print("✅ 数据库查询测试通过")
        else:
            print("❌ 数据库查询测试失败")
            return False
        
        # 清理测试数据
        Path("test.db").unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def test_crawler():
    """测试爬虫功能"""
    print("🔍 测试爬虫功能...")
    
    try:
        from toutiao.crawler import ToutiaoCrawler
        
        crawler = ToutiaoCrawler()
        
        # 测试URL解析
        test_url = "https://www.toutiao.com/article/7524937913248006694/?share_uid=MS4wLjABAAAARU520WoPhwMRICwKKawo_wwxcgIZTEFPNotxYaoz33I"
        user_id = crawler.extract_user_id_from_url(test_url)
        
        if user_id:
            print(f"✅ URL解析测试通过，用户ID: {user_id}")
        else:
            print("❌ URL解析测试失败")
            return False
        
        print("✅ 爬虫基础功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 爬虫测试失败: {e}")
        return False

def test_feishu_config():
    """测试飞书配置"""
    print("🔍 测试飞书配置...")
    
    try:
        with open("config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        webhook_url = config['feishu']['webhook_url']
        
        if not webhook_url or webhook_url == 'YOUR_FEISHU_WEBHOOK_URL_HERE':
            print("❌ 飞书Webhook URL未配置")
            print("请在config.json中设置正确的飞书机器人Webhook URL")
            return False
        
        if not webhook_url.startswith('https://open.feishu.cn/open-apis/bot/v2/hook/'):
            print("❌ 飞书Webhook URL格式不正确")
            return False
        
        print("✅ 飞书配置检查通过")
        return True
        
    except Exception as e:
        print(f"❌ 飞书配置测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始系统测试...\n")
    
    tests = [
        ("模块导入", test_imports),
        ("配置文件", test_config),
        ("数据库功能", test_database),
        ("爬虫功能", test_crawler),
        ("飞书配置", test_feishu_config),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常使用")
        return 0
    else:
        print("❌ 部分测试失败，请检查相关配置")
        return 1

if __name__ == '__main__':
    sys.exit(main())
