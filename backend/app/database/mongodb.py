from typing import Optional
from pymongo import MongoClient
from app.config import get_settings


class MongoDB:
    """MongoDB Atlas connection handler."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
    
    def connect(self) -> bool:
        try:
            settings = get_settings()
            if not settings.mongodb_uri or settings.mongodb_uri == "mongodb://localhost:27017":
                return False
            
            self.client = MongoClient(settings.mongodb_uri)
            self.db = self.client[settings.mongodb_db]
            self.client.admin.command('ping')
            return True
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            return False
    
    def get_db(self):
        if not self.db:
            self.connect()
        return self.db
    
    def close(self):
        if self.client:
            self.client.close()


mongodb = MongoDB()