#!/usr/bin/env python3
"""
测试Selenium爬虫策略的脚本
"""

import sys
import logging
from toutiao.crawler_selenium import ToutiaoSeleniumCrawler

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_selenium_crawler():
    """测试Selenium爬虫"""
    print("🚀 测试Selenium爬虫...")
    
    try:
        # 初始化爬虫（使用有头模式便于调试）
        crawler = ToutiaoSeleniumCrawler(headless=False)
        
        # 使用示例博主URL
        blogger_url = "https://www.toutiao.com/c/user/token/MS4wLjABAAAAu8TLqbwurnpNAkvSb1SB60loMjrybIwxT3py56-uKRM/?source=profile&tab=article"
        
        print(f"正在从博主URL获取文章...")
        print(f"访问URL: {blogger_url}")
        
        # 测试获取文章列表
        articles = crawler.get_articles_from_url(blogger_url, max_count=3)
        
        if articles:
            print(f"✅ 成功获取 {len(articles)} 篇文章:")
            for i, article in enumerate(articles, 1):
                print(f"\n{i}. 标题: {article.get('title', 'N/A')[:80]}...")
                print(f"   文章ID: {article.get('article_id', 'N/A')}")
                print(f"   URL: {article.get('url', 'N/A')}")
                
                # 测试获取文章详情
                if article.get('article_id'):
                    print(f"   正在获取详情...")
                    details = crawler.get_article_details(article['article_id'])
                    if details:
                        print(f"   发布时间: {details.get('publish_time', 'N/A')}")
                        print(f"   作者: {details.get('author', 'N/A')}")
                        print(f"   摘要: {details.get('summary', 'N/A')[:100]}...")
        else:
            print("❌ 未获取到文章")
        
        # 测试访问
        print(f"\n🔐 测试博主URL访问...")
        can_access = crawler.test_user_access(blogger_url)
        if can_access:
            print("✅ 博主URL访问正常")
        else:
            print("❌ 博主URL访问失败")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        logging.exception("测试Selenium爬虫失败")
    
    finally:
        # 确保清理资源
        if 'crawler' in locals():
            del crawler

if __name__ == '__main__':
    test_selenium_crawler()
