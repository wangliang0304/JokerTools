# 头条文章监控系统完整指南

## 系统架构

本系统基于 README.md 的设计，使用优化后的 `ToutiaoSeleniumCrawler` 爬虫类，实现了完整的头条文章监控流程。

### 核心组件

1. **ToutiaoSeleniumCrawler** - 优化后的Selenium爬虫
   - 基于实际HTML结构的精确解析
   - 支持文章ID、标题、作者、发布时间、阅读数、评论数、摘要提取
   - 多层级数据提取策略（JSON-LD → RENDER_DATA → 脚本搜索 → HTML元素）

2. **ArticleDatabase** - 数据库管理
   - SQLite数据库存储
   - 支持新字段（read_count, comment_count）
   - 自动数据库结构升级

3. **FeishuNotifier** - 飞书通知
   - 富文本消息格式
   - 包含完整文章信息（标题、作者、时间、统计数据、摘要、链接）
   - 支持签名验证

4. **ArticleMonitor** - 监控服务
   - 定时任务调度
   - 新文章检测
   - 自动通知发送

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository_url>
cd JokerTools

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置系统

编辑 `config.json` 文件：

```json
{
  "toutiao": {
    "blogger_url": "https://www.toutiao.com/c/user/token/MS4wLjABAAAAu8TLqbwurnpNAkvSb1SB60loMjrybIwxT3py56-uKRM/",
    "check_interval_minutes": 30
  },
  "feishu": {
    "webhook_url": "你的飞书机器人Webhook URL",
    "secret": "你的飞书机器人密钥（可选）"
  },
  "database": {
    "path": "articles.db"
  },
  "logging": {
    "level": "INFO",
    "file": "monitor.log"
  }
}
```

### 3. 系统测试

```bash
# 方式1: 使用启动脚本（推荐）
python run_system.py

# 方式2: 直接测试
python test_complete_system.py

# 方式3: 测试单个组件
python test_selenium_crawler.py
```

### 4. 启动监控

```bash
# 方式1: 使用main.py
python main.py start

# 方式2: 使用启动脚本
python run_system.py
# 然后选择选项6
```

## 系统特性

### 优化后的数据提取

- **文章列表解析**: 基于 `profile-article-card-wrapper` 容器的精确解析
- **文章详情解析**: 多源数据提取策略，确保信息完整性
- **数据验证**: 时间格式验证、作者信息验证等
- **错误处理**: 完善的异常处理和日志记录

### 提取的文章信息

```python
{
    'article_id': '7524937913248006694',
    'title': 'WTT美国大满贯9日战报：混双8强出炉！栋曼横扫晋级；国乒6战全胜',
    'url': 'https://www.toutiao.com/article/7524937913248006694/',
    'author': '纯侃体育',
    'publish_time': '2025-07-09 11:39:17',
    'summary': '北京时间7月9日上午，乒乓球WTT美国大满贯继续进行...',
    'read_count': 59000,
    'comment_count': 33
}
```

### 飞书通知格式

系统会发送包含以下信息的富文本消息：
- 📰 新文章标题
- 👤 作者信息
- ⏰ 发布时间
- 📊 统计数据（阅读数、评论数）
- 📝 文章摘要
- 🔗 原文链接

## 命令行工具

### main.py 命令

```bash
# 启动监控服务
python main.py start

# 测试系统组件
python main.py test

# 查看监控状态
python main.py status

# 手动执行一次检查
python main.py check

# 使用指定配置文件
python main.py start --config my_config.json
```

### 测试脚本

```bash
# 完整系统测试
python test_complete_system.py

# Selenium爬虫测试
python test_selenium_crawler.py

# 解析优化测试
python toutiao/test_parsing_optimization.py
```

## 部署建议

### 开发环境

```bash
# 直接启动
python main.py start

# 或使用启动脚本
python run_system.py
```

### 生产环境

#### 使用systemd (Linux)

创建服务文件 `/etc/systemd/system/toutiao-monitor.service`：

```ini
[Unit]
Description=Toutiao Article Monitor
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/JokerTools
ExecStart=/usr/bin/python3 main.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable toutiao-monitor
sudo systemctl start toutiao-monitor
```

#### 使用Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# 安装Chrome和ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

COPY . .
CMD ["python", "main.py", "start"]
```

## 故障排除

### 常见问题

1. **Selenium相关错误**
   - 确保安装了Chrome浏览器
   - 检查ChromeDriver版本兼容性
   - 尝试更新webdriver-manager

2. **文章获取失败**
   - 检查网络连接
   - 验证博主URL是否正确
   - 查看日志文件中的详细错误信息

3. **飞书通知失败**
   - 验证Webhook URL是否正确
   - 检查网络连接
   - 确认机器人权限设置

4. **数据库错误**
   - 检查文件权限
   - 确认磁盘空间充足
   - 查看数据库文件是否损坏

### 日志查看

```bash
# 查看实时日志
tail -f monitor.log

# 查看系统测试日志
tail -f system_test.log

# 查看解析测试日志
tail -f toutiao/parsing_test.log
```

### 调试模式

将配置文件中的日志级别设置为 `DEBUG`：

```json
{
  "logging": {
    "level": "DEBUG",
    "file": "monitor.log"
  }
}
```

## 性能优化

### 监控间隔

- 建议设置不少于30分钟的检查间隔
- 避免对头条服务器造成过大压力

### 资源使用

- 监控内存使用情况
- 定期清理日志文件
- 考虑使用无头模式运行Chrome

### 网络优化

- 使用稳定的网络连接
- 考虑配置代理（如需要）
- 设置合理的请求超时时间

## 扩展功能

### 多博主监控

可以扩展系统支持多个博主的监控：

```python
# 在配置文件中添加多个博主
"toutiao": {
    "bloggers": [
        {
            "name": "博主1",
            "url": "https://www.toutiao.com/c/user/token/TOKEN1/"
        },
        {
            "name": "博主2", 
            "url": "https://www.toutiao.com/c/user/token/TOKEN2/"
        }
    ],
    "check_interval_minutes": 30
}
```

### 自定义通知

可以扩展通知功能支持其他平台：

- 微信机器人
- 钉钉机器人
- 邮件通知
- 短信通知

### 数据分析

可以基于收集的数据进行分析：

- 文章发布时间分析
- 阅读数趋势分析
- 热门话题识别
- 作者活跃度统计

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！
