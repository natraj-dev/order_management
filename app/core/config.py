import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")

    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")

    # STRIPE KEYS (IMPORTANT)
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")


settings = Settings()
