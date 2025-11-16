from pydantic_settings import BaseSettings
from pydantic import ConfigDict  # CORREZIONE: ConfigDict si importa da 'pydantic', non 'pydantic_settings'
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "")

    # CORREZIONE: Sostituita la 'class Config' deprecata con 'model_config'
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding='utf-8'
    )

settings = Settings()