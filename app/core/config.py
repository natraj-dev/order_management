from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")


settings = Settings()
