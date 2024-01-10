from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    Sender: str
    Password: str


settings = Settings()
