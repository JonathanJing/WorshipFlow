import os
import json
from google.auth import default
from google.auth.transport.requests import Request
import google.generativeai as genai
from dotenv import load_dotenv

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
        return genai.GenerativeModel('gemini-2.0-flash-exp')
    
    @staticmethod
    def load_songs():
        songs_dir = "data/songs"
        songs = {}
        
        if not os.path.exists(songs_dir):
            return songs
            
        for filename in os.listdir(songs_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(songs_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        song_data = json.load(f)
                        song_id = filename.replace('.json', '')
                        songs[song_id] = song_data
                except Exception as e:
                    print(f"Error loading song {filename}: {e}")
        
        return songs
    
    @staticmethod
    def save_song(song_id, song_data):
        songs_dir = "data/songs"
        os.makedirs(songs_dir, exist_ok=True)
        
        filepath = os.path.join(songs_dir, f"{song_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(song_data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def save_flow(flow_id, flow_data):
        flows_dir = "data/flows"
        os.makedirs(flows_dir, exist_ok=True)
        
        filepath = os.path.join(flows_dir, f"{flow_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(flow_data, f, ensure_ascii=False, indent=2)