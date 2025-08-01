#!/usr/bin/env python3
"""
Local development startup script for WorshipFlow
本地开发启动脚本

This script loads local environment variables and starts Streamlit with local data folder.
该脚本加载本地环境变量并使用本地数据文件夹启动Streamlit。
"""

import os
import sys
from dotenv import load_dotenv

def main():
    # Load local environment variables first
    # 优先加载本地环境变量
    if os.path.exists('.env.local'):
        print("🔧 Loading local development configuration from .env.local")
        load_dotenv('.env.local', override=True)
    
    # Then load .env if it exists (for production overrides)
    # 然后加载.env文件（用于生产环境覆盖）
    if os.path.exists('.env'):
        print("📋 Loading .env configuration")
        load_dotenv('.env')
    
    # Ensure data directory exists
    # 确保数据目录存在
    os.makedirs('data/songs', exist_ok=True)
    os.makedirs('data/flows', exist_ok=True)
    print("📁 Local data directories ready: data/songs, data/flows")
    
    # Display current configuration
    # 显示当前配置
    force_local = os.getenv('FORCE_LOCAL_STORAGE', 'false').lower() == 'true'
    print(f"🏠 Force local storage: {'Enabled' if force_local else 'Disabled'}")
    
    if force_local:
        print("✅ Running in local development mode - data will be read from/saved to local 'data/' folder")
    else:
        print("☁️ Cloud storage mode - will attempt GCS connection with fallback to local")
    
    # Start Streamlit
    # 启动Streamlit
    print("\n🚀 Starting WorshipFlow...")
    os.system(f"{sys.executable} -m streamlit run app.py")

if __name__ == "__main__":
    main()