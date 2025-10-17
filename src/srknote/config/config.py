"""
config.py
-----------
Loads and manages application configuration values from environment variables.

This module uses Pydantic's `BaseSettings` to securely and easily
handle configuration for database connection, JWT authentication,
and encryption settings. Environment variables are read from the `.env` file.
"""

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration settings.

    Attributes:
        JWT_SECRET (SecretStr): Secret key used to sign JWT tokens.
        JWT_ALG (str): Algorithm used for JWT encoding (e.g., HS256).
        ENC_KEY (str): Encryption key used for note content encryption/decryption.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): JWT token expiry time in minutes.
        DB_USER (str): Database username.
        DB_PASSWORD (SecretStr): Database password (stored securely).
        DB_HOST (str): Hostname or IP address of the database server.
        DB_PORT (int): Port number of the database server.
        DB_NAME (str): Name of the application database.
    """
    JWT_SECRET: SecretStr
    JWT_ALG: str
    ENC_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    class Config:
        """Configuration for reading environment variables from `.env` file."""
        env_file = ".env"


# Instantiate the settings class to load environment variables immediately.
settings = Settings()
