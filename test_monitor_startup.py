#!/usr/bin/env python3
"""
测试监控服务启动流程
验证启动时不会发送测试通知
"""

import sys
import logging
from toutiao.monitor import ArticleMonitor

def test_monitor_startup():
    """测试监控服务启动"""
    print("🧪 测试监控服务启动流程...")
    
    try:
        # 设置日志级别
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        # 初始化监控服务
        monitor = ArticleMonitor('config.json')
        
        print("✅ 监控服务初始化成功")
        
        # 测试系统（不发送通知）
        print("\n🔧 测试系统组件（不发送通知）...")
        if monitor.test_system(send_test_notification=False):
            print("✅ 系统测试通过（无通知）")
        else:
            print("❌ 系统测试失败")
            return False
        
        # 测试系统（发送通知）
        print("\n📨 测试系统组件（发送通知）...")
        if monitor.test_system_with_notification():
            print("✅ 系统测试通过（含通知）")
        else:
            print("❌ 系统测试失败")
            return False
        
        print("\n✅ 所有测试通过！")
        print("现在启动监控服务时不会发送测试通知")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == '__main__':
    success = test_monitor_startup()
    sys.exit(0 if success else 1)
