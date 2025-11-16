from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
