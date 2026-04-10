from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    EMAIL: str
    PASSWORD: str

    class Config:
        env_file = ".env"


settings = Settings()
