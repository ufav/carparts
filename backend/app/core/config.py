import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = Field(default="redparts-api")
    API_V1_STR: str = Field(default="/api/v1")
    DATABASE_URL: str = Field(default="postgresql+psycopg2://postgres:postgres@localhost:5432/redparts_shop")
    DEBUG: bool = Field(default=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 