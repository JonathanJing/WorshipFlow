# WorshipFlow - Google Cloud Run 部署指南

本指南将帮助你将 WorshipFlow 部署到 Google Cloud Run，使用 Cloud Storage 存储数据。

## 🚀 快速部署

### 前提条件

1. **Google Cloud 账户** - 需要有效的 Google Cloud 项目
2. **gcloud CLI** - [安装指南](https://cloud.google.com/sdk/docs/install)
3. **已启用结算** - Cloud Run 和 Cloud Storage 需要启用结算

### 1. 克隆和配置项目

```bash
# 克隆项目 (如果还没有)
git clone <your-repo-url>
cd WorshipFlow

# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
nano .env
```

### 2. 设置 Google Cloud 项目

```bash
# 登录 Google Cloud
gcloud auth login

# 设置项目ID (替换为你的项目ID)
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# 获取 Gemini API Key (可选，也可以使用服务账户)
# 访问: https://aistudio.google.com/app/apikey
export GEMINI_API_KEY="your-api-key"
```

### 3. 一键部署

```bash
# 给部署脚本执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

部署脚本会自动：
- 启用必要的 Google Cloud APIs
- 创建 Cloud Storage 存储桶
- 构建 Docker 镜像  
- 部署到 Cloud Run
- 显示应用访问地址

## 🔧 手动部署步骤

如果你想手动控制每个步骤：

### 1. 启用必要的 APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com  
gcloud services enable storage.googleapis.com
gcloud services enable generativelanguage.googleapis.com
```

### 2. 创建 Cloud Storage 存储桶

```bash
# 创建存储桶 (区域建议选择亚洲)
gsutil mb -l asia-east1 gs://$PROJECT_ID-worshipflow-data
```

### 3. 构建 Docker 镜像

```bash
# 方法一：使用 cloudbuild.yaml 配置文件（推荐）
gcloud builds submit --config=cloudbuild.yaml

# 方法二：使用直接命令（如果遇到日志配置错误）
gcloud builds submit --tag gcr.io/$PROJECT_ID/worshipflow --logging=CLOUD_LOGGING_ONLY
```

**注意**: 如果遇到 `build.service_account` 相关的日志配置错误，使用 `--logging=CLOUD_LOGGING_ONLY` 参数可以解决。

### 4. 部署到 Cloud Run

```bash
# 部署服务
gcloud run deploy worshipflow \
    --image gcr.io/$PROJECT_ID/worshipflow \
    --platform managed \
    --region asia-east1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "GCS_BUCKET_NAME=$PROJECT_ID-worshipflow-data" \
    --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY" \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID"
```

## 🛡️ 安全配置 (推荐)

### 使用服务账户而不是 API Key

1. 创建服务账户：

```bash
# 创建服务账户
gcloud iam service-accounts create worshipflow-sa \
    --display-name="WorshipFlow Service Account"

# 赋予必要权限
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:worshipflow-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:worshipflow-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

2. 更新 Cloud Run 服务使用服务账户：

```bash
gcloud run services update worshipflow \
    --service-account=worshipflow-sa@$PROJECT_ID.iam.gserviceaccount.com \
    --region=asia-east1
```

### 存储 API Key 在 Secret Manager (如果使用 API Key)

```bash
# 创建密钥
echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-

# 给服务账户访问密钥的权限
gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:worshipflow-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# 更新服务使用密钥
gcloud run services update worshipflow \
    --update-env-vars="GEMINI_API_KEY_SECRET=projects/$PROJECT_ID/secrets/gemini-api-key/versions/latest" \
    --region=asia-east1
```

## 📊 监控和管理

### 查看日志

```bash
# 实时查看日志
gcloud run services logs tail worshipflow --region=asia-east1

# 查看特定时间范围的日志
gcloud run services logs read worshipflow --region=asia-east1 --limit=50
```

### 查看服务状态

```bash
# 查看服务详情
gcloud run services describe worshipflow --region=asia-east1

# 列出所有 Cloud Run 服务
gcloud run services list
```

### 更新服务

```bash
# 重新构建和部署
gcloud builds submit --tag gcr.io/$PROJECT_ID/worshipflow
gcloud run deploy worshipflow \
    --image gcr.io/$PROJECT_ID/worshipflow \
    --region=asia-east1
```

## 💰 成本优化

### Cloud Run 定价
- **请求数**: 每月前 200 万次请求免费
- **计算时间**: 每月前 18 万 vCPU-秒和 32 万 GiB-秒免费
- **网络**: 每月前 1GB 出站流量免费

### Cloud Storage 定价
- **存储**: 标准存储每月前 5GB 免费
- **操作**: 每月一定数量的读写操作免费

### 优化建议
1. 设置合适的 `minScale=0` 让服务可以缩容到0
2. 使用适当的内存和CPU配置 (1Gi内存，1CPU对大多数情况足够)
3. 定期清理不需要的镜像版本

## 🔧 故障排除

### 常见问题

1. **Cloud Build 日志配置错误**
   ```
   错误: if 'build.service_account' is specified, the build must either (a) specify 'build.logs_bucket'...
   ```
   **解决方案**:
   - 使用 `--logging=CLOUD_LOGGING_ONLY` 参数
   - 或者使用提供的 `cloudbuild.yaml` 配置文件
   ```bash
   gcloud builds submit --tag gcr.io/$PROJECT_ID/worshipflow --logging=CLOUD_LOGGING_ONLY
   ```

2. **部署失败 - 权限错误**
   ```bash
   # 确保你有必要的IAM权限
   gcloud auth list
   gcloud projects get-iam-policy $PROJECT_ID
   ```

3. **应用启动失败 - 端口错误**
   - 确保 Dockerfile 中 EXPOSE 8080
   - 确保 streamlit 配置使用 $PORT 环境变量

4. **Gemini API 调用失败**
   - 检查 API Key 是否有效
   - 确保 Generative Language API 已启用
   - 检查环境变量设置

5. **Cloud Storage 访问失败**
   - 确保存储桶存在且可访问
   - 检查服务账户权限
   - 验证 GCS_BUCKET_NAME 环境变量

### 调试命令

```bash
# 查看环境变量
gcloud run services describe worshipflow --region=asia-east1 --format="export"

# 测试 Cloud Storage 访问
gsutil ls gs://$PROJECT_ID-worshipflow-data

# 测试容器本地运行
docker build -t worshipflow-test .
docker run -p 8080:8080 \
    -e GEMINI_API_KEY=$GEMINI_API_KEY \
    -e GCS_BUCKET_NAME=$PROJECT_ID-worshipflow-data \
    worshipflow-test
```

## 🎯 后续步骤

1. **配置自定义域名** (可选)
   - 在 Cloud Run 控制台配置域名映射
   - 设置 SSL 证书

2. **设置监控告警**
   - 配置 Cloud Monitoring 告警
   - 监控错误率和响应时间

3. **备份数据**
   - 定期备份 Cloud Storage 存储桶
   - 考虑跨区域复制重要数据

## 📞 支持

如果遇到问题，请：
1. 查看 [Cloud Run 文档](https://cloud.google.com/run/docs)
2. 检查 [Cloud Storage 文档](https://cloud.google.com/storage/docs)
3. 在项目 GitHub 仓库提交 Issue