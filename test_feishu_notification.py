#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试飞书通知功能
"""

import sys
import os
import json
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from toutiao.feishu_notifier import FeishuNotifier

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def test_feishu_notification():
    """测试飞书通知"""
    print("🧪 测试飞书通知功能...")
    
    try:
        # 从配置文件读取飞书配置
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        webhook_url = config['feishu']['webhook_url']
        secret = config['feishu'].get('secret')
        
        if webhook_url == "YOUR_FEISHU_WEBHOOK_URL_HERE":
            print("❌ 请在config.json中设置正确的飞书Webhook URL")
            return False
        
        print(f"飞书Webhook URL: {webhook_url[:50]}...")
        
        # 初始化飞书通知器
        notifier = FeishuNotifier(webhook_url, secret)
        
        # 测试简单文本消息
        print("\n1. 测试简单文本消息...")
        if notifier.send_text_message("🧪 飞书通知测试 - 简单文本消息"):
            print("✅ 简单文本消息发送成功")
        else:
            print("❌ 简单文本消息发送失败")
            return False
        
        # 测试文章通知（使用新的简单格式）
        print("\n2. 测试文章通知（简单格式）...")
        test_article = {
            'title': '🧪 测试文章标题',
            'author': '测试作者',
            'publish_time': '2025-07-10 16:30:00',
            'summary': '这是一个测试文章的摘要，用于验证飞书通知功能是否正常工作。',
            'url': 'https://test.com/article/test',
            'read_count': 1500,
            'comment_count': 25
        }
        
        if notifier.send_article_notification(test_article):
            print("✅ 文章通知发送成功")
        else:
            print("❌ 文章通知发送失败")
            return False
        
        # 测试富文本消息（如果简单格式成功）
        print("\n3. 测试富文本消息...")
        try:
            if notifier.send_rich_article_notification(test_article):
                print("✅ 富文本消息发送成功")
            else:
                print("⚠️  富文本消息发送失败，但简单格式可用")
        except Exception as e:
            print(f"⚠️  富文本消息测试异常: {e}")
        
        # 测试边界情况
        print("\n4. 测试边界情况...")
        edge_case_article = {
            'title': '',  # 空标题
            'author': None,  # None作者
            'publish_time': '',  # 空时间
            'summary': None,  # None摘要
            'url': 'https://test.com/edge-case',
            'read_count': 0,
            'comment_count': 0
        }
        
        if notifier.send_article_notification(edge_case_article):
            print("✅ 边界情况处理成功")
        else:
            print("❌ 边界情况处理失败")
        
        print("\n✅ 飞书通知功能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        logging.exception("飞书通知测试失败")
        return False

def test_message_formats():
    """测试不同的消息格式"""
    print("\n📝 测试不同的消息格式...")
    
    try:
        # 从配置文件读取飞书配置
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        webhook_url = config['feishu']['webhook_url']
        secret = config['feishu'].get('secret')
        
        if webhook_url == "YOUR_FEISHU_WEBHOOK_URL_HERE":
            print("❌ 请在config.json中设置正确的飞书Webhook URL")
            return False
        
        notifier = FeishuNotifier(webhook_url, secret)
        
        # 测试不同类型的文章数据
        test_cases = [
            {
                'name': '完整信息文章',
                'article': {
                    'title': 'WTT美国大满贯9日战报：混双8强出炉！栋曼横扫晋级；国乒6战全胜',
                    'author': '纯侃体育',
                    'publish_time': '2025-07-09 11:39:17',
                    'summary': '北京时间7月9日上午，乒乓球WTT美国大满贯继续进行，混双1/4决赛全部结束，8强全部产生。',
                    'url': 'https://www.toutiao.com/article/7524937913248006694/',
                    'read_count': 59000,
                    'comment_count': 33
                }
            },
            {
                'name': '最小信息文章',
                'article': {
                    'title': '测试文章',
                    'url': 'https://test.com/minimal'
                }
            },
            {
                'name': '高阅读量文章',
                'article': {
                    'title': '热门文章测试',
                    'author': '热门作者',
                    'read_count': 1250000,  # 125万
                    'comment_count': 5680,
                    'url': 'https://test.com/popular'
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. 测试{test_case['name']}...")
            if notifier.send_article_notification(test_case['article']):
                print(f"✅ {test_case['name']}发送成功")
            else:
                print(f"❌ {test_case['name']}发送失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 消息格式测试失败: {e}")
        return False

def main():
    """主函数"""
    setup_logging()
    
    print("🚀 飞书通知功能测试")
    print("=" * 50)
    
    # 基础功能测试
    if not test_feishu_notification():
        print("\n❌ 基础功能测试失败")
        return
    
    # 消息格式测试
    if not test_message_formats():
        print("\n❌ 消息格式测试失败")
        return
    
    print("\n🎉 所有测试通过！")
    print("飞书通知功能正常工作")

if __name__ == "__main__":
    main()
