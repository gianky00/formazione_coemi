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

    # SMTP Settings for email notifications
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.example.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER", "user@example.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "password")
    EMAIL_RECIPIENTS_TO: str = os.getenv("EMAIL_RECIPIENTS_TO", "gianky.allegretti@gmail.com")
    EMAIL_RECIPIENTS_CC: str = os.getenv("EMAIL_RECIPIENTS_CC", "")

    # CORREZIONE: Sostituita la 'class Config' deprecata con 'model_config'
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding='utf-8'
    )

settings = Settings()