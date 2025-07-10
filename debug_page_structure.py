#!/usr/bin/env python3
"""
调试页面结构的脚本
"""

import requests
import logging
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_page_structure():
    """调试页面结构"""
    print("🔍 调试页面结构...")
    
    blogger_url = "https://www.toutiao.com/c/user/token/MS4wLjABAAAAu8TLqbwurnpNAkvSb1SB60loMjrybIwxT3py56-uKRM/?source=profile&tab=article"
    
    print(f"访问URL: {blogger_url}")
    
    # 设置请求头
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
    ]
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        response = session.get(blogger_url, timeout=15)
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)}")
        
        if response.status_code == 200:
            # 保存原始HTML
            with open('debug_page_structure.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("✅ 页面内容已保存到 debug_page_structure.html")
            
            # 解析页面
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查看页面标题
            title = soup.find('title')
            if title:
                print(f"\n页面标题: {title.get_text()}")
            
            # 查找所有可能的文章链接
            print("\n🔍 查找文章链接...")
            
            # 方法1：查找class="title"的链接
            title_links = soup.find_all('a', class_='title')
            print(f"找到 {len(title_links)} 个class='title'的链接")
            for i, link in enumerate(title_links[:3]):
                print(f"  {i+1}. href: {link.get('href')}")
                print(f"     text: {link.get_text(strip=True)[:50]}...")
                print(f"     aria-label: {link.get('aria-label', '')[:50]}...")
            
            # 方法2：查找所有包含/article/的链接
            article_links = soup.find_all('a', href=lambda x: x and '/article/' in x)
            print(f"\n找到 {len(article_links)} 个包含'/article/'的链接")
            for i, link in enumerate(article_links[:5]):
                print(f"  {i+1}. href: {link.get('href')}")
                print(f"     text: {link.get_text(strip=True)[:50]}...")
                print(f"     class: {link.get('class')}")
                print(f"     aria-label: {link.get('aria-label', '')[:50]}...")
            
            # 方法3：查找所有链接
            all_links = soup.find_all('a', href=True)
            print(f"\n总共找到 {len(all_links)} 个链接")
            
            # 查找可能的文章容器
            print("\n🔍 查找文章容器...")
            
            # 查找可能的文章卡片
            article_cards = soup.find_all('div', class_=lambda x: x and ('article' in str(x).lower() or 'card' in str(x).lower() or 'feed' in str(x).lower()))
            print(f"找到 {len(article_cards)} 个可能的文章卡片")
            for i, card in enumerate(article_cards[:3]):
                print(f"  {i+1}. class: {card.get('class')}")
            
            # 查找script标签中的数据
            print("\n🔍 查找script标签中的数据...")
            scripts = soup.find_all('script')
            print(f"找到 {len(scripts)} 个script标签")
            
            # 查找可能包含数据的script标签
            for i, script in enumerate(scripts):
                if script.string and ('article' in script.string.lower() or 'data' in script.string.lower()):
                    print(f"Script {i+1} 可能包含数据: {script.string[:200]}...")
                    
                    # 如果包含文章数据，保存到文件
                    if 'article' in script.string.lower():
                        with open(f'debug_script_{i+1}.txt', 'w', encoding='utf-8') as f:
                            f.write(script.string)
                        print(f"  已保存到 debug_script_{i+1}.txt")
            
            # 查找特定的元素
            print("\n🔍 查找特定元素...")
            
            # 查找可能的文章列表容器
            containers = soup.find_all(['div', 'section', 'ul'], class_=lambda x: x and any(keyword in str(x).lower() for keyword in ['list', 'content', 'main', 'wrapper']))
            print(f"找到 {len(containers)} 个可能的容器")
            for i, container in enumerate(containers[:3]):
                print(f"  {i+1}. 标签: {container.name}, class: {container.get('class')}")
                # 查找容器内的链接
                inner_links = container.find_all('a', href=True)
                print(f"     内部链接数: {len(inner_links)}")
            
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:500]}...")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == '__main__':
    debug_page_structure()
