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
- **认证**: Google Cloud Service Account
- **数据存储**: 本地JSON文件
- **语言**: Python 3.12

## 项目结构

```
WorshipFlow/
├── app.py                  # 主应用程序
├── config.py              # 配置管理
├── requirements.txt       # 依赖包
├── .env.example          # 环境变量示例
├── .streamlit/           # Streamlit配置
│   └── config.toml
└── data/                 # 数据存储
    ├── songs/           # 诗歌JSON文件
    └── flows/           # 敬拜流程文件
```

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 Google Cloud Service Account

#### 方法一：使用Service Account（推荐）

1. 在 [Google Cloud Console](https://console.cloud.google.com/) 创建项目
2. 启用 Generative AI API
3. 创建 Service Account 并下载 JSON 密钥文件
4. 复制 `.env.example` 为 `.env`
5. 设置环境变量：

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
export GOOGLE_CLOUD_PROJECT=your-project-id
```

#### 方法二：使用API Key

```bash
export GEMINI_API_KEY=your-gemini-api-key
```

### 3. 运行应用

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

## 注意事项

- 确保有稳定的网络连接以访问 Gemini API
- 本地数据存储在 `data/` 目录中
- 建议定期备份诗歌和流程数据
- 使用 Service Account 认证比 API Key 更安全

## 故障排除

1. **认证错误**: 检查环境变量和Service Account配置
2. **API调用失败**: 确认网络连接和API配额
3. **诗歌数据丢失**: 检查 `data/songs/` 目录权限
4. **Streamlit启动失败**: 确认依赖包已正确安装

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 许可证

本项目基于 MIT 许可证开源。