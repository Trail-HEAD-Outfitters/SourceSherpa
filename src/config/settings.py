import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        self.mongodb_host = os.getenv("MONGODB_HOST", "localhost")
        self.mongodb_port = int(os.getenv("MONGODB_PORT", "27017"))
        self.mongodb_username = os.getenv("MONGODB_USERNAME")
        self.mongodb_password = os.getenv("MONGODB_PASSWORD")
        self.mongodb_database = os.getenv("MONGODB_DATABASE", "sourcesherpa")
        
    @property
    def mongodb_uri(self) -> str:
        """Construct MongoDB URI based on configuration."""
        if self.mongodb_username and self.mongodb_password:
            return f"mongodb://{self.mongodb_username}:{self.mongodb_password}@{self.mongodb_host}:{self.mongodb_port}/?authSource=admin"
        return f"mongodb://{self.mongodb_host}:{self.mongodb_port}"

# Create a global settings instance
settings = Settings() 