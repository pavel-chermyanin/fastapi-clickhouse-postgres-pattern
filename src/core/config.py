import os

from pydantic_settings import BaseSettings, SettingsConfigDict


def get_env_file():
    """
    Определяет какой .env файл использовать на основе переменной окружения APP_ENV.
    Если APP_ENV не задан, по умолчанию используется .env.development.
    """
    app_env = os.getenv("APP_ENV", "development")

    # Пытаемся найти файл .env.<app_env>
    env_file = f".env.{app_env}"

    # Если файл не существует, откатываемся на .env
    if not os.path.exists(env_file):
        if os.path.exists(".env"):
            return ".env"
        return ".env.development"

    return env_file


class Settings(BaseSettings):
    """
    Класс конфигурации приложения, использующий pydantic-settings.
    Загружает переменные окружения из выбранного .env файла.
    """

    model_config = SettingsConfigDict(
        env_file=get_env_file(), env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # Конфигурация приложения
    PROJECT_NAME: str = "FastAPI Universal Pattern"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # База данных (PostgreSQL)
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"

    # ClickHouse
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = ""
    CLICKHOUSE_DATABASE: str = "default"

    # Безопасность
    SECRET_KEY: str = "yoursecretkeyhere"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 дней

    # Административная панель
    ADMIN_USER: str = "admin"
    ADMIN_PASSWORD: str = "admin"


# Экземпляр настроек для использования во всем приложении
settings = Settings()
