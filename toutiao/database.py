"""
数据库管理模块
用于存储和管理已监控的文章信息
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional


class ArticleDatabase:
    """文章数据库管理类"""
    
    def __init__(self, db_path: str):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 创建文章表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        article_id TEXT UNIQUE NOT NULL,
                        title TEXT NOT NULL,
                        url TEXT NOT NULL,
                        publish_time TEXT,
                        author TEXT,
                        summary TEXT,
                        read_count INTEGER DEFAULT 0,
                        comment_count INTEGER DEFAULT 0,
                        created_at TEXT NOT NULL,
                        notified BOOLEAN DEFAULT FALSE
                    )
                ''')

                # 检查并添加新字段（兼容旧数据库）
                self._upgrade_database_schema(cursor)

                conn.commit()
                logging.info("数据库初始化完成")
        except Exception as e:
            logging.error(f"数据库初始化失败: {e}")
            raise

    def _upgrade_database_schema(self, cursor):
        """升级数据库结构，添加新字段"""
        try:
            # 检查是否存在read_count字段
            cursor.execute("PRAGMA table_info(articles)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'read_count' not in columns:
                cursor.execute('ALTER TABLE articles ADD COLUMN read_count INTEGER DEFAULT 0')
                logging.info("添加read_count字段")

            if 'comment_count' not in columns:
                cursor.execute('ALTER TABLE articles ADD COLUMN comment_count INTEGER DEFAULT 0')
                logging.info("添加comment_count字段")

        except Exception as e:
            logging.debug(f"数据库结构升级: {e}")  # 不是致命错误，只记录调试信息
    
    def add_article(self, article_data: Dict) -> bool:
        """
        添加新文章到数据库

        Args:
            article_data: 文章数据字典

        Returns:
            bool: 添加成功返回True，已存在返回False
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO articles
                    (article_id, title, url, publish_time, author, summary, read_count, comment_count, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article_data['article_id'],
                    article_data['title'],
                    article_data['url'],
                    article_data.get('publish_time', ''),
                    article_data.get('author', ''),
                    article_data.get('summary', ''),
                    article_data.get('read_count', 0),
                    article_data.get('comment_count', 0),
                    datetime.now().isoformat()
                ))

                if cursor.rowcount > 0:
                    conn.commit()
                    logging.info(f"新文章已添加到数据库: {article_data['title']} (阅读:{article_data.get('read_count', 0)}, 评论:{article_data.get('comment_count', 0)})")
                    return True
                else:
                    logging.debug(f"文章已存在: {article_data['title']}")
                    return False

        except Exception as e:
            logging.error(f"添加文章到数据库失败: {e}")
            return False
    
    def mark_as_notified(self, article_id: str) -> bool:
        """
        标记文章为已通知
        
        Args:
            article_id: 文章ID
            
        Returns:
            bool: 标记成功返回True
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE articles SET notified = TRUE WHERE article_id = ?',
                    (article_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"标记文章为已通知失败: {e}")
            return False
    
    def get_unnotified_articles(self) -> List[Dict]:
        """
        获取未通知的文章列表

        Returns:
            List[Dict]: 未通知的文章列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT article_id, title, url, publish_time, author, summary, read_count, comment_count
                    FROM articles
                    WHERE notified = FALSE
                    ORDER BY created_at DESC
                ''')

                columns = ['article_id', 'title', 'url', 'publish_time', 'author', 'summary', 'read_count', 'comment_count']
                articles = []
                for row in cursor.fetchall():
                    articles.append(dict(zip(columns, row)))

                return articles
        except Exception as e:
            logging.error(f"获取未通知文章失败: {e}")
            return []
    
    def get_latest_articles(self, limit: int = 10) -> List[Dict]:
        """
        获取最新的文章列表

        Args:
            limit: 返回文章数量限制

        Returns:
            List[Dict]: 最新文章列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT article_id, title, url, publish_time, author, summary, read_count, comment_count, notified
                    FROM articles
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (limit,))

                columns = ['article_id', 'title', 'url', 'publish_time', 'author', 'summary', 'read_count', 'comment_count', 'notified']
                articles = []
                for row in cursor.fetchall():
                    articles.append(dict(zip(columns, row)))

                return articles
        except Exception as e:
            logging.error(f"获取最新文章失败: {e}")
            return []
    
    def article_exists(self, article_id: str) -> bool:
        """
        检查文章是否已存在
        
        Args:
            article_id: 文章ID
            
        Returns:
            bool: 存在返回True
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT 1 FROM articles WHERE article_id = ?',
                    (article_id,)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logging.error(f"检查文章是否存在失败: {e}")
            return False

if __name__ == '__main__':
    ArticleDatabase(db_path="articles.db")