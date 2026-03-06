import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "NYtXc,k$5HZDx}DP<f$JWsjeo3LPn)X>")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # API Keys - Groq preferred (free), OpenAI fallback
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Groq Model - set via GROQ_MODEL env var
    # Use llama-3.1-8b-instant as default (newer supported model)
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

settings = Settings()
