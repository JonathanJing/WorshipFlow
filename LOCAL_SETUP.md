# 本地开发设置指南 / Local Development Setup Guide

本指南帮助你在本地环境中运行 WorshipFlow，使用本地 `data/` 文件夹而不是 Google Cloud Storage。

This guide helps you run WorshipFlow locally, using the local `data/` folder instead of Google Cloud Storage.

## 🚀 快速开始 / Quick Start

### 1. 环境配置 / Environment Configuration

项目已经配置了本地开发环境文件 `.env.local`：

```bash
# 强制使用本地存储
FORCE_LOCAL_STORAGE=true

# 可选：设置 Gemini API 密钥用于 AI 功能
# GEMINI_API_KEY=your_api_key_here
```

### 2. 启动方式 / Launch Options

#### 方式 1：使用启动脚本（推荐）/ Method 1: Using Startup Script (Recommended)

```bash
python start_local.py
```

#### 方式 2：直接启动 Streamlit / Method 2: Direct Streamlit Launch

```bash
# 确保加载本地环境变量
source .env.local  # 或在 Windows: set FORCE_LOCAL_STORAGE=true

# 启动应用
streamlit run app.py
```

### 3. 访问应用 / Access Application

启动后访问：http://localhost:8501

## 📁 数据存储 / Data Storage

### 本地数据结构 / Local Data Structure

```
data/
├── songs/          # 诗歌数据 / Songs data
│   ├── amazing_grace.json
│   ├── here_i_am_to_worship.json
│   └── ...
└── flows/          # 敬拜流程 / Worship flows  
    ├── 2024-01-15_103045_service.json
    └── ...
```

### 现有数据 / Existing Data

你的 `data/songs/` 文件夹已包含示例诗歌：

- `amazing_grace.json`
- `here_i_am_to_worship.json`
- `how_great_is_our_god.json`
- `因他活着.json`

## ⚙️ 配置说明 / Configuration Details

### 环境变量 / Environment Variables

| 变量名                   | 默认值               | 说明                           |
| ------------------------ | -------------------- | ------------------------------ |
| `FORCE_LOCAL_STORAGE`  | `false`            | 强制使用本地存储               |
| `GEMINI_MODEL`         | `gemini-2.5-flash` | 使用的Gemini模型               |
| `GEMINI_API_KEY`       | -                    | Gemini AI API 密钥             |
| `GOOGLE_CLOUD_PROJECT` | -                    | GCP 项目 ID（本地模式不需要）  |
| `GCS_BUCKET_NAME`      | `worshipflow-data` | GCS 存储桶名（本地模式不需要） |

### 可用的AI模型 / Available AI Models

| 模型名称             | 特点            | 适用场景             |
| -------------------- | --------------- | -------------------- |
| `gemini-2.5-flash` | ⚡ 最新快速模型 | 推荐，速度快，质量高 |
| `gemini-2.5-pro`   | 🧠 专业版本     | 复杂任务，更高质量   |

### 工作模式 / Working Modes

1. **本地模式（推荐用于开发）/ Local Mode (Recommended for Development)**

   - 设置 `FORCE_LOCAL_STORAGE=true`
   - 所有数据读写都在本地 `data/` 文件夹
   - 不需要 Google Cloud 凭证
2. **云端模式 / Cloud Mode**

   - 设置 `FORCE_LOCAL_STORAGE=false` 或不设置
   - 优先使用 Google Cloud Storage
   - 连接失败时自动回退到本地存储

## 🔧 开发测试 / Development Testing

### 模型切换 / Model Switching

**方式1：通过UI切换**

- 在侧边栏的"🤖 AI 模型"部分选择不同模型
- 切换后立即生效，重新生成的串词会使用新模型

**方式2：通过环境变量**

```bash
# 在 .env.local 中设置
GEMINI_MODEL=gemini-1.5-pro

# 或者临时设置
export GEMINI_MODEL=gemini-1.5-pro
streamlit run app.py
```

### 添加测试数据 / Adding Test Data

1. 启动应用后访问"诗歌库管理"页面
2. 使用"添加新歌"功能添加诗歌
3. 数据会自动保存到 `data/songs/` 文件夹

### 功能测试 / Feature Testing

1. **诗歌管理** - 添加、查看诗歌
2. **流程设计** - 选择诗歌、生成串词
3. **排练模式** - 查看完整敬拜流程
4. **模型测试** - 切换不同模型测试串词生成质量

## 🚀 部署到云端 / Deploy to Cloud

当准备部署到生产环境时：

1. 设置 `FORCE_LOCAL_STORAGE=false`
2. 配置 Google Cloud 凭证
3. 使用现有的 Cloud Run 部署脚本

## ❓ 故障排除 / Troubleshooting

### 常见问题 / Common Issues

1. **端口被占用**

   ```bash
   # 停止现有进程
   pkill -f streamlit

   # 使用不同端口
   streamlit run app.py --server.port 8502
   ```
2. **缺少依赖**

   ```bash
   pip install -r requirements.txt
   ```
3. **API 密钥问题**

   - 在 `.env.local` 中设置 `GEMINI_API_KEY`
   - 或者使用 Google Cloud 服务账号凭证

### 检查配置 / Check Configuration

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv('.env.local', override=True)
print(f'Force local: {os.getenv(\"FORCE_LOCAL_STORAGE\")}')
"
```

## 📝 注意事项 / Notes

- 本地数据与云端数据不会自动同步
- 建议在本地开发时使用独立的测试数据
- 生产环境请使用云端存储确保数据安全性
