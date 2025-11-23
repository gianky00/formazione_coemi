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

# Load environment variables from .env file
# We now prioritize the user data directory .env, but load_dotenv() still checks cwd for dev
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

    # Alert thresholds
    ALERT_THRESHOLD_DAYS: int = int(os.getenv("ALERT_THRESHOLD_DAYS", 60))
    ALERT_THRESHOLD_DAYS_VISITE: int = int(os.getenv("ALERT_THRESHOLD_DAYS_VISITE", 30))

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days (60 * 24 * 30)

    # First Run Admin Credentials (Secure Default)
    FIRST_RUN_ADMIN_USERNAME: str = "admin"
    FIRST_RUN_ADMIN_PASSWORD: str = "allegretti@coemi"

    model_config = ConfigDict(
        env_file=get_user_data_dir() / ".env",
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()
