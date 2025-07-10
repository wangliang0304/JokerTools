# 快速开始指南

## 🚀 5分钟快速部署

### 第一步：准备飞书机器人

1. 在飞书群组中点击 **群设置** → **群机器人** → **添加机器人** → **自定义机器人**
2. 设置机器人名称（如：头条监控助手）
3. 复制生成的 **Webhook URL**（以 `https://open.feishu.cn/open-apis/bot/v2/hook/` 开头）

### 第二步：获取博主链接

1. 打开今日头条，找到你要监控的博主
2. 访问博主的主页（格式如：`https://www.toutiao.com/c/user/token/用户ID/`）
3. 或者复制博主的任意一篇文章链接（包含完整的URL参数）

### 第三步：运行配置向导

**Windows用户：**
```cmd
# 双击运行 start.bat 文件
# 或在命令行中运行：
python setup_config.py
```

**Linux/Mac用户：**
```bash
# 给脚本执行权限
chmod +x start.sh

# 运行启动脚本
./start.sh

# 或直接运行配置向导
python3 setup_config.py
```

### 第四步：按向导提示配置

1. **输入博主文章链接**：粘贴第二步复制的链接
2. **设置检查间隔**：建议30-60分钟（避免频繁请求）
3. **输入飞书Webhook URL**：粘贴第一步复制的URL
4. **其他配置**：使用默认值即可

### 第五步：测试和启动

```bash
# 测试爬虫策略
python test_crawler.py

# 测试系统
python main.py test

# 启动监控
python main.py start
```

## 📱 配置示例

### config.json 示例
```json
{
  "toutiao": {
    "blogger_url": "https://www.toutiao.com/article/7524937913248006694/?share_uid=MS4wLjABAAAARU520WoPhwMRICwKKawo_wwxcgIZTEFPNotxYaoz33I",
    "user_id": "MS4wLjABAAAARU520WoPhwMRICwKKawo_wwxcgIZTEFPNotxYaoz33I",
    "check_interval_minutes": 30
  },
  "feishu": {
    "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx",
    "secret": ""
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

## 🔧 常用命令

```bash
# 启动监控服务
python main.py start

# 测试系统组件
python main.py test

# 查看监控状态
python main.py status

# 手动执行一次检查
python main.py check

# 运行配置向导
python setup_config.py

# 运行系统测试
python test_system.py
```

## 📊 通知效果

当发现新文章时，飞书机器人会发送如下格式的消息：

```
📰 发现新文章！

标题：文章标题
作者：博主名称
发布时间：2025-01-09 15:30:00
摘要：文章摘要内容...
链接：点击查看原文
```

## 🚨 常见问题

### 1. 无法获取文章
- 检查网络连接
- 确认用户ID是否正确
- 检查博主是否有新文章

### 2. 飞书通知失败
- 确认Webhook URL是否正确
- 检查机器人是否被移除
- 验证网络连接

### 3. 程序启动失败
- 检查Python版本（需要3.7+）
- 安装依赖：`pip install -r requirements.txt`
- 检查配置文件格式

## 🔄 后台运行

### Windows（使用任务计划程序）
1. 打开任务计划程序
2. 创建基本任务
3. 设置程序路径：`python.exe`
4. 设置参数：`main.py start`
5. 设置工作目录为项目目录

### Linux（使用systemd）
```bash
# 运行安装脚本
./setup_service.sh

# 启动服务
sudo systemctl start toutiao-monitor

# 查看状态
sudo systemctl status toutiao-monitor
```

## 📞 获取帮助

如果遇到问题：

1. 查看日志文件：`monitor.log`
2. 运行系统测试：`python test_system.py`
3. 检查配置文件：确保所有必填项都已正确配置

## 🎯 下一步

- 可以监控多个博主（修改代码支持多用户）
- 添加更多通知渠道（微信、钉钉等）
- 设置关键词过滤
- 添加文章内容分析功能
