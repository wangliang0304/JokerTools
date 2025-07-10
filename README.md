# 头条文章监控系统

一个用于监控今日头条博主最新文章并通过飞书机器人发送通知的自动化系统。

## 功能特性

- 🔍 **自动监控**: 定时爬取指定博主的最新文章
- 📱 **实时通知**: 发现新文章时立即通过飞书机器人发送通知
- 💾 **数据持久化**: 使用SQLite数据库存储文章信息，避免重复通知
- ⚙️ **灵活配置**: 支持自定义监控间隔、飞书机器人等配置
- 🛡️ **反爬虫处理**: 基于HTML页面解析，绕过API限制，内置随机延迟和User-Agent轮换
- 📊 **状态监控**: 提供系统状态查看和测试功能
- 🕒 **精确时间**: 自动获取文章的准确发布时间

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置系统

复制并编辑配置文件：

```bash
cp config.json config.json.bak
```

编辑 `config.json` 文件：

```json
{
  "toutiao": {
    "blogger_url": "你要监控的博主文章链接",
    "user_id": "博主用户ID（可自动提取）",
    "check_interval_minutes": 30
  },
  "feishu": {
    "webhook_url": "你的飞书机器人Webhook URL",
    "secret": "飞书机器人密钥（可选）"
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

### 3. 设置飞书机器人

1. 在飞书群组中添加自定义机器人
2. 复制机器人的Webhook URL
3. 将URL填入配置文件的 `feishu.webhook_url` 字段

### 4. 测试爬虫策略

```bash
# 测试新的爬虫策略
python test_selenium_crawler.py
```

### 5. 测试系统

```bash
python main.py test
```

### 6. 启动监控

```bash
python main.py start
```

## 使用说明

### 命令行工具

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

### 获取博主用户ID

系统支持从头条文章链接自动提取用户ID，你只需要：

1. 找到博主的任意一篇文章链接
2. 将链接填入配置文件的 `blogger_url` 字段
3. 系统会自动提取用户ID

### 飞书通知格式

系统会发送包含以下信息的富文本消息：

- 📰 新文章标题
- 👤 作者信息
- ⏰ 发布时间
- 📝 文章摘要
- 🔗 原文链接

## 项目结构

```
JokerTools/
├── toutiao/                 # 核心模块
│   ├── __init__.py         # 模块初始化
│   ├── crawler.py          # 文章爬虫
│   ├── database.py         # 数据库管理
│   ├── feishu_notifier.py  # 飞书通知
│   └── monitor.py          # 监控服务
├── main.py                 # 主程序入口
├── config.json             # 配置文件
├── requirements.txt        # 依赖列表
└── README.md              # 说明文档
```

## 配置说明

### 头条配置 (toutiao)

- `blogger_url`: 博主文章链接（用于提取用户ID）
- `user_id`: 博主用户ID（可自动提取）
- `check_interval_minutes`: 检查间隔（分钟）

### 飞书配置 (feishu)

- `webhook_url`: 飞书机器人Webhook URL（必填）
- `secret`: 飞书机器人密钥（可选，用于签名验证）

### 数据库配置 (database)

- `path`: SQLite数据库文件路径

### 日志配置 (logging)

- `level`: 日志级别（DEBUG, INFO, WARNING, ERROR）
- `file`: 日志文件路径

## 部署建议

### 开发环境

直接使用命令行启动：

```bash
python main.py start
```

### 生产环境

建议使用系统服务或进程管理器：

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

#### 使用PM2 (Node.js环境)

```bash
pm2 start main.py --name toutiao-monitor --interpreter python3
pm2 save
pm2 startup
```

## 故障排除

### 常见问题

1. **无法获取文章**: 检查网络连接和用户ID是否正确
2. **飞书通知失败**: 验证Webhook URL和网络连接
3. **数据库错误**: 检查文件权限和磁盘空间

### 日志查看

系统会将日志输出到配置文件指定的日志文件中，可以通过以下命令查看：

```bash
tail -f monitor.log
```

### 调试模式

将配置文件中的日志级别设置为 `DEBUG` 可以获取更详细的日志信息。

## 注意事项

1. **合理设置检查间隔**: 建议不少于30分钟，避免对头条服务器造成压力
2. **网络稳定性**: 确保运行环境有稳定的网络连接
3. **权限管理**: 确保程序有读写数据库文件的权限
4. **资源监控**: 长期运行时注意监控内存和磁盘使用情况

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！
