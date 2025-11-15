from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GOOGLE_CLOUD_PROJECT: str
    GCS_BUCKET_NAME: str

    model_config = {"env_file": ".env"}

settings = Settings()
