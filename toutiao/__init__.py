"""
头条文章监控系统

一个用于监控今日头条博主最新文章并通过飞书机器人发送通知的系统。

主要功能：
1. 定时爬取指定博主的最新文章
2. 检测新发布的文章
3. 通过飞书机器人发送新文章通知
4. 数据持久化存储

使用方法：
    from toutiao.monitor import ArticleMonitor

    monitor = ArticleMonitor('config.json')
    monitor.start_monitoring()
"""

from .monitor import ArticleMonitor
from .database import ArticleDatabase
from .feishu_notifier import FeishuNotifier

# 优先使用优化后的Selenium爬虫
try:
    from .crawler_selenium import ToutiaoSeleniumCrawler as ToutiaoCrawler
except ImportError:
    try:
        from .crawler_new import ToutiaoCrawler
    except ImportError:
        from .crawler import ToutiaoCrawler

__version__ = "2.0.0"
__author__ = "JokerTools"

__all__ = [
    'ArticleMonitor',
    'ToutiaoCrawler',
    'ArticleDatabase',
    'FeishuNotifier'
]