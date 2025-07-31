# WorshipFlow Dockerfile for Google Cloud Run deployment
# WorshipFlow Docker文件，用于Google Cloud Run部署

# Use Python 3.11 slim image for smaller size and security
# 使用Python 3.11 slim镜像以获得更小的体积和更好的安全性
FROM python:3.11-slim

# Set working directory / 设置工作目录
WORKDIR /app

# Install system dependencies required for building Python packages
# 安装构建Python包所需的系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
# 首先复制requirements以获得更好的Docker层缓存
COPY requirements.txt .

# Install Python dependencies / 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code / 复制应用代码
COPY . .

# Create non-root user for security / 为安全创建非root用户
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port (Cloud Run will set PORT env var automatically)
# 暴露端口（Cloud Run会自动设置PORT环境变量）
EXPOSE 8080

# Health check for container monitoring
# 容器监控健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/_stcore/health || exit 1

# Run the Streamlit application with Cloud Run optimized settings
# 使用Cloud Run优化设置运行Streamlit应用
CMD streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --browser.gatherUsageStats=false