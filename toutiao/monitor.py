"""
文章监控服务模块
协调爬虫、数据库和通知功能
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

try:
    from .crawler_selenium import ToutiaoSeleniumCrawler

    SELENIUM_AVAILABLE = True
    logging.info("使用优化后的Selenium爬虫")
except ImportError:
    pass
from .database import ArticleDatabase
from .feishu_notifier import FeishuNotifier


class ArticleMonitor:
    """文章监控服务类"""

    def __init__(self, config_path: str = "config.json"):
        """
        初始化监控服务
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.setup_logging()

        # 初始化各个组件
        self.crawler = ToutiaoSeleniumCrawler()
        self.database = ArticleDatabase(self.config['database']['path'])
        self.notifier = FeishuNotifier(
            self.config['feishu']['webhook_url'],
            self.config['feishu'].get('secret')
        )

        # 获取博主URL
        self.blogger_url = self.config['toutiao']['blogger_url']
        if not self.blogger_url:
            raise ValueError("请在配置中设置博主URL")

        logging.info(f"监控服务初始化完成，博主URL: {self.blogger_url}")

    def _load_config(self, config_path: str) -> Dict:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Dict: 配置字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            logging.error(f"加载配置文件失败: {e}")
            raise

    def setup_logging(self):
        """设置日志配置"""
        log_level = getattr(logging, self.config['logging']['level'].upper())
        log_file = self.config['logging']['file']

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

    def check_new_articles(self) -> List[Dict]:
        """
        检查新文章

        Returns:
            List[Dict]: 新文章列表
        """
        try:
            logging.info("开始检查新文章...")

            # 获取最新文章
            latest_articles = self.crawler.get_latest_articles(self.blogger_url, limit=10)

            if not latest_articles:
                logging.warning("未获取到任何文章")
                return []

            new_articles = []

            # 检查每篇文章是否为新文章
            for article in latest_articles:
                if not self.database.article_exists(article['article_id']):
                    # 添加到数据库
                    if self.database.add_article(article):
                        new_articles.append(article)
                        logging.info(f"发现新文章: {article['title']}")

            if new_articles:
                logging.info(f"共发现 {len(new_articles)} 篇新文章")
            else:
                logging.info("没有发现新文章")

            return new_articles

        except Exception as e:
            logging.error(f"检查新文章失败: {e}")
            return []

    def send_notifications(self, articles: List[Dict]) -> int:
        """
        发送文章通知
        
        Args:
            articles: 文章列表
            
        Returns:
            int: 成功发送的通知数量
        """
        success_count = 0

        for article in articles:
            try:
                if self.notifier.send_article_notification(article):
                    # 标记为已通知
                    self.database.mark_as_notified(article['article_id'])
                    success_count += 1
                    logging.info(f"文章通知发送成功: {article['title']}")

                    # 发送间隔，避免频繁请求
                    time.sleep(1)
                else:
                    logging.error(f"文章通知发送失败: {article['title']}")

            except Exception as e:
                logging.error(f"发送文章通知异常: {e}")

        return success_count

    def run_check_cycle(self):
        """运行一次检查周期"""
        try:
            start_time = datetime.now()
            logging.info(f"开始执行检查周期: {start_time}")

            # 检查新文章
            new_articles = self.check_new_articles()

            # 发送通知
            if new_articles:
                success_count = self.send_notifications(new_articles)
                logging.info(f"通知发送完成，成功: {success_count}/{len(new_articles)}")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logging.info(f"检查周期完成，耗时: {duration:.2f}秒")

        except Exception as e:
            logging.error(f"检查周期执行失败: {e}")

    def test_system(self, send_test_notification: bool = True) -> bool:
        """
        测试系统各组件

        Args:
            send_test_notification: 是否发送测试通知

        Returns:
            bool: 测试通过返回True
        """
        try:
            logging.info("开始系统测试...")

            # 测试爬虫
            logging.info("测试爬虫组件...")
            if not self.crawler.test_user_access(self.blogger_url):
                logging.error("爬虫测试失败")
                return False
            logging.info("爬虫测试通过")

            # 测试数据库
            logging.info("测试数据库组件...")
            test_article = {
                'article_id': 'test_' + str(int(time.time())),
                'title': '测试文章',
                'url': 'https://test.com',
                'author': '测试作者',
                'summary': '测试摘要'
            }
            if not self.database.add_article(test_article):
                logging.error("数据库测试失败")
                return False
            logging.info("数据库测试通过")

            # 测试飞书通知（可选）
            if send_test_notification:
                logging.info("测试飞书通知组件...")
                if not self.notifier.test_connection():
                    logging.error("飞书通知测试失败")
                    return False
                logging.info("飞书通知测试通过")
            else:
                logging.info("跳过飞书通知测试")

            logging.info("系统测试全部通过")
            return True

        except Exception as e:
            logging.error(f"系统测试失败: {e}")
            return False

    def test_system_with_notification(self) -> bool:
        """
        完整测试系统各组件（包括发送测试通知）

        Returns:
            bool: 测试通过返回True
        """
        return self.test_system(send_test_notification=True)

    def start_monitoring(self):
        """启动监控服务"""
        try:
            logging.info("启动文章监控服务...")

            # 系统测试（不发送测试通知）
            if not self.test_system(send_test_notification=False):
                logging.error("系统测试失败，无法启动监控服务")
                return

            # 创建调度器
            scheduler = BlockingScheduler()

            # 添加定时任务
            interval_minutes = self.config['toutiao']['check_interval_minutes']
            scheduler.add_job(
                func=self.run_check_cycle,
                trigger=IntervalTrigger(minutes=interval_minutes),
                id='article_check',
                name='文章检查任务',
                replace_existing=True
            )

            logging.info(f"监控服务已启动，检查间隔: {interval_minutes}分钟")

            # 立即执行一次检查
            self.run_check_cycle()

            # 启动调度器
            scheduler.start()

        except KeyboardInterrupt:
            logging.info("收到停止信号，正在关闭监控服务...")
        except Exception as e:
            logging.error(f"监控服务启动失败: {e}")

    def get_status(self) -> Dict:
        """
        获取监控状态
        
        Returns:
            Dict: 状态信息
        """
        try:
            latest_articles = self.database.get_latest_articles(5)
            unnotified_count = len(self.database.get_unnotified_articles())

            return {
                'blogger_url': self.blogger_url,
                'latest_articles_count': len(latest_articles),
                'unnotified_count': unnotified_count,
                'latest_articles': latest_articles,
                'last_check_time': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"获取状态失败: {e}")
            return {}


if __name__ == '__main__':
    ArticleMonitor().run_check_cycle()