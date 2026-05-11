import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    github_token: str
    github_api_base_url: str = "https://api.github.com"
    request_timeout: float = 10.0

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="forbid",
    )

os.environ["GITHUB_TOKEN"] = "test"
os.environ["RANDOM_VAR"] = "hello"

try:
    s = Settings()
    print("Success")
except Exception as e:
    print(e)
