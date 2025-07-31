import os
from google.auth import default
from google.auth.transport.requests import Request
import google.generativeai as genai
from dotenv import load_dotenv
from storage import storage_manager

load_dotenv()

class Config:
    def __init__(self):
        self.setup_gemini()
    
    def setup_gemini(self):
        service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        api_key = os.getenv('GEMINI_API_KEY')
        
        if service_account_path and os.path.exists(service_account_path):
            try:
                credentials, project = default()
                if credentials.expired:
                    credentials.refresh(Request())
                
                genai.configure(credentials=credentials)
                self.project_id = project or os.getenv('GOOGLE_CLOUD_PROJECT')
                print(f"Using service account authentication for project: {self.project_id}")
                self.auth_method = "service_account"
            except Exception as e:
                print(f"Service account authentication failed: {e}")
                if api_key:
                    print("Falling back to API key authentication")
                    genai.configure(api_key=api_key)
                    self.auth_method = "api_key"
                else:
                    raise
            
        elif api_key:
            genai.configure(api_key=api_key)
            print("Using API key authentication")
            self.auth_method = "api_key"
            
        else:
            raise ValueError(
                "No valid authentication found. Please set either:\n"
                "1. GOOGLE_APPLICATION_CREDENTIALS (path to service account JSON)\n"
                "2. GEMINI_API_KEY (API key)"
            )
    
    @staticmethod
    def get_model():
        return genai.GenerativeModel('gemini-2.5-flash')
    
    @staticmethod
    def load_songs():
        """Load all songs from Cloud Storage or local fallback"""
        return storage_manager.list_items('songs')
    
    @staticmethod
    def save_song(song_id, song_data):
        """Save song to Cloud Storage or local fallback"""
        success = storage_manager.save_json('songs', song_id, song_data)
        if not success:
            raise Exception("Failed to save song data")
    
    @staticmethod
    def save_flow(flow_id, flow_data):
        """Save flow to Cloud Storage or local fallback"""
        success = storage_manager.save_json('flows', flow_id, flow_data)
        if not success:
            raise Exception("Failed to save flow data")
    
    @staticmethod
    def load_flows():
        """Load all flows from Cloud Storage or local fallback"""
        return storage_manager.list_items('flows')