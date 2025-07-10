# 头条爬虫策略说明

## 新策略概述

基于头条的反爬虫限制，我们采用了全新的爬虫策略，不再依赖API接口，而是直接解析HTML页面内容。

## 策略特点

### 1. 基于HTML页面解析
- 直接访问博主主页：`https://www.toutiao.com/c/user/token/{user_id}/`
- 解析页面中的文章链接和元数据
- 绕过API的反爬虫限制

### 2. 多层信息获取
- **第一层**：从主页获取文章列表（标题、ID、链接、基础统计）
- **第二层**：访问具体文章页面获取详细信息（发布时间、作者、摘要）

### 3. 智能解析机制
- 使用BeautifulSoup解析HTML结构
- 支持多种CSS选择器模式
- 自动处理不同的页面布局

### 4. 反爬虫对策
- 随机User-Agent轮换
- 随机延迟（2-5秒）
- 模拟真实浏览器请求头
- 重试机制

## 实现细节

### 文章列表解析

从博主主页HTML中提取文章信息：

```html
<a href="/article/7524937913248006694/" target="_blank" rel="noopener" class="title" 
   aria-label="WTT美国大满贯9日战报：混双8强出炉！栋曼横扫晋级；国乒6战全胜">
   WTT美国大满贯9日战报：混双8强出炉！栋曼横扫晋级；国乒6战全胜
</a>
```

提取信息：
- **文章ID**：从href中提取（如：7524937913248006694）
- **标题**：从aria-label或文本内容获取
- **链接**：构建完整URL
- **统计数据**：解析阅读数、评论数等

### 文章详情获取

访问具体文章页面获取：
- **发布时间**：从JSON数据或HTML中提取
- **作者信息**：从页面元素中获取
- **文章摘要**：从meta标签或内容中提取

### 时间解析

支持多种时间格式：
- 标准格式：`2025-01-09 15:30:00`
- 相对时间：`9小时前`、`前天16:35`
- 时间戳：自动转换毫秒/秒级时间戳

## 使用方法

### 1. 基础用法

```python
from toutiao.crawler_new import ToutiaoCrawler

crawler = ToutiaoCrawler()

# 提取用户ID
user_id = crawler.extract_user_id_from_url(blogger_url)

# 获取文章列表
articles = crawler.get_user_articles(user_id, max_count=10)

# 获取文章详情
details = crawler.get_article_details(article_id)

# 获取最新文章（包含详情）
latest_articles = crawler.get_latest_articles(user_id, limit=10)
```

### 2. 配置示例

```json
{
  "toutiao": {
    "blogger_url": "https://www.toutiao.com/c/user/token/MS4wLjABAAAAu8TLqbwurnpNAkvSb1SB60loMjrybIwxT3py56-uKRM/",
    "user_id": "MS4wLjABAAAAu8TLqbwurnpNAkvSb1SB60loMjrybIwxT3py56-uKRM",
    "check_interval_minutes": 30
  }
}
```

## 数据结构

### 文章信息结构

```python
{
    'article_id': '7524937913248006694',
    'title': 'WTT美国大满贯9日战报：混双8强出炉！栋曼横扫晋级；国乒6战全胜',
    'url': 'https://www.toutiao.com/article/7524937913248006694/',
    'author': '纯侃体育',
    'summary': '文章摘要内容...',
    'publish_time': '2025-01-09 15:30:00',
    'read_count': 59000,
    'comment_count': 33
}
```

## 测试方法

### 1. 运行爬虫测试

```bash
python test_crawler.py
```

### 2. 测试内容

- 用户ID提取测试
- 文章列表获取测试
- 文章详情获取测试
- 最新文章获取测试
- 用户访问测试

## 优势对比

### 新策略 vs 旧策略

| 特性 | 新策略（HTML解析） | 旧策略（API调用） |
|------|-------------------|-------------------|
| 反爬虫绕过 | ✅ 高 | ❌ 低 |
| 数据完整性 | ✅ 高 | ⚠️ 中 |
| 稳定性 | ✅ 高 | ❌ 低 |
| 维护成本 | ⚠️ 中 | ✅ 低 |
| 获取速度 | ⚠️ 中 | ✅ 快 |

## 注意事项

### 1. 请求频率
- 建议监控间隔不少于30分钟
- 避免短时间内大量请求
- 使用随机延迟分散请求

### 2. 错误处理
- 网络异常自动重试
- 解析失败降级处理
- 完善的日志记录

### 3. 数据准确性
- 多重验证机制
- 时间格式标准化
- 数据清洗和过滤

## 故障排除

### 常见问题

1. **无法获取文章列表**
   - 检查用户ID是否正确
   - 确认网络连接正常
   - 查看日志中的错误信息

2. **文章详情获取失败**
   - 文章可能已被删除
   - 访问权限限制
   - 页面结构变化

3. **时间解析错误**
   - 检查时间格式
   - 确认时区设置
   - 查看原始数据

### 调试方法

1. 启用DEBUG日志级别
2. 使用测试脚本验证
3. 检查网络请求响应
4. 分析HTML页面结构

## 未来优化

### 1. 性能优化
- 并发请求处理
- 缓存机制
- 增量更新

### 2. 功能扩展
- 支持更多博主类型
- 添加内容分析
- 关键词过滤

### 3. 稳定性提升
- 更多反爬虫策略
- 自适应解析
- 异常恢复机制
