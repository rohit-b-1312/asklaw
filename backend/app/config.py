import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
    JWT_ALGO = "HS256"

settings = Settings()
