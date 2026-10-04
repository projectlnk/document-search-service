from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    ELASTIC_HOST: str
    ELASTIC_PORT: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()