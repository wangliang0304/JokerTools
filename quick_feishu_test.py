#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试飞书通知修复
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from toutiao.feishu_notifier import FeishuNotifier

def main():
    """快速测试"""
    print("🧪 快速测试飞书通知修复...")
    
    try:
        # 读取配置
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        webhook_url = config['feishu']['webhook_url']
        secret = config['feishu'].get('secret')
        
        # 初始化通知器
        notifier = FeishuNotifier(webhook_url, secret)
        
        # 测试文章（模拟之前失败的文章）
        test_article = {
            'title': 'WTT美国大满贯9日战报：混双8强出炉！栋曼横扫晋级；国乒6战全胜',
            'author': '纯侃体育',
            'publish_time': '2025-07-09 11:39:17',
            'summary': '北京时间7月9日上午，乒乓球WTT美国大满贯继续进行，混双1/4决赛全部结束。',
            'url': 'https://www.toutiao.com/article/7524937913248006694/',
            'read_count': 59000,
            'comment_count': 33
        }
        
        print("发送测试文章通知...")
        if notifier.send_article_notification(test_article):
            print("✅ 文章通知发送成功！修复有效")
        else:
            print("❌ 文章通知发送失败")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    main()
