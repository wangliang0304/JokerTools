"""
飞书通知模块
用于向飞书群组发送新文章通知
"""

import json
import time
import hmac
import hashlib
import base64
import requests
import logging
from typing import Dict, List


class FeishuNotifier:
    """飞书通知器类"""
    
    def __init__(self, webhook_url: str, secret: str = None):
        """
        初始化飞书通知器
        
        Args:
            webhook_url: 飞书机器人Webhook URL
            secret: 飞书机器人密钥（可选）
        """
        self.webhook_url = webhook_url
        self.secret = secret
    
    def _generate_sign(self, timestamp: str) -> str:
        """
        生成飞书机器人签名
        
        Args:
            timestamp: 时间戳
            
        Returns:
            str: 签名字符串
        """
        if not self.secret:
            return ""
        
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign
    
    def send_text_message(self, content: str) -> bool:
        """
        发送文本消息
        
        Args:
            content: 消息内容
            
        Returns:
            bool: 发送成功返回True
        """
        timestamp = str(int(time.time()))
        
        data = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
        
        # 如果有密钥，添加签名
        if self.secret:
            sign = self._generate_sign(timestamp)
            data["timestamp"] = timestamp
            data["sign"] = sign
        
        return self._send_message(data)
    
    def send_rich_text_message(self, title: str, content: List[List[Dict]]) -> bool:
        """
        发送富文本消息
        
        Args:
            title: 消息标题
            content: 富文本内容
            
        Returns:
            bool: 发送成功返回True
        """
        timestamp = str(int(time.time()))
        
        data = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": content
                    }
                }
            }
        }
        
        # 如果有密钥，添加签名
        if self.secret:
            sign = self._generate_sign(timestamp)
            data["timestamp"] = timestamp
            data["sign"] = sign
        
        return self._send_message(data)
    
    def send_article_notification(self, article: Dict) -> bool:
        """
        发送文章通知
        
        Args:
            article: 文章信息字典
            
        Returns:
            bool: 发送成功返回True
        """
        try:
            # 构建富文本消息内容
            content = [
                [
                    {
                        "tag": "text",
                        "text": "📰 发现新文章！\n\n"
                    }
                ],
                [
                    {
                        "tag": "text",
                        "text": "标题：",
                        "style": ["bold"]
                    },
                    {
                        "tag": "text",
                        "text": article.get('title', '未知标题')
                    }
                ],
                [
                    {
                        "tag": "text",
                        "text": "作者：",
                        "style": ["bold"]
                    },
                    {
                        "tag": "text",
                        "text": article.get('author', '未知作者')
                    }
                ]
            ]
            
            # 添加发布时间（如果有）
            if article.get('publish_time'):
                content.append([
                    {
                        "tag": "text",
                        "text": "⏰ 发布时间：",
                        "style": ["bold"]
                    },
                    {
                        "tag": "text",
                        "text": article['publish_time']
                    }
                ])

            # 添加统计信息（阅读数、评论数）
            stats_parts = []
            if article.get('read_count', 0) > 0:
                read_count = article['read_count']
                if read_count >= 10000:
                    read_text = f"{read_count/10000:.1f}万"
                else:
                    read_text = str(read_count)
                stats_parts.append(f"👀 {read_text}阅读")

            if article.get('comment_count', 0) > 0:
                stats_parts.append(f"💬 {article['comment_count']}评论")

            if stats_parts:
                content.append([
                    {
                        "tag": "text",
                        "text": "📊 数据：",
                        "style": ["bold"]
                    },
                    {
                        "tag": "text",
                        "text": " | ".join(stats_parts)
                    }
                ])

            # 添加摘要（如果有）
            if article.get('summary'):
                summary_text = article['summary']
                if len(summary_text) > 200:
                    summary_text = summary_text[:200] + "..."

                content.append([
                    {
                        "tag": "text",
                        "text": "📝 摘要：",
                        "style": ["bold"]
                    },
                    {
                        "tag": "text",
                        "text": summary_text
                    }
                ])
            
            # 添加链接
            content.append([
                {
                    "tag": "text",
                    "text": "链接：",
                    "style": ["bold"]
                },
                {
                    "tag": "a",
                    "text": "点击查看原文",
                    "href": article.get('url', '')
                }
            ])
            
            return self.send_rich_text_message("头条博主新文章通知", content)
            
        except Exception as e:
            logging.error(f"发送文章通知失败: {e}")
            # 如果富文本发送失败，尝试发送简单文本
            stats_info = ""
            if article.get('read_count', 0) > 0 or article.get('comment_count', 0) > 0:
                read_count = article.get('read_count', 0)
                comment_count = article.get('comment_count', 0)
                read_text = f"{read_count/10000:.1f}万" if read_count >= 10000 else str(read_count)
                stats_info = f"\n数据：👀 {read_text}阅读 | 💬 {comment_count}评论"

            simple_message = f"""📰 发现新文章！

标题：{article.get('title', '未知标题')}
作者：{article.get('author', '未知作者')}
发布时间：{article.get('publish_time', '未知')}{stats_info}
链接：{article.get('url', '')}"""

            return self.send_text_message(simple_message)
    
    def _send_message(self, data: Dict) -> bool:
        """
        发送消息到飞书
        
        Args:
            data: 消息数据
            
        Returns:
            bool: 发送成功返回True
        """
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.webhook_url,
                headers=headers,
                data=json.dumps(data),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('StatusCode') == 0:
                    logging.info("飞书消息发送成功")
                    return True
                else:
                    logging.error(f"飞书消息发送失败: {result}")
                    return False
            else:
                logging.error(f"飞书API请求失败: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"发送飞书消息异常: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        测试飞书连接
        
        Returns:
            bool: 连接成功返回True
        """
        test_message = "🤖 头条文章监控系统测试消息"
        return self.send_text_message(test_message)
