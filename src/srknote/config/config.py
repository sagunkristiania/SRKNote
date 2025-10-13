from typing import Optional
from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    JWT_SECRET: SecretStr
    JWT_ALG: str
    ENC_KEY:str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    class Config:
        env_file = ".env"


settings = Settings()


