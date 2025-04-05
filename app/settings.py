import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path("./app") / ".env"
if not load_dotenv(dotenv_path=env_path):
    print(f">>> ERROR loading .env file at {env_path}")


class Settings:
    PROJECT_NAME: str = "WG App Login Test"
    PROJECT_VERSION: str = "0.00000001"

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    PASSWORD_SALT: str = os.getenv("PASSWORD_SALT")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # in mins


settings = Settings()
