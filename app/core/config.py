from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL_NAME: str = "gemini-1.5-pro-latest"

    class Config:
        env_file = ".env"

settings = Settings()
