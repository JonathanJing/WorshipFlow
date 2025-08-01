# WorshipFlow 日志系统使用指南

## 📊 概述

WorshipFlow 内置了完整的用户行为日志系统，支持本地文件存储和 Google Cloud Logging 双重日志记录，用于记录和分析用户操作，帮助优化应用体验和进行数据分析。

## 🏗 日志架构

### 智能日志路由
- **本地开发模式**: 仅使用本地文件日志
- **云端生产模式**: 同时写入本地文件和 Google Cloud Logging
- **自动降级**: Cloud Logging 失败时自动回退到本地日志

## 🔧 配置

### 环境变量配置

在 `.env.local` 文件中配置：

```bash
# 启用/禁用用户行为日志记录
ENABLE_USER_LOGGING=true  # 设置为 false 可禁用日志记录

# 禁用 Cloud Logging（仅使用本地文件）
DISABLE_CLOUD_LOGGING=false  # 设置为 true 可强制使用本地日志

# GCP 项目配置（云端模式需要）
GOOGLE_CLOUD_PROJECT=your-project-id
```

### 日志存储

#### 本地文件日志
- **位置**: `logs/` 目录
- **格式**: 每日一个文件，格式为 `user_actions_YYYY-MM-DD.log`
- **编码**: UTF-8
- **结构**: JSON格式的结构化日志

#### Google Cloud Logging
- **日志名称**: `worship-flow-user-actions`
- **项目**: 配置的 GCP 项目
- **标签**: service, category, user_id
- **严重级别**: INFO, WARNING, ERROR

## 📝 记录的操作类型

### 1. 页面导航 (navigation)
- `page_visit` - 页面访问记录

### 2. 诗歌管理 (song_management)
- `song_added` - 添加新诗歌
- `song_viewed` - 查看诗歌详情

### 3. 敬拜流程设计 (flow_design)
- `flow_saved` - 保存敬拜流程

### 4. AI生成 (ai_generation)
- `opening_transition_generated` - 成功生成开场词
- `opening_transition_failed` - 开场词生成失败
- `transition_generated` - 成功生成串词
- `transition_failed` - 串词生成失败

### 5. 错误记录 (error)
- `error_occurred` - 应用错误记录

## 🔍 日志分析

### 本地文件日志分析

```bash
# 分析所有本地日志
python log_analyzer.py

# 分析特定日期的日志
python log_analyzer.py --date 2024-01-15

# 生成JSON格式报告
python log_analyzer.py --format json --output report.json

# 生成文本报告并保存
python log_analyzer.py --output usage_report.md
```

### Cloud Logging 分析

```bash
# 分析最近24小时的云端日志
python cloud_log_analyzer.py

# 分析最近7天的日志
python cloud_log_analyzer.py --hours 168

# 指定项目ID
python cloud_log_analyzer.py --project-id your-project-id

# 添加过滤条件
python cloud_log_analyzer.py --filter 'severity="ERROR"'

# 生成报告并导出原始数据
python cloud_log_analyzer.py --output cloud_report.md --export-raw raw_data.json
```

### GCP Console 查看

在 Google Cloud Console 中查看日志：
```
https://console.cloud.google.com/logs/query;query=logName%3D%22projects%2Fyour-project-id%2Flogs%2Fworship-flow-user-actions%22
```

### 分析报告内容

1. **用户统计**
   - 独立用户数
   - 独立会话数
   - 总操作数

2. **页面访问分析**
   - 最受欢迎页面
   - 页面访问分布
   - 用户页面使用偏好

3. **诗歌管理分析**
   - 添加诗歌统计
   - 最受欢迎诗歌
   - 热门标签分析

4. **AI功能分析**
   - 模型使用分布
   - AI功能成功率
   - 提示类型统计

5. **敬拜流程分析**
   - 创建流程数量
   - 平均诗歌数量
   - AI串词使用率

6. **错误分析**
   - 错误类型分布
   - 最近错误记录

## 📊 日志数据结构

每条日志记录包含以下字段：

```json
{
  "category": "song_management",
  "action": "song_added", 
  "details": {
    "song_title": "Amazing Grace",
    "song_author": "John Newton",
    "song_tags": ["赞美", "传统"],
    "song_key": "G"
  },
  "user_id": "abc123def456",
  "session_id": "session_789",
  "client_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "timestamp": "2024-01-15T10:30:45.123456",
  "page": "song_manager"
}
```

## 🔐 隐私保护

- **用户ID**: 基于会话信息生成的哈希值，不包含个人信息
- **IP地址**: 仅记录用于会话区分，不用于用户追踪
- **数据存储**: 本地存储，不会发送到外部服务器

## 📈 使用场景

### 1. 产品优化
- 了解用户最常使用的功能
- 识别用户操作中的痛点
- 优化页面流程和用户体验

### 2. 功能分析
- AI功能的使用情况和成功率
- 不同模型的表现对比
- 用户对不同功能的偏好

### 3. 错误监控
- 实时监控应用错误
- 识别常见问题模式
- 改进错误处理机制

### 4. 使用统计
- 用户活跃度分析
- 功能使用频率统计
- 内容创建模式分析

## 🛠 高级用法

### 自定义分析

```python
from log_analyzer import WorshipFlowLogAnalyzer

# 创建分析器实例
analyzer = WorshipFlowLogAnalyzer('logs')

# 加载日志
analyzer.load_logs()

# 获取特定分析数据
user_stats = analyzer.get_user_stats()
ai_analytics = analyzer.get_ai_analytics()

# 自定义分析逻辑
# ... 您的分析代码
```

### 定期报告

可以设置定时任务每日生成分析报告：

```bash
# 添加到 crontab
0 2 * * * cd /path/to/worshipflow && python log_analyzer.py --output daily_report_$(date +\%Y-\%m-\%d).md
```

## ⚠️ 注意事项

1. **日志文件大小**: 高频使用时日志文件可能较大，建议定期清理旧日志
2. **性能影响**: 日志记录对应用性能影响微乎其微
3. **存储空间**: 根据使用量合理规划日志存储空间
4. **数据保护**: 日志包含用户操作信息，请妥善保管

## 🔧 故障排除

### 日志文件未生成
- 检查 `ENABLE_USER_LOGGING` 环境变量
- 确认 `logs/` 目录权限
- 查看应用错误日志

### 分析工具报错
- 确认日志文件格式正确
- 检查 Python 依赖是否安装完整
- 验证日志文件编码为 UTF-8

### 数据不准确
- 确认时区设置正确
- 检查日志时间戳格式
- 验证数据过滤条件