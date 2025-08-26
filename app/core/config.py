from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: SecretStr

    S3_ENDPOINT: str | None = None
    S3_REGION: str = "us-east-1"
    S3_ACCESS_KEY: SecretStr
    S3_SECRET_KEY: SecretStr
    S3_BUCKET: str = "finn-voice"


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
