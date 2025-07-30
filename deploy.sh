#!/bin/bash

# WorshipFlow - Cloud Run Deployment Script
# 使用前请确保: gcloud CLI已安装并已认证

set -e

# 配置变量
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
SERVICE_NAME=${SERVICE_NAME:-"worshipflow"}
REGION=${REGION:-"asia-east1"}
BUCKET_NAME=${BUCKET_NAME:-"${PROJECT_ID}-worshipflow-data"}
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 部署 WorshipFlow 到 Google Cloud Run"
echo "项目ID: $PROJECT_ID"
echo "服务名称: $SERVICE_NAME"
echo "区域: $REGION"
echo "存储桶: $BUCKET_NAME"

# 检查必要的环境变量
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo "❌ 请设置 PROJECT_ID 环境变量"
    echo "export PROJECT_ID=your-actual-project-id"
    exit 1
fi

# 设置项目
echo "📋 设置 gcloud 项目..."
gcloud config set project $PROJECT_ID

# 启用必要的API
echo "🔌 启用必要的 Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable generativelanguage.googleapis.com

# 创建存储桶
echo "🪣 创建 Cloud Storage 存储桶..."
if ! gsutil ls -b gs://$BUCKET_NAME >/dev/null 2>&1; then
    gsutil mb -l $REGION gs://$BUCKET_NAME
    echo "✅ 存储桶 $BUCKET_NAME 已创建"
else
    echo "📦 存储桶 $BUCKET_NAME 已存在"
fi

# 构建Docker镜像
echo "🔨 构建 Docker 镜像..."
gcloud builds submit --tag $IMAGE_NAME

# 部署到Cloud Run
echo "🚀 部署到 Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "GCS_BUCKET_NAME=${BUCKET_NAME}" \
    --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY}" \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"

# 获取服务URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo ""
echo "🎉 部署完成!"
echo "📱 应用访问地址: $SERVICE_URL"
echo "🪣 数据存储桶: gs://$BUCKET_NAME"
echo ""
echo "💡 后续步骤:"
echo "1. 访问应用URL验证部署"
echo "2. 在诗歌库中添加一些诗歌测试存储功能"
echo "3. 配置域名 (可选)"
echo ""
echo "🔧 管理命令:"
echo "查看日志: gcloud run services logs tail $SERVICE_NAME --region=$REGION"
echo "更新服务: ./deploy.sh"
echo "删除服务: gcloud run services delete $SERVICE_NAME --region=$REGION"