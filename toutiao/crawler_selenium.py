"""
头条文章爬虫模块 - Selenium版本
使用Selenium处理JavaScript渲染的页面
"""

import re
import json
import time
import random
import logging
import urllib.parse
from urllib.parse import urlparse, parse_qs, urljoin, unquote
from typing import List, Dict, Optional
from fake_useragent import UserAgent
from retrying import retry
from bs4 import BeautifulSoup
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium未安装，无法使用Selenium爬虫")


class ToutiaoSeleniumCrawler:
    """头条文章爬虫类 - Selenium版本"""
    
    def __init__(self, headless=True):
        """
        初始化爬虫
        
        Args:
            headless: 是否使用无头模式
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium未安装，请安装selenium和webdriver-manager")
        
        self.headless = headless
        self.driver = None
        self.ua = UserAgent()
        self.setup_driver()
    
    def setup_driver(self):
        """设置Selenium WebDriver"""
        try:
            options = Options()
            
            if self.headless:
                options.add_argument('--headless')
            
            # 反检测设置
            options.add_argument("--disable-gcm")   # 禁用GCM，避免被检测
            options.add_argument("--disable-notifications")
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')

            # 使用PC端User-Agent确保访问PC版页面
            pc_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            options.add_argument(f'--user-agent={pc_user_agent}')

            # 设置窗口大小为PC端 # 这个很重要，如果是移动端，会有加载数据不全的问题
            options.add_argument('--window-size=1920,1080')

            # 设置视口大小
            options.add_argument('--viewport-size=1920,1080')
            
            # 使用webdriver-manager自动管理ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # 执行反检测脚本
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # 设置窗口大小确保PC模式
            self.driver.set_window_size(1920, 1080)

            logging.info("Selenium WebDriver初始化成功")
            
        except Exception as e:
            logging.error(f"Selenium初始化失败: {e}")
            raise
    
    def __del__(self):
        """析构函数，清理资源"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def get_articles_from_url(self, blogger_url: str, max_count: int = 10) -> List[Dict]:
        """
        直接从博主URL获取文章列表
        
        Args:
            blogger_url: 博主URL链接
            max_count: 最大获取文章数量
            
        Returns:
            List[Dict]: 文章列表
        """
        try:
            # 确保URL包含正确的参数
            if '?source=profile&tab=article' not in blogger_url:
                if '?' in blogger_url:
                    blogger_url += '&source=profile&tab=article'
                else:
                    blogger_url += '?source=profile&tab=article'
            
            logging.info(f"访问博主URL: {blogger_url}")
            
            # 使用Selenium访问页面
            self.driver.get(blogger_url)
            
            # 等待页面加载
            time.sleep(random.uniform(30, 35))
            
            # 等待文章列表加载
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "profile-article-card-wrapper"))
                )
                logging.info("文章容器加载成功")
            except:
                logging.warning("等待文章容器加载超时，尝试继续")

            # # 滚动页面以触发内容加载
            # logging.debug("滚动页面以触发内容加载...")
            # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # time.sleep(3)
            #
            # # 再次滚动确保内容完全加载
            # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 获取页面源码
            html_content = self.driver.page_source

            # 解析文章列表
            articles = self._parse_articles_from_html(html_content, max_count)
            logging.info(f"成功从URL获取 {len(articles)} 篇文章")
            return articles
                
        except Exception as e:
            logging.error(f"从URL获取文章失败: {e}")
            return []
    
    def _parse_articles_from_html(self, html_content: str, max_count: int) -> List[Dict]:
        """
        从HTML内容中解析文章列表

        Args:
            html_content: HTML内容
            max_count: 最大文章数量

        Returns:
            List[Dict]: 文章列表
        """
        articles = []

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # 基于实际HTML结构的精确解析策略
            # 首先查找文章卡片容器
            article_containers = soup.find_all('div', class_='profile-article-card-wrapper')

            if article_containers:
                logging.info(f"找到 {len(article_containers)} 个文章卡片容器")

                for container in article_containers[:max_count]:
                    try:
                        # 在每个容器中查找文章链接
                        # 基于实际HTML结构: <a href="/article/7524937913248006694/" target="_blank" rel="noopener" title="..." aria-hidden="false" tabindex="0">
                        article_link = container.find('a', href=re.compile(r'/article/\d+/'))

                        if not article_link:
                            continue

                        href = article_link.get('href', '')
                        if not href:
                            continue

                        # 提取文章ID
                        article_id_match = re.search(r'/article/(\d+)/', href)
                        if not article_id_match:
                            continue

                        article_id = article_id_match.group(1)

                        # 提取标题 - 优先从title属性获取
                        title = article_link.get('title', '').strip()
                        if not title:
                            # 如果title属性为空，尝试从aria-label获取
                            title = article_link.get('aria-label', '').strip()
                        if not title:
                            # 最后尝试从链接文本获取
                            title = article_link.get_text(strip=True)

                        # 过滤无效标题
                        if not title or len(title) < 5:
                            continue

                        # 构建完整URL
                        article_url = urljoin('https://www.toutiao.com', href)

                        # 提取阅读数和评论数
                        read_count = 0
                        comment_count = 0

                        # 查找阅读数 - 基于实际HTML结构
                        read_elem = container.find('div', class_='profile-feed-card-tools-text')
                        if read_elem:
                            read_text = read_elem.get_text(strip=True)
                            # 匹配格式如: "5.9万阅读", "266万阅读"
                            read_match = re.search(r'([\d.]+)([万千]?)阅读', read_text)
                            if read_match:
                                num = float(read_match.group(1))
                                unit = read_match.group(2)
                                if unit == '万':
                                    read_count = int(num * 10000)
                                elif unit == '千':
                                    read_count = int(num * 1000)
                                else:
                                    read_count = int(num)

                        # 查找评论数 - 基于实际HTML结构
                        comment_elem = container.find('a', href=re.compile(r'#comment'))
                        if comment_elem:
                            comment_text = comment_elem.get_text(strip=True)
                            # 匹配格式如: "33评论", "3862评论"
                            comment_match = re.search(r'(\d+)评论', comment_text)
                            if comment_match:
                                comment_count = int(comment_match.group(1))

                        # 提取发布时间（如果在列表页面有的话）
                        publish_time = ''
                        time_elem = container.find('div', class_='feed-card-footer-time-cmp')
                        if time_elem:
                            time_text = time_elem.get_text(strip=True)
                            # 匹配格式如: "9小时前", "前天16:35", "2021年09月18日"
                            if time_text and ('前' in time_text or '年' in time_text or '小时' in time_text or '分钟' in time_text or '天前' in time_text):
                                publish_time = time_text

                        article = {
                            'article_id': article_id,
                            'title': title,
                            'url': article_url,
                            'author': '',
                            'summary': '',
                            'publish_time': publish_time,
                            'read_count': read_count,
                            'comment_count': comment_count
                        }

                        articles.append(article)
                        logging.debug(f"解析文章: {title[:50]}... (ID:{article_id}, 阅读:{read_count}, 评论:{comment_count})")

                    except Exception as e:
                        logging.warning(f"解析单个文章容器失败: {e}")
                        continue

            else:
                # 如果没有找到标准容器，使用备用解析策略
                logging.warning("未找到标准文章容器，使用备用解析策略...")
                self._parse_articles_fallback(soup, articles, max_count)

        except Exception as e:
            logging.error(f"解析HTML失败: {e}")

        return articles

    def _parse_articles_fallback(self, soup, articles: List[Dict], max_count: int):
        """
        备用文章解析策略

        Args:
            soup: BeautifulSoup对象
            articles: 文章列表
            max_count: 最大文章数量
        """
        try:
            # 查找所有包含article链接的a标签
            all_links = soup.find_all('a', href=re.compile(r'/article/\d+/'))

            logging.info(f"备用策略找到 {len(all_links)} 个文章链接")

            seen_ids = set()

            for link in all_links:
                if len(articles) >= max_count:
                    break

                try:
                    href = link.get('href', '')
                    if not href:
                        continue

                    # 提取文章ID
                    article_id_match = re.search(r'/article/(\d+)/', href)
                    if not article_id_match:
                        continue

                    article_id = article_id_match.group(1)

                    # 避免重复
                    if article_id in seen_ids:
                        continue
                    seen_ids.add(article_id)

                    # 提取标题
                    title = link.get('title', '').strip()
                    if not title:
                        title = link.get('aria-label', '').strip()
                    if not title:
                        title = link.get_text(strip=True)

                    # 过滤无效标题
                    if not title or len(title) < 5 or title in ['更多', '查看更多', '详情']:
                        continue

                    # 构建完整URL
                    article_url = urljoin('https://www.toutiao.com', href)

                    article = {
                        'article_id': article_id,
                        'title': title,
                        'url': article_url,
                        'author': '',
                        'summary': '',
                        'publish_time': '',
                        'read_count': 0,
                        'comment_count': 0
                    }

                    articles.append(article)
                    logging.debug(f"备用策略解析文章: {title[:50]}... (ID:{article_id})")

                except Exception as e:
                    logging.warning(f"备用策略解析单个文章失败: {e}")
                    continue

        except Exception as e:
            logging.error(f"备用解析策略失败: {e}")
    
    def get_article_details(self, article_id: str) -> Dict:
        """
        获取文章详细信息，包括发布时间
        
        Args:
            article_id: 文章ID
            
        Returns:
            Dict: 文章详细信息
        """
        try:
            article_url = f"https://www.toutiao.com/article/{article_id}/"
            
            logging.info(f"获取文章详情: {article_url}")
            
            # 使用Selenium访问文章页面
            self.driver.get(article_url)
            
            # 等待页面加载
            time.sleep(random.uniform(2, 4))
            
            # 获取页面源码
            html_content = self.driver.page_source
            
            return self._parse_article_details(html_content, article_id)
                
        except Exception as e:
            logging.error(f"获取文章详情失败: {e}")
            return {}
    
    def _parse_article_details(self, html_content: str, article_id: str) -> Dict:
        """
        解析文章详细信息

        Args:
            html_content: HTML内容
            article_id: 文章ID

        Returns:
            Dict: 文章详细信息
        """
        details = {
            'article_id': article_id,
            'publish_time': '',
            'author': '',
            'summary': ''
        }

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # 方法1: 优先从JSON-LD结构化数据中提取信息
            # 基于实际HTML结构: <script type="application/ld+json">{"@context":"https://schema.org","@type":"NewsArticle",...}</script>
            json_ld_script = soup.find('script', type='application/ld+json')
            if json_ld_script and json_ld_script.string:
                try:
                    json_data = json.loads(json_ld_script.string)

                    # 提取发布时间: "datePublished":"2025-07-09T11:39:17+08:00"
                    if 'datePublished' in json_data:
                        details['publish_time'] = json_data['datePublished']
                        logging.debug(f"从JSON-LD提取发布时间: {details['publish_time']}")

                    # 提取作者: "author":{"@type":"Person","name":"纯侃体育"}
                    if 'author' in json_data and isinstance(json_data['author'], dict):
                        details['author'] = json_data['author'].get('name', '')
                        logging.debug(f"从JSON-LD提取作者: {details['author']}")

                    # 提取摘要: "description":"北京时间7月9日上午，乒乓球WTT美国大满贯继续进行..."
                    if 'description' in json_data:
                        details['summary'] = json_data['description']
                        logging.debug(f"从JSON-LD提取摘要: {details['summary'][:50]}...")

                except Exception as e:
                    logging.debug(f"解析JSON-LD失败: {e}")

            # 方法2: 如果JSON-LD没有提取到信息，尝试从RENDER_DATA中提取
            # 基于实际HTML结构: <script id="RENDER_DATA" type="application/json">%7B%22data%22%3A%7B...</script>
            if not details['publish_time'] or not details['author']:
                render_data_match = re.search(r'<script id="RENDER_DATA" type="application/json">([^<]+)</script>', html_content)
                if render_data_match:
                    try:
                        # URL解码JSON数据
                        json_str = unquote(render_data_match.group(1))
                        data = json.loads(json_str)

                        # 提取文章信息
                        if 'data' in data:
                            article_data = data['data']

                            # 提取发布时间: "publishTime":"2025-07-09 11:39"
                            if not details['publish_time'] and 'publishTime' in article_data:
                                details['publish_time'] = article_data['publishTime']
                                logging.debug(f"从RENDER_DATA提取发布时间: {details['publish_time']}")

                            # 提取作者: "source":"纯侃体育"
                            if not details['author'] and 'source' in article_data:
                                details['author'] = article_data['source']
                                logging.debug(f"从RENDER_DATA提取作者: {details['author']}")

                            # 提取摘要: "abstract":"北京时间7月9日上午，乒乓球WTT美国大满贯继续进行..."
                            if not details['summary'] and 'abstract' in article_data:
                                details['summary'] = article_data['abstract']
                                logging.debug(f"从RENDER_DATA提取摘要: {details['summary'][:50]}...")

                    except Exception as e:
                        logging.warning(f"解析RENDER_DATA失败: {e}")

            # 方法3: 如果仍然没有提取到发布时间，尝试从其他脚本中搜索
            if not details['publish_time']:
                # 搜索所有脚本中的时间信息
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and len(script.string) > 50:  # 只处理有内容的脚本
                        script_content = script.string

                        # 查找可能的时间格式，按优先级排序
                        time_patterns = [
                            (r'"datePublished":"([^"]+)"', 'datePublished'),
                            (r'"publishTime":"([^"]+)"', 'publishTime'),
                            (r'"publish_time":"([^"]+)"', 'publish_time'),
                            (r'"time":"([^"]+)"', 'time'),
                            (r'"created_at":"([^"]+)"', 'created_at'),
                            (r'"date":"([^"]+)"', 'date')
                        ]

                        for pattern, source in time_patterns:
                            match = re.search(pattern, script_content)
                            if match:
                                time_value = match.group(1)
                                # 验证时间格式是否合理
                                if self._is_valid_time_format(time_value):
                                    details['publish_time'] = time_value
                                    logging.debug(f"从脚本中提取发布时间({source}): {details['publish_time']}")
                                    break

                        if details['publish_time']:
                            break

            # 方法4: 如果仍然没有提取到作者，尝试从HTML元素中提取
            if not details['author']:
                author_selectors = [
                    'meta[name="author"]',
                    'meta[property="article:author"]',
                    '.article-author',
                    '.author-name',
                    '[data-author]',
                    '.byline-author',
                    '.source'
                ]

                for selector in author_selectors:
                    author_elem = soup.select_one(selector)
                    if author_elem:
                        if author_elem.name == 'meta':
                            author_text = author_elem.get('content', '').strip()
                        else:
                            author_text = author_elem.get_text(strip=True)

                        # 验证作者名称是否合理
                        if author_text and 2 <= len(author_text) <= 50 and not author_text.isdigit():
                            details['author'] = author_text
                            logging.debug(f"从HTML元素提取作者: {details['author']}")
                            break

            # 如果仍然没有提取到摘要，尝试从meta标签中提取
            if not details['summary']:
                summary_selectors = [
                    'meta[name="description"]',
                    'meta[property="og:description"]',
                    '.article-summary',
                    '.article-abstract'
                ]

                for selector in summary_selectors:
                    summary_elem = soup.select_one(selector)
                    if summary_elem:
                        if summary_elem.name == 'meta':
                            details['summary'] = summary_elem.get('content', '')
                        else:
                            details['summary'] = summary_elem.get_text(strip=True)

                        if details['summary']:
                            logging.debug(f"从HTML元素提取摘要: {details['summary'][:50]}...")
                            break

            # 格式化发布时间
            if details['publish_time']:
                details['publish_time'] = self._format_publish_time(details['publish_time'])

            logging.info(f"文章详情提取完成 - ID: {article_id}, 作者: {details['author']}, 时间: {details['publish_time']}")

        except Exception as e:
            logging.error(f"解析文章详情失败: {e}")

        return details

    def _format_publish_time(self, time_str: str) -> str:
        """
        格式化发布时间

        Args:
            time_str: 原始时间字符串

        Returns:
            str: 格式化后的时间字符串
        """
        try:
            # 处理ISO格式时间 (如: 2025-07-09T11:39:17+08:00)
            if 'T' in time_str and ('+' in time_str or 'Z' in time_str):
                from datetime import datetime
                # 移除时区信息进行解析
                clean_time = time_str.split('+')[0].split('Z')[0]
                dt = datetime.fromisoformat(clean_time)
                return dt.strftime('%Y-%m-%d %H:%M:%S')

            # 处理其他格式
            if '年' in time_str and '月' in time_str and '日' in time_str:
                # 中文日期格式
                return time_str

            # 处理相对时间
            if '小时前' in time_str or '分钟前' in time_str or '天前' in time_str:
                return time_str

            return time_str

        except Exception as e:
            logging.debug(f"时间格式化失败: {e}")
            return time_str

    def _is_valid_time_format(self, time_str: str) -> bool:
        """
        验证时间格式是否合理

        Args:
            time_str: 时间字符串

        Returns:
            bool: 是否为有效时间格式
        """
        if not time_str or len(time_str) < 8:
            return False

        # 检查常见的时间格式
        time_patterns = [
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO格式
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # 标准格式
            r'\d{4}年\d{1,2}月\d{1,2}日',  # 中文日期
            r'\d{1,2}小时前',  # 相对时间
            r'\d{1,2}分钟前',
            r'\d{1,2}天前',
            r'前天\d{2}:\d{2}',
            r'昨天\d{2}:\d{2}'
        ]

        for pattern in time_patterns:
            if re.search(pattern, time_str):
                return True

        return False
    
    def get_latest_articles(self, blogger_url: str, limit: int = 10) -> List[Dict]:
        """
        获取最新的文章列表，包含详细信息

        Args:
            blogger_url: 博主URL链接
            limit: 获取文章数量限制

        Returns:
            List[Dict]: 最新文章列表
        """
        try:
            # 先获取文章列表
            articles = self.get_articles_from_url(blogger_url, limit)

            if not articles:
                logging.warning("未获取到任何文章")
                return []

            logging.info(f"获取到 {len(articles)} 篇文章，开始获取详细信息...")

            # 为每篇文章获取详细信息
            for i, article in enumerate(articles):
                if article.get('article_id'):
                    try:
                        logging.info(f"正在获取第 {i+1}/{len(articles)} 篇文章详情: {article['title'][:30]}...")
                        details = self.get_article_details(article['article_id'])
                        if details:
                            # 更新文章信息
                            if details.get('publish_time'):
                                article['publish_time'] = details['publish_time']
                            if details.get('author'):
                                article['author'] = details['author']
                            if details.get('summary'):
                                article['summary'] = details['summary']

                        # 添加延迟避免请求过快
                        time.sleep(random.uniform(1, 3))

                    except Exception as e:
                        logging.warning(f"获取文章详情失败 {article.get('article_id')}: {e}")
                        continue

            # 按发布时间排序（最新的在前）
            articles_with_time = [a for a in articles if a.get('publish_time')]
            articles_without_time = [a for a in articles if not a.get('publish_time')]

            # 对有时间的文章排序
            articles_with_time.sort(key=lambda x: x.get('publish_time', ''), reverse=True)

            # 合并结果，有时间的在前
            sorted_articles = articles_with_time + articles_without_time

            logging.info(f"成功获取 {len(sorted_articles)} 篇文章，其中 {len(articles_with_time)} 篇有发布时间")

            return sorted_articles

        except Exception as e:
            logging.error(f"获取最新文章失败: {e}")
            return []

    def check_new_articles(self, blogger_url: str, last_article_ids: List[str], limit: int = 10) -> List[Dict]:
        """
        检查是否有新文章

        Args:
            blogger_url: 博主URL链接
            last_article_ids: 上次检查的文章ID列表
            limit: 检查文章数量限制

        Returns:
            List[Dict]: 新文章列表
        """
        try:
            # 获取最新文章列表
            latest_articles = self.get_latest_articles(blogger_url, limit)

            # 筛选出新文章
            new_articles = []
            for article in latest_articles:
                if article.get('article_id') not in last_article_ids:
                    new_articles.append(article)

            logging.info(f"检查到 {len(new_articles)} 篇新文章")

            return new_articles

        except Exception as e:
            logging.error(f"检查新文章失败: {e}")
            return []
    
    def test_user_access(self, blogger_url: str) -> bool:
        """
        测试博主URL访问是否正常

        Args:
            blogger_url: 博主URL链接

        Returns:
            bool: 访问正常返回True
        """
        try:
            articles = self.get_articles_from_url(blogger_url, 1)
            return len(articles) > 0
        except:
            return False

    def test_extraction(self, blogger_url: str) -> Dict:
        """
        测试信息提取功能

        Args:
            blogger_url: 博主URL链接

        Returns:
            Dict: 测试结果
        """
        test_result = {
            'success': False,
            'articles_found': 0,
            'articles_with_details': 0,
            'sample_article': None,
            'errors': []
        }

        try:
            logging.info("开始测试信息提取功能...")

            # 测试文章列表提取
            articles = self.get_articles_from_url(blogger_url, 3)  # 只测试3篇文章
            test_result['articles_found'] = len(articles)

            if articles:
                logging.info(f"成功提取 {len(articles)} 篇文章")

                # 测试第一篇文章的详细信息提取
                first_article = articles[0]
                if first_article.get('article_id'):
                    details = self.get_article_details(first_article['article_id'])
                    if details and details.get('publish_time'):
                        test_result['articles_with_details'] = 1
                        test_result['sample_article'] = {
                            'article_id': first_article['article_id'],
                            'title': first_article['title'],
                            'url': first_article['url'],
                            'publish_time': details['publish_time'],
                            'author': details['author'],
                            'summary': details['summary'][:100] if details['summary'] else '',
                            'read_count': first_article.get('read_count', 0),
                            'comment_count': first_article.get('comment_count', 0)
                        }
                        logging.info(f"成功提取文章详情: {first_article['title'][:30]}...")
                        test_result['success'] = True
                    else:
                        test_result['errors'].append("无法提取文章详细信息")
                else:
                    test_result['errors'].append("文章ID提取失败")
            else:
                test_result['errors'].append("未找到任何文章")

        except Exception as e:
            test_result['errors'].append(f"测试过程中出错: {str(e)}")
            logging.error(f"测试失败: {e}")

        return test_result

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logging.info("浏览器已关闭")


# 为了保持兼容性，提供别名
ToutiaoCrawler = ToutiaoSeleniumCrawler
