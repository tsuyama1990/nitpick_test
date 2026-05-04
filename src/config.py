from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration loaded securely using pydantic-settings."""

    # GitHub Personal Access Token for authenticating API requests
    github_token: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Provide a ready-to-use config instance (lazily or at import, depending on need).
# For pure architecture, we might instantiate it when needed, but a central
# load_config function or global instance is common.
def get_config() -> AppConfig:
    return AppConfig()  # type: ignore[call-arg]
