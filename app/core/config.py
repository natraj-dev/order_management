from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    EMAIL: str
    EMAIL_PASSWORD: str
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

    class Config:
        env_file = ".env"


settings = Settings()
