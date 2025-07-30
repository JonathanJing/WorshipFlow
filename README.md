# 灵泉Flow (WorshipFlow) 

基于AI的敬拜串词生成系统，使用 Gemini 2.5 Pro 为敬拜主领生成高质量的诗歌串词。

## 功能特色

- 🎵 **诗歌库管理**: 添加和管理敬拜诗歌
- ✨ **敬拜流程设计**: 创建完整的主日敬拜流程
- 🤖 **AI串词生成**: 使用 Gemini 2.5 Pro 生成多维度串词
- 🎭 **排练模式**: 查看和导出完整敬拜讲稿

## 技术栈

- **前端**: Streamlit
- **AI模型**: Google Gemini 2.5 Pro
- **认证**: Google Cloud Service Account / API Key
- **数据存储**: Google Cloud Storage (支持本地fallback)
- **部署平台**: Google Cloud Run
- **语言**: Python 3.11+

## 项目结构

```
WorshipFlow/
├── app.py                  # 主应用程序
├── config.py              # 配置和Gemini API管理
├── storage.py             # Cloud Storage适配器
├── requirements.txt       # 依赖包
├── .env.example          # 环境变量示例
├── Dockerfile            # Docker容器配置
├── deploy.sh             # 一键部署脚本
├── service.yaml          # Cloud Run服务配置
├── DEPLOYMENT.md         # 详细部署指南
├── .streamlit/           # Streamlit配置
│   └── config.toml
└── data/                 # 本地数据存储(fallback)
    ├── songs/           # 诗歌JSON文件
    └── flows/           # 敬拜流程文件
```

## 快速开始

### 🚀 Cloud Run 部署 (推荐)

1. **克隆项目**
   ```bash
   git clone <your-repo-url>
   cd WorshipFlow
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，设置 PROJECT_ID 和 GEMINI_API_KEY
   ```

3. **一键部署**
   ```bash
   export PROJECT_ID="your-project-id"
   export GEMINI_API_KEY="your-api-key"
   ./deploy.sh
   ```

详细部署指南请参考 [DEPLOYMENT.md](DEPLOYMENT.md)

### 💻 本地开发

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置认证

**方法一：Service Account（推荐生产环境）**

1. 在 [Google Cloud Console](https://console.cloud.google.com/) 创建项目
2. 启用 Generative AI API 和 Cloud Storage API
3. 创建 Service Account 并下载 JSON 密钥文件
4. 设置环境变量：

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
export GOOGLE_CLOUD_PROJECT=your-project-id
export GCS_BUCKET_NAME=your-bucket-name  # 可选
```

**方法二：API Key（适合开发测试）**

```bash
export GEMINI_API_KEY=your-gemini-api-key
```

#### 3. 运行应用

```bash
streamlit run app.py
```

## 使用指南

### 1. 诗歌库管理
- 在侧边栏点击"诗歌库管理"
- 添加新诗歌：输入标题、作者、歌词和标签
- 查看诗歌：搜索和浏览已添加的诗歌

### 2. 敬拜流程设计
- 输入证道主题和核心经文
- 选择敬拜诗歌并排序
- 点击"生成串词"按钮生成AI串词
- 选择合适的串词维度

### 3. 排练模式
- 查看完整的敬拜流程
- 导出Markdown格式的讲稿

## AI串词生成

系统会根据以下信息生成三个维度的串词：

- **赞美维度**: 引导会众从一首歌过渡到下一首
- **激励维度**: 结合证道主题给予属灵鼓励
- **祷告维度**: 生成可带领会众的祷告词

## 数据格式

### 诗歌JSON格式
```json
{
  "title": "Here I Am to Worship",
  "author": "Tim Hughes",
  "key": "D", 
  "lyrics": "歌词内容...",
  "tags": ["赞美", "敬拜", "道成肉身"]
}
```

### 敬拜流程JSON格式
```json
{
  "date": "2023-10-29",
  "sermon_title": "行在光明中",
  "key_scripture": "约翰一书 1:7",
  "worship_flow": [
    {
      "type": "song",
      "song_id": "here_i_am_to_worship"
    },
    {
      "type": "transition_text", 
      "content": "生成的串词内容..."
    }
  ]
}
```

## 架构特点

### 🔄 数据存储策略
- **生产环境**: 使用 Google Cloud Storage 持久化存储
- **开发环境**: 自动fallback到本地文件存储
- **数据格式**: 统一的JSON格式，便于迁移和备份

### 🛡️ 安全性
- **认证**: 支持Service Account和API Key两种认证方式
- **权限**: 最小权限原则，仅授予必要的API访问权限
- **密钥管理**: 推荐使用Secret Manager存储敏感信息

### ⚡ 性能优化
- **容器化**: Docker容器确保环境一致性
- **自动扩缩容**: Cloud Run根据负载自动调整实例数量
- **缓存策略**: Streamlit内置缓存提升响应速度

## 注意事项

- **网络连接**: 确保有稳定的网络连接以访问 Gemini API
- **数据备份**: Cloud Storage自动提供数据冗余，建议定期导出重要数据
- **认证安全**: 生产环境推荐使用Service Account而非API Key
- **成本控制**: Cloud Run和Cloud Storage都有免费额度，适合小规模使用

## 故障排除

### 常见问题

1. **认证错误**
   - 检查环境变量设置
   - 验证Service Account权限
   - 确认API已启用

2. **部署失败**
   - 检查gcloud CLI配置
   - 验证项目权限
   - 查看Cloud Build日志

3. **数据存储问题**
   - 验证Cloud Storage权限
   - 检查存储桶配置
   - 查看应用日志

4. **API调用失败**
   - 确认网络连接
   - 检查API配额限制
   - 验证Gemini API密钥

### 调试命令

```bash
# 查看Cloud Run服务日志
gcloud run services logs tail worshipflow --region=asia-east1

# 测试本地容器
docker build -t worshipflow-test .
docker run -p 8080:8080 -e GEMINI_API_KEY=$GEMINI_API_KEY worshipflow-test

# 检查Cloud Storage访问
gsutil ls gs://your-bucket-name
```

## 版本更新

### v2.0 (当前版本)
- ✅ 迁移到Google Cloud Storage持久化存储
- ✅ 支持Google Cloud Run部署
- ✅ 优化用户体验和成功消息显示
- ✅ 修复排练模式数据读取问题
- ✅ 添加自动fallback存储机制

### v1.0
- 基础诗歌库管理功能
- AI串词生成
- 敬拜流程设计
- 排练模式和讲稿导出

## 技术支持

如需帮助，请：
1. 查看 [部署指南](DEPLOYMENT.md)
2. 检查 [故障排除](#故障排除) 部分
3. 提交 [GitHub Issue](https://github.com/your-repo/issues)

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 许可证

本项目基于 MIT 许可证开源。