import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    MOCK_BANK_URL: str = "http://localhost:8001"
    AWS_REGION: str = "us-east-1"
    SQS_QUEUE_URL: str = "http://localhost:4566/000000000000/proposals-queue"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()