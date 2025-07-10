#!/usr/bin/env python3
"""
测试新爬虫策略的脚本
"""

import sys
import logging
from toutiao.crawler_new import ToutiaoCrawler

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_blogger_url():
    """测试博主URL访问"""
    print("🔍 测试博主URL访问...")

    # 使用示例博主URL
    blogger_url = "https://www.toutiao.com/c/user/token/MS4wLjABAAAAu8TLqbwurnpNAkvSb1SB60loMjrybIwxT3py56-uKRM/?source=profile&tab=article"

    print(f"博主URL: {blogger_url}")
    print("✅ 直接使用博主URL，无需提取用户ID")
    print()

def test_get_articles():
    """测试获取文章列表"""
    print("📰 测试获取文章列表...")

    crawler = ToutiaoCrawler()

    # 使用示例博主URL
    blogger_url = "https://www.toutiao.com/c/user/token/MS4wLjABAAAAu8TLqbwurnpNAkvSb1SB60loMjrybIwxT3py56-uKRM/?source=profile&tab=article"

    print(f"正在从博主URL获取文章...")
    print(f"访问URL: {blogger_url}")

    articles = crawler.get_articles_from_url(blogger_url, max_count=5)

    if articles:
        print(f"✅ 成功获取 {len(articles)} 篇文章:")
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. 标题: {article.get('title', 'N/A')[:80]}...")
            print(f"   文章ID: {article.get('article_id', 'N/A')}")
            print(f"   URL: {article.get('url', 'N/A')}")
            print(f"   发布时间: {article.get('publish_time', 'N/A')}")
    else:
        print("❌ 未获取到文章")

def test_get_article_details():
    """测试获取文章详情"""
    print("📄 测试获取文章详情...")
    
    crawler = ToutiaoCrawler()
    
    # 使用示例文章ID
    article_id = "7524937913248006694"
    
    print(f"正在获取文章 {article_id} 的详情...")
    
    details = crawler.get_article_details(article_id)
    
    if details:
        print("✅ 成功获取文章详情:")
        print(f"   文章ID: {details.get('article_id', 'N/A')}")
        print(f"   发布时间: {details.get('publish_time', 'N/A')}")
        print(f"   作者: {details.get('author', 'N/A')}")
        print(f"   摘要: {details.get('summary', 'N/A')[:100]}...")
    else:
        print("❌ 未获取到文章详情")

def test_get_latest_articles():
    """测试获取最新文章（包含详情）"""
    print("🆕 测试获取最新文章（包含详情）...")

    crawler = ToutiaoCrawler()

    # 使用示例博主URL
    blogger_url = "https://www.toutiao.com/c/user/token/MS4wLjABAAAAu8TLqbwurnpNAkvSb1SB60loMjrybIwxT3py56-uKRM/?source=profile&tab=article"

    print(f"正在获取博主的最新文章...")

    articles = crawler.get_latest_articles(blogger_url, limit=3)

    if articles:
        print(f"✅ 成功获取 {len(articles)} 篇最新文章:")
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. 标题: {article.get('title', 'N/A')}")
            print(f"   文章ID: {article.get('article_id', 'N/A')}")
            print(f"   作者: {article.get('author', 'N/A')}")
            print(f"   发布时间: {article.get('publish_time', 'N/A')}")
            print(f"   阅读数: {article.get('read_count', 0)}")
            print(f"   评论数: {article.get('comment_count', 0)}")
            print(f"   URL: {article.get('url', 'N/A')}")
    else:
        print("❌ 未获取到最新文章")

def test_user_access():
    """测试博主URL访问"""
    print("🔐 测试博主URL访问...")

    crawler = ToutiaoCrawler()

    # 使用示例博主URL
    blogger_url = "https://www.toutiao.com/c/user/token/MS4wLjABAAAAu8TLqbwurnpNAkvSb1SB60loMjrybIwxT3py56-uKRM/?source=profile&tab=article"

    print(f"正在测试博主URL访问...")

    can_access = crawler.test_user_access(blogger_url)

    if can_access:
        print("✅ 博主URL访问正常")
    else:
        print("❌ 博主URL访问失败")

def main():
    """主测试函数"""
    print("🚀 开始测试新爬虫策略...\n")
    
    tests = [
        ("博主URL测试", test_blogger_url),
        ("获取文章列表", test_get_articles),
        ("获取文章详情", test_get_article_details),
        ("获取最新文章", test_get_latest_articles),
        ("博主URL访问测试", test_user_access),
    ]
    
    for test_name, test_func in tests:
        print("=" * 60)
        print(f"测试: {test_name}")
        print("=" * 60)
        
        try:
            test_func()
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            logging.exception(f"测试 {test_name} 失败")
        
        print("\n")
    
    print("🎉 测试完成！")

if __name__ == '__main__':
    main()
