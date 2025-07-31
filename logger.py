import logging
import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import streamlit as st

# Optional GCP imports - will fallback gracefully if not available
try:
    from google.cloud import logging as gcp_logging
    from google.auth import default
    GCP_LOGGING_AVAILABLE = True
except ImportError:
    GCP_LOGGING_AVAILABLE = False


class UserActionLogger:
    """
    User Action Logger for WorshipFlow
    用户操作日志记录器
    
    This class logs user actions with session tracking for analytics and debugging.
    该类记录用户操作并进行会话跟踪，用于分析和调试。
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the user action logger
        初始化用户操作日志记录器
        
        Args:
            log_dir: Directory to store log files / 存储日志文件的目录
        """
        self.log_dir = log_dir
        self.use_cloud_logging = self._should_use_cloud_logging()
        self.cloud_logger = None
        self.setup_logging()
    
    def _should_use_cloud_logging(self) -> bool:
        """
        Determine if Cloud Logging should be used
        判断是否应该使用Cloud Logging
        
        Returns:
            bool: True if should use Cloud Logging / 是否使用Cloud Logging
        """
        # Check if running in GCP environment
        is_gcp = os.getenv('GOOGLE_CLOUD_PROJECT') is not None
        
        # Check if force local storage (development mode)
        force_local = os.getenv('FORCE_LOCAL_STORAGE', 'false').lower() == 'true'
        
        # Check if Cloud Logging is explicitly disabled
        cloud_logging_disabled = os.getenv('DISABLE_CLOUD_LOGGING', 'false').lower() == 'true'
        
        return (GCP_LOGGING_AVAILABLE and is_gcp and 
                not force_local and not cloud_logging_disabled)
        
    def setup_logging(self):
        """Setup logging configuration / 设置日志配置"""
        # Setup local logging
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('worship_flow_user_actions')
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Setup Cloud Logging if enabled
        if self.use_cloud_logging:
            self._setup_cloud_logging()
        
        # Always setup local file logging as backup
        self._setup_file_logging()
    
    def _setup_cloud_logging(self):
        """Setup Google Cloud Logging / 设置Google Cloud Logging"""
        try:
            # Initialize Cloud Logging client
            client = gcp_logging.Client()
            
            # Create a Cloud Logging handler
            cloud_handler = client.get_default_handler()
            cloud_handler.setLevel(logging.INFO)
            
            # Add structured logging format
            cloud_formatter = logging.Formatter('%(message)s')
            cloud_handler.setFormatter(cloud_formatter)
            
            self.logger.addHandler(cloud_handler)
            self.cloud_logger = client.logger('worship-flow-user-actions')
            
            print("✅ Cloud Logging initialized successfully")
            
        except Exception as e:
            print(f"❌ Cloud Logging setup failed: {e}")
            print("Falling back to local file logging only")
            self.use_cloud_logging = False
    
    def _setup_file_logging(self):
        """Setup local file logging / 设置本地文件日志"""
        # File handler for daily logs
        log_filename = os.path.join(
            self.log_dir, 
            f"user_actions_{datetime.now().strftime('%Y-%m-%d')}.log"
        )
        
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # JSON formatter for structured logs
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def get_user_id(self) -> str:
        """
        Generate or retrieve user ID for session tracking
        生成或获取用户ID用于会话跟踪
        
        Returns:
            str: Unique user session ID / 唯一用户会话ID
        """
        if 'user_session_id' not in st.session_state:
            # Generate unique session ID based on session info and timestamp
            session_info = f"{st.runtime.get_instance().session_id}_{datetime.now().isoformat()}"
            user_id = hashlib.md5(session_info.encode()).hexdigest()[:12]
            st.session_state.user_session_id = user_id
        
        return st.session_state.user_session_id
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        Get user context information
        获取用户上下文信息
        
        Returns:
            Dict: User context data / 用户上下文数据
        """
        try:
            # Get Streamlit session context
            ctx = st.runtime.get_instance().get_current_session()
            
            return {
                "user_id": self.get_user_id(),
                "session_id": st.runtime.get_instance().session_id,
                "client_ip": getattr(ctx, 'client_ip', 'unknown') if ctx else 'unknown',
                "user_agent": getattr(ctx, 'user_agent', 'unknown') if ctx else 'unknown',
                "timestamp": datetime.now().isoformat(),
                "page": st.session_state.get('page', 'unknown')
            }
        except Exception:
            # Fallback for cases where session context is not available
            return {
                "user_id": self.get_user_id(),
                "session_id": "unknown",
                "client_ip": "unknown", 
                "user_agent": "unknown",
                "timestamp": datetime.now().isoformat(),
                "page": st.session_state.get('page', 'unknown')
            }
    
    def log_action(self, action: str, details: Optional[Dict[str, Any]] = None, 
                   category: str = "general"):
        """
        Log user action with context
        记录用户操作及上下文
        
        Args:
            action: Action description / 操作描述
            details: Additional action details / 额外操作详情
            category: Action category / 操作类别
        """
        # Check if logging is enabled
        if os.getenv('ENABLE_USER_LOGGING', 'true').lower() != 'true':
            return
            
        try:
            log_entry = {
                "category": category,
                "action": action,
                "details": details or {},
                **self.get_user_info()
            }
            
            # Log to local file (JSON format for compatibility)
            self.logger.info(json.dumps(log_entry, ensure_ascii=False))
            
            # Also log to Cloud Logging with structured data
            if self.use_cloud_logging and self.cloud_logger:
                self._log_to_cloud(log_entry)
            
        except Exception as e:
            # Fallback logging in case of errors
            self.logger.error(f"Failed to log action '{action}': {str(e)}")
    
    def _log_to_cloud(self, log_entry: Dict[str, Any]):
        """
        Log structured data to Google Cloud Logging
        将结构化数据记录到Google Cloud Logging
        
        Args:
            log_entry: Log entry data / 日志条目数据
        """
        try:
            # Add severity and labels for better Cloud Logging integration
            severity = 'INFO'
            if log_entry.get('category') == 'error':
                severity = 'ERROR'
            elif log_entry.get('category') == 'ai_generation' and not log_entry.get('details', {}).get('success', True):
                severity = 'WARNING'
            
            # Structure the log for Cloud Logging
            structured_log = {
                **log_entry,
                'severity': severity,
                'service': 'worship-flow',
                'version': '1.0'
            }
            
            # Send to Cloud Logging
            self.cloud_logger.log_struct(
                structured_log,
                severity=severity,
                labels={
                    'service': 'worship-flow',
                    'category': log_entry.get('category', 'general'),
                    'user_id': log_entry.get('user_id', 'unknown')
                }
            )
            
        except Exception as e:
            # Don't fail the main logging if Cloud Logging fails
            print(f"Cloud Logging failed: {e}")
    
    def log_page_visit(self, page_name: str):
        """Log page visit / 记录页面访问"""
        self.log_action(
            action="page_visit",
            details={"page_name": page_name},
            category="navigation"
        )
    
    def log_song_action(self, action: str, song_data: Dict[str, Any]):
        """Log song-related actions / 记录诗歌相关操作"""
        self.log_action(
            action=action,
            details={
                "song_title": song_data.get("title", "unknown"),
                "song_author": song_data.get("author", "unknown"),
                "song_tags": song_data.get("tags", []),
                "song_key": song_data.get("key", "unknown")
            },
            category="song_management"
        )
    
    def log_flow_action(self, action: str, flow_data: Dict[str, Any]):
        """Log worship flow actions / 记录敬拜流程操作"""
        self.log_action(
            action=action,
            details={
                "sermon_title": flow_data.get("sermon_title", "unknown"),
                "key_scripture": flow_data.get("key_scripture", "unknown"),
                "date": flow_data.get("date", "unknown"),
                "song_count": len(flow_data.get("worship_flow", [])),
                "has_transitions": any(
                    item.get("type") == "transition_text" 
                    for item in flow_data.get("worship_flow", [])
                )
            },
            category="flow_design"
        )
    
    def log_ai_action(self, action: str, model_name: str, prompt_type: str, 
                      success: bool, details: Optional[Dict[str, Any]] = None):
        """Log AI-related actions / 记录AI相关操作"""
        self.log_action(
            action=action,
            details={
                "model_name": model_name,
                "prompt_type": prompt_type,
                "success": success,
                "additional_details": details or {}
            },
            category="ai_generation"
        )
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None):
        """Log application errors / 记录应用错误"""
        self.log_action(
            action="error_occurred",
            details={
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {}
            },
            category="error"
        )


# Global logger instance
user_logger = UserActionLogger()