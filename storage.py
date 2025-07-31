import os
import json
from typing import Dict, Any, Optional
from google.cloud import storage
from google.auth import default
import tempfile


class CloudStorageManager:
    """
    Cloud Storage manager for WorshipFlow data
    云存储管理器，用于管理WorshipFlow数据
    
    This class provides a unified interface for storing and retrieving
    worship songs and flows data, with automatic fallback to local storage
    when Cloud Storage is not available.
    
    该类为存储和检索敬拜诗歌和流程数据提供统一接口，
    当Cloud Storage不可用时自动回退到本地存储。
    """
    
    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize CloudStorageManager
        初始化云存储管理器
        
        Args:
            bucket_name: GCS bucket name, defaults to env var or 'worshipflow-data'
                        GCS存储桶名称，默认为环境变量或'worshipflow-data'
        """
        self.bucket_name = bucket_name or os.getenv('GCS_BUCKET_NAME', 'worshipflow-data')
        self.client = None
        self.bucket = None
        self._initialize_client()
    
    def _initialize_client(self):
        """
        Initialize GCS client / 初始化GCS客户端
        
        Attempts to connect to Google Cloud Storage using default credentials.
        Falls back to local storage if connection fails.
        
        尝试使用默认凭证连接Google Cloud Storage。
        如果连接失败则回退到本地存储。
        """
        try:
            # Try to get default credentials / 尝试获取默认凭证
            credentials, project = default()
            self.client = storage.Client(credentials=credentials, project=project)
            self.bucket = self.client.bucket(self.bucket_name)
            print(f"✅ Connected to GCS bucket: {self.bucket_name}")
        except Exception as e:
            print(f"❌ GCS initialization failed: {e}")
            print("Using local storage fallback")
            self.client = None
            self.bucket = None
    
    def is_gcs_available(self) -> bool:
        """
        Check if GCS is available / 检查GCS是否可用
        
        Returns:
            bool: True if GCS client and bucket are initialized
                 如果GCS客户端和存储桶已初始化则返回True
        """
        return self.client is not None and self.bucket is not None
    
    def _get_blob_name(self, category: str, item_id: str) -> str:
        """
        Generate blob name for storage / 生成存储的blob名称
        
        Args:
            category: Data category (songs/flows) / 数据类别（诗歌/流程）
            item_id: Unique identifier / 唯一标识符
            
        Returns:
            str: Formatted blob name / 格式化的blob名称
        """
        return f"{category}/{item_id}.json"
    
    def save_json(self, category: str, item_id: str, data: Dict[str, Any]) -> bool:
        """
        Save JSON data to GCS or local fallback / 将JSON数据保存到GCS或本地备选
        
        Args:
            category: Data category (songs/flows) / 数据类别（诗歌/流程）
            item_id: Unique identifier / 唯一标识符
            data: JSON data to save / 要保存的JSON数据
            
        Returns:
            bool: True if save successful / 保存成功返回True
        """
        if self.is_gcs_available():
            return self._save_to_gcs(category, item_id, data)
        else:
            return self._save_to_local(category, item_id, data)
    
    def load_json(self, category: str, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Load JSON data from GCS or local fallback / 从GCS或本地备选加载JSON数据
        
        Args:
            category: Data category (songs/flows) / 数据类别（诗歌/流程）
            item_id: Unique identifier / 唯一标识符
            
        Returns:
            Optional[Dict]: Loaded data or None if not found / 加载的数据，未找到则返回None
        """
        if self.is_gcs_available():
            return self._load_from_gcs(category, item_id)
        else:
            return self._load_from_local(category, item_id)
    
    def list_items(self, category: str) -> Dict[str, Dict[str, Any]]:
        """
        List all items in a category from GCS or local fallback
        从GCS或本地备选列出类别中的所有项目
        
        Args:
            category: Data category (songs/flows) / 数据类别（诗歌/流程）
            
        Returns:
            Dict: All items in the category / 类别中的所有项目
        """
        if self.is_gcs_available():
            return self._list_from_gcs(category)
        else:
            return self._list_from_local(category)
    
    def _save_to_gcs(self, category: str, item_id: str, data: Dict[str, Any]) -> bool:
        """Save to Google Cloud Storage"""
        try:
            blob_name = self._get_blob_name(category, item_id)
            blob = self.bucket.blob(blob_name)
            
            # Convert to JSON string
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            
            # Upload to GCS
            blob.upload_from_string(json_data, content_type='application/json')
            print(f"✅ Saved {blob_name} to GCS")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save {category}/{item_id} to GCS: {e}")
            return False
    
    def _load_from_gcs(self, category: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Load from Google Cloud Storage"""
        try:
            blob_name = self._get_blob_name(category, item_id)
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                return None
            
            # Download and parse JSON
            json_data = blob.download_as_text()
            return json.loads(json_data)
            
        except Exception as e:
            print(f"❌ Failed to load {category}/{item_id} from GCS: {e}")
            return None
    
    def _list_from_gcs(self, category: str) -> Dict[str, Dict[str, Any]]:
        """List items from Google Cloud Storage"""
        try:
            prefix = f"{category}/"
            blobs = self.bucket.list_blobs(prefix=prefix)
            
            items = {}
            for blob in blobs:
                if blob.name.endswith('.json'):
                    # Extract item_id from blob name
                    item_id = blob.name.replace(prefix, '').replace('.json', '')
                    
                    # Download and parse JSON
                    try:
                        json_data = blob.download_as_text()
                        items[item_id] = json.loads(json_data)
                    except Exception as e:
                        print(f"❌ Failed to load {blob.name}: {e}")
            
            return items
            
        except Exception as e:
            print(f"❌ Failed to list {category} from GCS: {e}")
            return {}
    
    def _save_to_local(self, category: str, item_id: str, data: Dict[str, Any]) -> bool:
        """Fallback: Save to local filesystem"""
        try:
            dir_path = f"data/{category}"
            os.makedirs(dir_path, exist_ok=True)
            
            file_path = os.path.join(dir_path, f"{item_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Saved {category}/{item_id} locally")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save {category}/{item_id} locally: {e}")
            return False
    
    def _load_from_local(self, category: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Fallback: Load from local filesystem"""
        try:
            file_path = f"data/{category}/{item_id}.json"
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"❌ Failed to load {category}/{item_id} locally: {e}")
            return None
    
    def _list_from_local(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Fallback: List from local filesystem"""
        try:
            dir_path = f"data/{category}"
            
            if not os.path.exists(dir_path):
                return {}
            
            items = {}
            for filename in os.listdir(dir_path):
                if filename.endswith('.json'):
                    item_id = filename.replace('.json', '')
                    item_data = self._load_from_local(category, item_id)
                    if item_data:
                        items[item_id] = item_data
            
            return items
            
        except Exception as e:
            print(f"❌ Failed to list {category} locally: {e}")
            return {}


# Global storage instance
storage_manager = CloudStorageManager()