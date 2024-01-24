from pydantic_settings import BaseSettings, SettingsConfigDict
from os import getenv


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    JWT_SECRET_KEY: str
    Sender: str
    Password: str
    DataBase_Path: str


settings = Settings()

