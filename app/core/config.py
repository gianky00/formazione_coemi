from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv
import os
from pathlib import Path

# Helper to determine user data directory
def get_user_data_dir() -> Path:
    if os.name == 'nt':
        app_data = os.getenv('LOCALAPPDATA')
        if not app_data:
             app_data = os.path.expanduser("~\\AppData\\Local")
        base_dir = Path(app_data) / "Intelleo"
    else:
        # Fallback for Linux dev/test
        base_dir = Path.home() / ".local" / "share" / "Intelleo"

    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

# Load environment variables from .env file in CWD for development if it exists.
# Pydantic will handle loading the one from the user data directory.
load_dotenv()

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    GOOGLE_CLOUD_PROJECT: str = ""
    GCS_BUCKET_NAME: str = ""

    # SMTP Settings for email notifications
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "user@example.com"
    SMTP_PASSWORD: str = "password"
    EMAIL_RECIPIENTS_TO: str = "gianky.allegretti@gmail.com"
    EMAIL_RECIPIENTS_CC: str = ""

    # Alert thresholds
    ALERT_THRESHOLD_DAYS: int = 60
    ALERT_THRESHOLD_DAYS_VISITE: int = 30

    # Security
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days (60 * 24 * 30)

    # First Run Admin Credentials (Secure Default)
    FIRST_RUN_ADMIN_USERNAME: str = "admin"
    FIRST_RUN_ADMIN_PASSWORD: str = "allegretti@coemi"

    # License Auto-Update Settings
    LICENSE_GITHUB_TOKEN: str = ""
    LICENSE_REPO_OWNER: str = ""
    LICENSE_REPO_NAME: str = ""

    model_config = ConfigDict(
        env_file=get_user_data_dir() / ".env",
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()
