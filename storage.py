import os
import json
from typing import Dict, Any, Optional
from google.cloud import storage
from google.auth import default
import tempfile


class CloudStorageManager:
    """Cloud Storage manager for WorshipFlow data"""
    
    def __init__(self, bucket_name: Optional[str] = None):
        self.bucket_name = bucket_name or os.getenv('GCS_BUCKET_NAME', 'worshipflow-data')
        self.client = None
        self.bucket = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize GCS client"""
        try:
            # Try to get default credentials
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
        """Check if GCS is available"""
        return self.client is not None and self.bucket is not None
    
    def _get_blob_name(self, category: str, item_id: str) -> str:
        """Generate blob name for storage"""
        return f"{category}/{item_id}.json"
    
    def save_json(self, category: str, item_id: str, data: Dict[str, Any]) -> bool:
        """Save JSON data to GCS or local fallback"""
        if self.is_gcs_available():
            return self._save_to_gcs(category, item_id, data)
        else:
            return self._save_to_local(category, item_id, data)
    
    def load_json(self, category: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Load JSON data from GCS or local fallback"""
        if self.is_gcs_available():
            return self._load_from_gcs(category, item_id)
        else:
            return self._load_from_local(category, item_id)
    
    def list_items(self, category: str) -> Dict[str, Dict[str, Any]]:
        """List all items in a category from GCS or local fallback"""
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